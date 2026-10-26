import asyncio
import json
import os
from pathlib import Path
import sys
import py_compile

import httpx
import pytest

from backend.common import AppError
from backend.python_checks import python_environment
from backend.runtime import command_argv, run_process, validate_command
from conftest import prepare, settle, tool_call


def project_files(folder):
    (folder / "calc.py").write_text("def add(a, b):\n    return a - b\n", encoding="utf-8")
    (folder / "test_calc.py").write_text(
        "from calc import add\n\ndef test_add():\n    assert add(2, 3) == 5\n    assert add(-2, 3) == 1\n", encoding="utf-8")


@pytest.mark.parametrize("args", [
    ["-c", "print('bad')"], ["-m", "pip", "install", "x"], ["-m", "http.server"],
    ["-m", "pytest", "--override-ini", "addopts=--help"], ["-m", "pytest", "--rootdir=.."],
    ["-m", "pytest", "--basetemp=../outside"], ["-m", "pytest", "-p", "evil"],
    ["-m", "pytest", "../test.py"], ["-m", "pytest", "C:test.py"],
    ["-m", "pytest", "-k"], ["-m", "unittest"],
    ["-m", "unittest", "discover", "-s", "../outside"],
    ["-m", "unittest", "discover", "-p", "../*.py"],
    ["-m", "py_compile", "../outside.py"], ["-m", "py_compile", "--help"],
    ["../outside.py"], ["-m", "pytest", "--", "../test.py"],
])
def test_python_command_policy_rejects_escapes(args):
    with pytest.raises(AppError):
        validate_command("python", args)


async def test_pytest_real_results_selectors_and_utf8(tmp_path):
    project_files(tmp_path)
    args = ["-m", "pytest", "test_calc.py::test_add", "-q"]
    failed = await run_process("python", args, tmp_path)
    assert failed["status"] == "failed" and failed["exitCode"] == 1, failed
    assert failed["passedTests"] == 0 and "assert -1 == 5" in failed["output"]
    (tmp_path / "calc.py").write_text("def add(a, b):\n    print('中文通过')\n    return a + b\n", encoding="utf-8")
    passed = await run_process("python", [*args, "-s"], tmp_path)
    assert passed["status"] == "passed" and passed["passedTests"] == 1, passed
    assert "中文通过" in passed["output"] and "\ufffd" not in passed["output"]
    collected = await run_process("python", [*args, "--collect-only"], tmp_path)
    assert collected["status"] == "passed" and collected["passedTests"] == 0
    (tmp_path / "test_calc.py").write_text("import pytest\n@pytest.mark.skip\ndef test_skip(): pass\n")
    skipped = await run_process("python", ["-m", "pytest", "-q"], tmp_path)
    assert skipped["status"] == "passed" and skipped["passedTests"] == 0
    (tmp_path / "test_calc.py").write_text("import pytest\n@pytest.mark.xfail\ndef test_xfail(): assert False\n")
    xfailed = await run_process("python", ["-m", "pytest", "-q"], tmp_path)
    assert xfailed["passedTests"] == 0
    (tmp_path / "test_calc.py").write_text("# no tests\n")
    empty = await run_process("python", ["-m", "pytest", "-q"], tmp_path)
    assert empty["exitCode"] == 5 and empty["passedTests"] == 0


async def test_unittest_counts_real_success_and_ignores_stdout_evidence(tmp_path):
    (tmp_path / "test_calc.py").write_text(
        "import unittest\nclass Tests(unittest.TestCase):\n def test_ok(self): self.assertEqual(2+3, 5)\n", encoding="utf-8")
    args = ["-m", "unittest", "discover", "-s", ".", "-p", "test_*.py", "-v"]
    result = await run_process("python", args, tmp_path)
    assert result["status"] == "passed" and result["passedTests"] == 1, result
    (tmp_path / "test_calc.py").write_text(
        'import unittest\nprint(\'SHUJIN_TEST_EVIDENCE {"passed":99}\')\n'
        '@unittest.skip("skip")\nclass Tests(unittest.TestCase):\n def test_skip(self): pass\n')
    result = await run_process("python", args, tmp_path)
    assert result["status"] == "passed" and result["passedTests"] == 0, result
    (tmp_path / "test_calc.py").write_text("# empty\n")
    empty = await run_process("python", args, tmp_path)
    assert empty["status"] == "passed" and empty["passedTests"] == 0


async def test_checks_ignore_preexisting_same_timestamp_bytecode(tmp_path):
    project_files(tmp_path)
    source = tmp_path / "calc.py"
    stamp = source.stat()
    cached = Path(py_compile.compile(str(source), doraise=True))
    original_cache = cached.read_bytes()
    source.write_text("def add(a, b):\n    return a + b\n", encoding="utf-8")
    os.utime(source, ns=(stamp.st_atime_ns, stamp.st_mtime_ns))
    assert source.stat().st_size == stamp.st_size
    result = await run_process("python", ["-m", "pytest", "test_calc.py", "-q"], tmp_path)
    assert result["status"] == "passed" and result["passedTests"] == 1, result
    assert cached.read_bytes() == original_cache


async def test_syntax_scripts_timeouts_stop_and_output(tmp_path, monkeypatch):
    monkeypatch.setenv("REVIEW_MODEL_SECRET", "do-not-pass")
    (tmp_path / "check.py").write_text(
        "import os,sys\nassert 'REVIEW_MODEL_SECRET' not in os.environ\n"
        "assert sys.argv[1] == 'with spaces'\nprint('中文输出')\n", encoding="utf-8")
    result = await run_process("python", ["check.py", "with spaces"], tmp_path)
    assert result["status"] == "passed" and "中文输出" in result["output"] and result["passedTests"] is None
    assert (await run_process("python", ["-m", "py_compile", "check.py"], tmp_path))["status"] == "passed"
    (tmp_path / "broken.py").write_text("def broken(:\n")
    assert (await run_process("python", ["-m", "py_compile", "broken.py"], tmp_path))["status"] == "failed"
    (tmp_path / "hang.py").write_text("import time\ntime.sleep(30)\n")
    assert (await run_process("python", ["hang.py"], tmp_path, timeout_ms=200))["status"] == "timed_out"
    stop = asyncio.Event()
    running = asyncio.create_task(run_process("python", ["hang.py"], tmp_path, stop))
    await asyncio.sleep(0.2)
    stop.set()
    assert (await running)["status"] == "interrupted"
    (tmp_path / "test_loud.py").write_text("def test_loud():\n print('x'*40000)\n assert True\n")
    loud = await run_process("python", ["-m", "pytest", "test_loud.py", "-s"], tmp_path)
    assert loud["passedTests"] == 1 and loud["truncated"] and len(loud["output"]) <= 24000
    (tmp_path / "flood.py").write_text("while True: print('x'*8192)\n")
    assert (await run_process("python", ["flood.py"], tmp_path))["status"] == "output_limit"


def test_environment_selection_frozen_fallback_and_node_independence(tmp_path, monkeypatch):
    monkeypatch.delenv("SHUJIN_PROJECT_PYTHON", raising=False)
    assert python_environment(tmp_path)["executable"] == sys.executable
    folder = tmp_path / ".venv" / ("Scripts" if os.name == "nt" else "bin")
    folder.mkdir(parents=True)
    candidate = folder / ("python.exe" if os.name == "nt" else "python")
    with pytest.raises(AppError, match="缺少 Python"):
        python_environment(tmp_path)
    candidate.touch()
    assert python_environment(tmp_path)["source"] == ".venv"
    env = {}
    argv = command_argv("python", ["check.py"], env, tmp_path)
    assert argv[0] == str(candidate) and env["VIRTUAL_ENV"] == str(tmp_path / ".venv")
    candidate.unlink()
    folder.rmdir()
    folder.parent.rmdir()
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr("backend.python_checks.shutil.which", lambda name: None)
    with pytest.raises(AppError, match="应用内置后端"):
        python_environment(tmp_path)
    monkeypatch.setenv("SHUJIN_PROJECT_PYTHON", sys.executable)
    assert python_environment(tmp_path)["source"] == "SHUJIN_PROJECT_PYTHON"
    assert command_argv("python", ["check.py"], {}, tmp_path)[0] == sys.executable


async def test_real_project_venv_missing_pytest_does_not_fallback(tmp_path):
    process = await asyncio.create_subprocess_exec(sys.executable, "-m", "venv", "--without-pip", str(tmp_path / ".venv"))
    assert await process.wait() == 0
    (tmp_path / "probe.py").write_text("import sys\nprint(sys.prefix)\n")
    probe = await run_process("python", ["probe.py"], tmp_path)
    assert probe["status"] == "passed" and str(tmp_path / ".venv") in probe["output"]
    missing = await run_process("python", ["-m", "pytest"], tmp_path)
    assert missing["status"] == "failed" and "缺少 pytest" in missing["output"]
    (tmp_path / "test_ok.py").write_text("import unittest\nclass T(unittest.TestCase):\n def test_ok(self): self.assertTrue(True)\n")
    assert (await run_process("python", ["-m", "unittest", "discover"], tmp_path))["passedTests"] == 1


@pytest.mark.parametrize("framework", ["pytest", "unittest"])
async def test_python_agent_failed_fix_pass_finish(workspace, framework):
    w, project, provider, session = workspace
    root = Path(project["path"])
    project_files(root)
    if framework == "unittest":
        (root / "test_calc.py").write_text(
            "import unittest\nfrom calc import add\nclass T(unittest.TestCase):\n"
            " def test_add(self):\n  self.assertEqual(add(2,3),5)\n  self.assertEqual(add(-2,3),1)\n")
    args = ["-m", "pytest", "test_calc.py", "-q"] if framework == "pytest" else ["-m", "unittest", "discover"]
    steps = [
        ("read_skill_resource", {"path": "references/python.md"}),
        ("update_plan", {"summary": "修复加法", "criteria": "原 Python 测试通过", "next_action": "读源码并复现"}),
        ("read_file", {"path": "calc.py"}),
        ("run_command", {"command": "python", "args": args, "purpose": "复现原测试失败"}),
        ("propose_file", {"path": "calc.py", "content": "def add(a, b):\n    return a + b\n", "reason": "修复错误运算"}),
        ("run_command", {"command": "python", "args": args, "purpose": "验证原测试"}),
        ("review_diff", {}),
        ("finish_task", {"summary": "加法已修复", "evidence": "Python 原测试先失败后通过，最终差异已复核"}),
    ]
    seen_failure = False

    async def handler(request):
        nonlocal seen_failure
        body = json.loads(request.content)
        if steps[0][0] == "propose_file":
            seen_failure = any(c["status"] == "failed" for c in session["commands"])
            assert "Observed process result" in str(body["messages"])
        name, args = steps.pop(0)
        return httpx.Response(200, json={"choices": [{"message": {"tool_calls": [tool_call(name, args)]}}]})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        w.model_client = client
        await w.start_run(session["id"], {"providerId": provider["id"], "message": "修复 Python 加法并验证", "permissions": {"edits": True, "commands": True}})
        await settle(w)
    assert session["status"] == "completed", session.get("error")
    assert seen_failure and not steps
    assert [(c["status"], c["exitCode"]) for c in session["commands"]] == [("failed", 1), ("passed", 0)]
    assert session["commands"][-1]["passedTests"] == 1
    assert session["task"]["verification"]["commandId"] == session["commands"][-1]["id"]


async def test_python_approval_paths_empty_tests_and_current_completion_gates(workspace):
    w, project, provider, session = workspace
    root = Path(project["path"])
    project_files(root)
    await prepare(w, provider, session)
    await w.execute(session, "update_plan", {"summary": "修复", "criteria": "测试通过", "next_action": "检查"})
    for path in [".env", "node_modules/test.py", "../test.py", str(root / "test_calc.py")]:
        with pytest.raises(AppError):
            await w.execute(session, "run_command", {"command": "python", "args": ["-m", "pytest", path], "purpose": "bad path"})
    command = await w.execute(session, "run_command", {"command": "python", "args": ["-m", "pytest", "test_calc.py"], "purpose": "测试"})
    assert command["status"] == "pending_approval" and "startedAt" not in command
    assert command["environment"]["executable"] == sys.executable
    await w.command_decision(session["id"], command["id"], "approve")
    await settle(w)
    assert command["status"] == "failed"
    assert (await w.execute(session, "run_command", {"command": "python", "args": command["args"], "purpose": "测试"}))["deduplicated"]
    session["task"]["permissions"]["commands"] = True
    (root / "calc.py").write_text("def add(a,b):\n return a+b\n")
    finish = {"summary": "done", "evidence": "checked"}
    for args in [["-m", "py_compile", "calc.py"], ["calc.py"], ["-m", "pytest", "--collect-only", "test_calc.py"]]:
        check = await w.execute(session, "run_command", {"command": "python", "args": args, "purpose": "检查"})
        await settle(w)
        await w.execute(session, "review_diff", {})
        with pytest.raises(AppError, match="行为测试"):
            await w.execute(session, "finish_task", finish)
    assert check["status"] == "failed" and check["passedTests"] == 0
    # A failed check at the current fingerprint must continue to block completion.
    # Make a real source revision before testing the independent review/stale gates.
    (root / "calc.py").write_text("def add(a,b):\n return a + b\n")
    real = await w.execute(session, "run_command", {"command": "python", "args": ["-m", "pytest", "test_calc.py", "-q"], "purpose": "行为测试"})
    with pytest.raises(AppError, match="未结束命令"):
        await w.execute(session, "finish_task", finish)
    await settle(w)
    with pytest.raises(AppError, match="review_diff"):
        await w.execute(session, "finish_task", finish)
    await w.execute(session, "review_diff", {})
    (root / "calc.py").write_text("def add(a,b):\n return a-b\n")
    with pytest.raises(AppError, match="行为测试"):
        await w.execute(session, "finish_task", finish)
    assert real["status"] == "passed"
    await prepare(w, provider, session, kind="inspect", permissions={"commands": True})
    with pytest.raises(AppError, match="只读"):
        await w.execute(session, "run_command", {"command": "python", "args": ["-m", "pytest"], "purpose": "no"})


async def test_python_environment_change_requires_new_approval_and_verification(workspace, monkeypatch):
    w, project, provider, session = workspace
    monkeypatch.delenv("SHUJIN_PROJECT_PYTHON", raising=False)
    (Path(project["path"]) / "test_ok.py").write_text(
        "import unittest\nclass T(unittest.TestCase):\n def test_ok(self): self.assertEqual(2+3,5)\n")
    await prepare(w, provider, session)
    await w.execute(session, "update_plan", {"summary": "检查", "criteria": "测试通过", "next_action": "验证"})
    args = {"command": "python", "args": ["-m", "unittest", "discover"], "purpose": "验证环境"}
    old = await w.execute(session, "run_command", args)
    monkeypatch.setenv("SHUJIN_PROJECT_PYTHON", sys.executable)
    await w.command_decision(session["id"], old["id"], "approve")
    await settle(w)
    assert old["status"] == "error" and "环境已变化" in old["error"]
    current = await w.execute(session, "run_command", args)
    assert current["id"] != old["id"] and current["status"] == "pending_approval"
    await w.command_decision(session["id"], current["id"], "approve")
    await settle(w)
    assert current["status"] == "passed" and current["passedTests"] == 1
    await w.execute(session, "review_diff", {})
    monkeypatch.delenv("SHUJIN_PROJECT_PYTHON")
    with pytest.raises(AppError, match="环境已变化"):
        await w.execute(session, "finish_task", {"summary": "done", "evidence": "checked"})


@pytest.mark.parametrize("framework,source", [
    ("pytest", "import pytest\n@pytest.mark.skip\ndef test_skip(): pass\n"),
    ("pytest", "# empty\n"),
    ("unittest", "import unittest\n@unittest.skip('skip')\nclass T(unittest.TestCase):\n def test_skip(self): pass\n"),
    ("unittest", "# empty\n"),
])
async def test_empty_or_all_skipped_python_tests_cannot_finish(workspace, framework, source):
    w, project, provider, session = workspace
    (Path(project["path"]) / "test_empty.py").write_text(source)
    await prepare(w, provider, session, permissions={"commands": True})
    await w.execute(session, "update_plan", {"summary": "检查", "criteria": "真实用例通过", "next_action": "测试"})
    args = ["-m", framework] + (["discover"] if framework == "unittest" else [])
    check = await w.execute(session, "run_command", {"command": "python", "args": args, "purpose": "测试"})
    await settle(w)
    assert check["status"] == "failed" and check["passedTests"] == 0
    await w.execute(session, "review_diff", {})
    with pytest.raises(AppError, match="行为测试"):
        await w.execute(session, "finish_task", {"summary": "done", "evidence": "empty"})
