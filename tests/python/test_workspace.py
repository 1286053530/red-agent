import asyncio
import json
from pathlib import Path

import httpx
import pytest

from backend.common import AppError
from backend.workspace import Workspace
from conftest import prepare, settle, tool_call

PLAN = {"summary": "修复加法", "criteria": "原行为测试全部通过", "next_action": "读取源码"}


async def test_real_agent_loop_failed_fix_then_correction(workspace):
    w, project, provider, s = workspace
    steps = [("read_skill_resource", {"path": "references/javascript-node.md"}), ("update_plan", PLAN), ("read_file", {"path": "app.mjs"}),
             ("propose_file", {"path": "app.mjs", "content": "export const add=(a,b)=>a*b;\n", "reason": "first attempt"}),
             ("run_command", {"command": "node", "args": ["--test", "app.test.mjs"], "purpose": "behavior"}),
             ("update_plan", {**PLAN, "failure": "乘法错误，需要相加"}), ("read_file", {"path": "app.mjs"}),
             ("propose_file", {"path": "app.mjs", "content": "export const add=(a,b)=>a+b;\n", "reason": "correct failure"}),
             ("run_command", {"command": "node", "args": ["--test", "app.test.mjs"], "purpose": "regression"}),
             ("review_diff", {}), ("finish_task", {"summary": "已修复加法", "evidence": "真实测试通过，最终差异已复核"})]
    observed = False
    expected_rounds = len(steps)
    async def handler(request):
        nonlocal observed
        body = json.loads(request.content)
        if len(steps) == 6:
            observed = '"status":"failed"' in json.dumps(body, ensure_ascii=False).replace('\\"', '"')
        name, args = steps.pop(0)
        return httpx.Response(200, json={"choices": [{"message": {"tool_calls": [tool_call(name, args)]}}], "usage": {"prompt_tokens": 10, "completion_tokens": 5}})
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        w.model_client = client
        await w.start_run(s["id"], {"providerId": provider["id"], "message": "修复 add", "permissions": {"edits": True, "commands": True}})
        await settle(w)
    assert s["status"] == "completed", s["error"]
    assert observed and not steps
    assert [(c["status"], c["exitCode"]) for c in s["commands"]] == [("failed", 1), ("passed", 0)]
    assert s["task"]["metrics"]["inputTokens"] == expected_rounds * 10
    assert s["task"]["skill"]["loadedResources"] == ["references/javascript-node.md"]
    assert "a+b" in (Path(project["path"]) / "app.mjs").read_text()
    events = [json.loads(line) for line in (w.data_dir / "runs" / (s["task"]["id"] + ".jsonl")).read_text(encoding="utf-8").splitlines()]
    assert events[-1]["type"] == "task_completed"


async def test_completion_gates_current_behavior_and_review(workspace):
    w, project, provider, s = workspace
    await prepare(w, provider, s, permissions={"commands": True})
    await w.execute(s, "update_plan", PLAN)
    finish = {"summary": "done", "evidence": "verified"}
    with pytest.raises(AppError, match="行为测试"):
        await w.execute(s, "finish_task", finish)
    await w.execute(s, "run_command", {"command": "node", "args": ["--check", "app.mjs"], "purpose": "syntax"})
    await settle(w)
    await w.execute(s, "review_diff", {})
    with pytest.raises(AppError, match="行为测试"):
        await w.execute(s, "finish_task", finish)
    (Path(project["path"]) / "app.mjs").write_text("export const add=(a,b)=>a+b;\n")
    await w.execute(s, "run_command", {"command": "node", "args": ["--test", "app.test.mjs"], "purpose": "behavior"})
    with pytest.raises(AppError, match="未结束命令"):
        await w.execute(s, "finish_task", finish)
    await settle(w)
    with pytest.raises(AppError, match="review_diff"):
        await w.execute(s, "finish_task", finish)
    await w.execute(s, "review_diff", {})
    (Path(project["path"]) / "app.mjs").write_text("export const add=(a,b)=>a-b;\n")
    with pytest.raises(AppError, match="行为测试"):
        await w.execute(s, "finish_task", finish)


async def test_approval_retry_and_project_reservation(workspace):
    w, project, provider, s = workspace
    await prepare(w, provider, s)
    args = {"command": "node", "args": ["--test", "app.test.mjs"], "purpose": "behavior"}
    command = await w.execute(s, "run_command", args)
    assert command["status"] == "pending_approval" and "startedAt" not in command
    other = w.create_session({"projectId": project["id"]})
    with pytest.raises(AppError, match="待审核"):
        await w.start_run(other["id"], {"providerId": provider["id"], "message": "other"})
    await w.command_decision(s["id"], command["id"], "approve")
    await settle(w)
    assert command["status"] == "failed"
    assert (await w.execute(s, "run_command", args))["deduplicated"]
    s["task"]["permissions"]["commands"] = True
    retry = await w.execute(s, "run_command", {**args, "retry_id": command["id"]})
    await settle(w)
    assert retry["id"] != command["id"]
    s["task"]["permissions"]["commands"] = False
    pending = await w.execute(s, "run_command", {"command": "node", "args": ["--check", "app.mjs"], "purpose": "syntax"})
    await w.command_decision(s["id"], pending["id"], "deny")
    await settle(w)
    assert pending["status"] == "denied"


async def test_empty_tests_and_readonly_permissions(workspace):
    w, project, provider, s = workspace
    await prepare(w, provider, s, kind="inspect", permissions={"edits": True, "commands": True})
    await w.execute(s, "update_plan", PLAN)
    await w.execute(s, "read_file", {"path": "app.mjs"})
    for name, args in [("propose_file", {"path": "app.mjs", "content": "no"}), ("run_command", {"command": "node", "args": ["--test"], "purpose": "no"})]:
        with pytest.raises(AppError, match="只读"):
            await w.execute(s, name, args)
    await w.execute(s, "finish_task", {"summary": "使用减法", "evidence": "已读取源码，未执行代码"})
    assert s["status"] == "completed" and not s["changes"] and not s["commands"]
    await prepare(w, provider, s, permissions={"commands": True})
    (Path(project["path"]) / "empty.test.mjs").write_text("// no tests\n")
    command = await w.execute(s, "run_command", {"command": "node", "args": ["--test", "empty.test.mjs"], "purpose": "empty"})
    await settle(w)
    assert command["status"] == "failed" and command["passedTests"] == 0


async def test_character_paging_preserves_large_read_in_model_context(workspace):
    w, project, provider, s = workspace
    text = "// " + "a" * 45000 + "TAIL_MARKER\n"
    (Path(project["path"]) / "large.mjs").write_bytes(text.encode("utf-8"))
    await prepare(w, provider, s, permissions={"edits": True})
    first = await w.execute(s, "read_file", {"path": "large.mjs"})
    assert len(first["content"]) == 12000 and first["hasMore"]
    with pytest.raises(AppError, match="读完"):
        await w.execute(s, "propose_file", {"path": "large.mjs", "content": "// replacement"})
    from backend.runtime import bounded_history
    history = [{"role": "assistant", "tool_calls": [tool_call("read_file")]}, {"role": "tool", "tool_call_id": "read", "content": json.dumps(first)}]
    assert bounded_history(history) == history
    combined = first["content"]
    while first["hasMore"]:
        first = await w.execute(s, "read_file", {"path": "large.mjs", "offset": first["next_offset"]})
        combined += first["content"]
    assert combined == text
    change = await w.execute(s, "propose_file", {"path": "large.mjs", "content": text + "// tail change\n", "reason": "tail"})
    assert change["status"] == "applied"
    review = await w.execute(s, "review_diff", {})
    assert review["incomplete"] and s["task"].get("review") is None  # A 45KB minified diff cannot be silently reviewed.


async def test_diff_includes_tail_changes_after_first_6000_characters(workspace):
    w, project, provider, s = workspace
    text = "// padding\n" * 900 + "export const answer=1;\n"
    (Path(project["path"]) / "tail.mjs").write_bytes(text.encode("utf-8"))
    await prepare(w, provider, s, permissions={"edits": True})
    await w.execute(s, "read_file", {"path": "tail.mjs", "offset": 0})
    await w.execute(s, "propose_file", {"path": "tail.mjs", "content": text.replace("answer=1", "answer=2"), "reason": "tail"})
    review = await w.execute(s, "review_diff", {})
    assert not review["incomplete"] and "-export const answer=1" in review["changes"][0]["diff"] and "+export const answer=2" in review["changes"][0]["diff"]


async def test_conflicts_restoration_and_restart(workspace):
    w, project, provider, s = workspace
    await prepare(w, provider, s)
    await w.execute(s, "read_file", {"path": "app.mjs"})
    proposal = await w.execute(s, "propose_file", {"path": "app.mjs", "content": "export const add=(a,b)=>a+b;\n", "reason": "fix"})
    source = Path(project["path"]) / "app.mjs"
    original = source.read_text()
    source.write_text("external\n")
    with pytest.raises(AppError, match="其他地方修改"):
        await w.apply_change(s["id"], proposal["changeId"], "apply")
    source.write_text(original)
    await w.apply_change(s["id"], proposal["changeId"], "apply")
    await settle(w)
    await w.apply_change(s["id"], proposal["changeId"], "revert")
    assert source.read_text() == original
    await w.execute(s, "update_plan", {**PLAN, "failure": "用户停止"})
    s["status"] = "running"
    s["commands"].append({"id": "unknown", "status": "running", "exitCode": None})
    w.save()
    restored = Workspace(w.data_dir)
    result = restored.session(s["id"])
    assert result["status"] == "stopped" and result["commands"][-1]["status"] == "interrupted"
    assert result["task"]["checkpoint"]["failure"] == "用户停止"
    await restored.shutdown()


async def test_node_state_and_encryption_compatibility(workspace):
    w, project, provider, s = workspace
    assert "fixture-secret" not in json.dumps(w.state())
    assert "fixture-secret" not in (w.data_dir / "workspace.json").read_text(encoding="utf-8")
    # The JS predecessor uses base64(iv[12] + ciphertext + tag[16]), same AES-GCM format.
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    import base64
    import os
    iv = os.urandom(12)
    cipher = Cipher(algorithms.AES(w.key), modes.GCM(iv)).encryptor()
    ciphertext = cipher.update(b"legacy-node-secret") + cipher.finalize()
    assert w.decrypt(base64.b64encode(iv + ciphertext + cipher.tag)) == "legacy-node-secret"
    restored = Workspace(w.data_dir)
    assert restored.decrypt(restored.data["providers"][0]["secret"]) == "fixture-secret"
    for name in [".env", "secret.key", ".GIT/config", "../outside", "nested/../app.mjs", "node_modules/dependency.js", ".env "]:
        with pytest.raises(AppError):
            w.read_source(project, name)
    await restored.shutdown()


async def test_stop_interrupts_model_request(workspace):
    w, _, provider, s = workspace
    requested = asyncio.Event()
    async def handler(request):
        requested.set()
        await asyncio.Event().wait()
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        w.model_client = client
        await w.start_run(s["id"], {"providerId": provider["id"], "message": "stop"})
        await requested.wait()
        await w.stop(s["id"])
    assert s["status"] == "stopped" and not w.runs
