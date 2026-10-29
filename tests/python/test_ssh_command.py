import asyncio
import json
import sys
import time

import pytest

from backend.common import AppError
from backend.model import TOOLS
from backend.runtime import child_environment, command_argv, run_process, validate_command
from backend.ssh_runtime import run_password_ssh
from backend.workspace import Workspace, protected_ssh_answer
from conftest import prepare, settle, tool_call


def test_ssh_command_accepts_only_target_port_and_remote_command(monkeypatch):
    for args in (["root@example.org", "uname -a"], ["-p", "2222", "root@192.0.2.1", "whoami"]):
        validate_command("ssh", args)
    for args in (["-o", "ProxyCommand=bad", "root@example.org", "id"], ["-p", "0", "root@example.org", "id"],
                 ["-p", "abc", "root@example.org", "id"], ["-p", "22", "-bad", "id"],
                 ["root@host", ""], ["root@host", "id\nnext"], [42, "id"], ["root@host", 42]):
        with pytest.raises(AppError):
            validate_command("ssh", args)
    monkeypatch.setenv("SSH_AUTH_SOCK", "test-agent-socket")
    monkeypatch.setenv("REVIEW_MODEL_SECRET", "must-not-inherit")
    env = child_environment()
    argv = command_argv("ssh", ["-p", "2222", "root@example.org", "uname -a"], env)
    assert argv[-4:] == ["-p", "2222", "root@example.org", "uname -a"]
    assert "BatchMode=yes" in argv and "StrictHostKeyChecking=accept-new" in argv
    assert env["SSH_AUTH_SOCK"] == "test-agent-socket" and "REVIEW_MODEL_SECRET" not in env
    assert "SSH_AUTH_SOCK" not in child_environment()
    schema = next(item["function"] for item in TOOLS if item["function"]["name"] == "run_command")
    assert "ssh" in schema["parameters"]["properties"]["command"]["enum"]


async def test_native_ssh_uses_supervised_process_without_real_network(tmp_path, monkeypatch):
    import backend.runtime as runtime
    monkeypatch.setattr(runtime, "command_argv", lambda command, args, env, cwd=None, report=None:
                        [sys.executable, "-c", "print('remote-ok')"])
    result = await run_process("ssh", ["root@example.org", "uname"], tmp_path)
    assert result["status"] == "passed" and "remote-ok" in result["output"]
    monkeypatch.setattr(runtime, "command_argv", lambda command, args, env, cwd=None, report=None:
                        [sys.executable, "-c", "import time; time.sleep(10)"])
    assert (await run_process("ssh", ["root@example.org", "sleep"], tmp_path, timeout_ms=100))["status"] == "timed_out"
    stop = asyncio.Event()
    running = asyncio.create_task(run_process("ssh", ["root@example.org", "sleep"], tmp_path, stop))
    await asyncio.sleep(0.1)
    stop.set()
    assert (await running)["status"] == "interrupted"


def test_one_shot_password_ssh_redacts_output_and_closes(monkeypatch, tmp_path):
    import backend.ssh_runtime as ssh_runtime
    seen = {}
    class Channel:
        def __init__(self):
            self.pending = True
        def exec_command(self, value):
            seen["remote"] = value
        def recv_ready(self):
            return self.pending
        def recv(self, count):
            self.pending = False
            return b"connected secret-value"
        def recv_stderr_ready(self):
            return False
        def recv_stderr(self, count):
            return b""
        def exit_status_ready(self):
            return True
        def recv_exit_status(self):
            return 0
        def close(self):
            seen["channel_closed"] = True
    class Client:
        def load_host_keys(self, path):
            seen["known_hosts"] = path
        def set_missing_host_key_policy(self, policy):
            seen["policy"] = policy
        def connect(self, host, **kwargs):
            seen["host"], seen["connect"] = host, kwargs
        def get_transport(self):
            return self
        def open_session(self, timeout):
            return Channel()
        def close(self):
            seen["client_closed"] = True
    monkeypatch.setattr(ssh_runtime, "known_hosts_path", lambda: tmp_path / "known_hosts")
    monkeypatch.setattr(ssh_runtime.paramiko, "SSHClient", Client)
    result = run_password_ssh(2222, "root@example.org", "uname", "secret-value", None, 1000)
    assert result["status"] == "passed" and result["exitCode"] == 0
    assert result["output"] == "connected [REDACTED]"
    assert seen["host"] == "example.org" and seen["connect"]["password"] == "secret-value"
    assert seen["connect"]["allow_agent"] is False and seen["remote"] == "uname"
    assert seen["channel_closed"] and seen["client_closed"]


def test_model_ssh_password_is_removed_from_saved_tool_calls():
    secret = 'p"ä\\value'
    call = tool_call("run_command", {"command": "ssh", "args": ["root@example.org", "id"], "password": secret, "purpose": "connect"})
    answer = {"content": "connecting " + secret, "tool_calls": [call],
              "_responses_output": [{"type": "function_call", "call_id": call["id"], "arguments": call["function"]["arguments"]}]}
    safe, passwords = protected_ssh_answer(answer)
    assert passwords[call["id"]] == secret
    saved = json.dumps(safe, ensure_ascii=False)
    assert secret not in saved and json.dumps(secret)[1:-1] not in saved
    assert "[REDACTED]" in saved
    assert json.loads(safe["tool_calls"][0]["function"]["arguments"])["password"] == "[REDACTED]"
    assert json.loads(answer["tool_calls"][0]["function"]["arguments"])["password"] == secret


async def test_password_ssh_uses_existing_command_approval_and_remote_completion(workspace, monkeypatch):
    import backend.workspace as workspace_module
    w, _, provider, session = workspace
    await prepare(w, provider, session, permissions={"commands": True})
    await w.execute(session, "update_plan", {"summary": "远程连接", "criteria": "远端返回核验信息", "next_action": "执行 SSH"})
    seen = {}
    async def fake_run(command, args, cwd, stop=None, timeout_ms=60000, on_output=None, ssh_password=None):
        seen.update(command=command, args=args, password=ssh_password)
        return {"status": "passed", "exitCode": 0, "output": "remote-ok", "bytes": 9, "finishedAt": "2026-10-29T00:00:00Z"}
    monkeypatch.setattr(workspace_module, "run_process", fake_run)
    command = await w.execute(session, "run_command", {"command": "ssh", "args": ["root@example.org", "uname"],
                                                        "purpose": "核验服务器", "password": "one-time-secret"})
    assert "_sshSecret" not in command
    assert "_sshSecret" not in w.public_session(session)["commands"][0]
    assert "one-time-secret" not in (w.data_dir / "workspace.json").read_text(encoding="utf-8")
    await settle(w)
    result = await w.execute(session, "command_result", {"id": command["id"]})
    assert result["status"] == "passed" and seen == {"command": "ssh", "args": ["root@example.org", "uname"], "password": "one-time-secret"}
    assert "one-time-secret" not in (w.data_dir / "runs" / (session["task"]["id"] + ".jsonl")).read_text(encoding="utf-8")
    finish = await w.execute(session, "finish_task", {"summary": "连接完成", "evidence": "SSH 返回 remote-ok"})
    assert finish["status"] == "completed" and session["task"]["verification"]["remote"] is True


async def test_password_ssh_stop_and_timeout_do_not_execute_after_signal(tmp_path, monkeypatch):
    import backend.ssh_runtime as ssh_runtime
    seen = []
    def delayed(port, target, command, password, stop, timeout_ms):
        while not stop.is_set():
            time.sleep(0.01)
        seen.append("stopped")
        return {"status": "interrupted", "exitCode": None, "output": "", "bytes": 0}
    monkeypatch.setattr(ssh_runtime, "run_password_ssh", delayed)
    timed = await run_process("ssh", ["root@example.org", "id"], tmp_path, timeout_ms=100, ssh_password="secret")
    assert timed["status"] == "timed_out"
    stop = asyncio.Event()
    running = asyncio.create_task(run_process("ssh", ["root@example.org", "id"], tmp_path, stop, ssh_password="secret"))
    await asyncio.sleep(0.05)
    stop.set()
    assert (await running)["status"] == "interrupted"
    await asyncio.sleep(0.05)
    assert seen == ["stopped", "stopped"]


async def test_password_ssh_waits_for_command_approval_without_exposing_password(workspace, monkeypatch):
    import backend.workspace as workspace_module
    w, _, provider, session = workspace
    await prepare(w, provider, session)
    seen = []
    async def fake_run(*args, **kwargs):
        seen.append(kwargs.get("ssh_password"))
        return {"status": "passed", "exitCode": 0, "output": "ok", "bytes": 2, "finishedAt": "2026-10-29T00:00:00Z"}
    monkeypatch.setattr(workspace_module, "run_process", fake_run)
    command = await w.execute(session, "run_command", {"command": "ssh", "args": ["root@example.org", "id"],
                                                        "purpose": "connect", "password": "pending-secret"})
    assert command["status"] == "pending_approval" and not seen
    assert "pending-secret" not in json.dumps(w.public_session(session), ensure_ascii=False)
    assert "pending-secret" not in (w.data_dir / "workspace.json").read_text(encoding="utf-8")
    internal = session["commands"][0]
    internal["approved"] = True
    w.launch_command(session, internal)
    await settle(w)
    assert seen == ["pending-secret"] and "_sshSecret" not in internal


async def test_ssh_cannot_bypass_readonly_or_local_change_verification(workspace, monkeypatch):
    import backend.workspace as workspace_module
    w, _, provider, session = workspace
    await prepare(w, provider, session, kind="inspect", permissions={"commands": True})
    with pytest.raises(AppError, match="只读"):
        await w.execute(session, "run_command", {"command": "ssh", "args": ["root@example.org", "id"], "purpose": "no"})
    await prepare(w, provider, session, permissions={"edits": True, "commands": True})
    await w.execute(session, "update_plan", {"summary": "远程连接", "criteria": "验证", "next_action": "SSH"})
    async def fake_run(*args, **kwargs):
        return {"status": "passed", "exitCode": 0, "output": "remote-ok", "bytes": 9, "finishedAt": "2026-10-29T00:00:00Z"}
    monkeypatch.setattr(workspace_module, "run_process", fake_run)
    await w.execute(session, "run_command", {"command": "ssh", "args": ["root@example.org", "id"], "purpose": "remote"})
    await settle(w)
    session["changes"].append({"taskId": session["task"]["id"], "status": "applied"})
    with pytest.raises(AppError, match="行为测试"):
        await w.execute(session, "finish_task", {"summary": "done", "evidence": "SSH returned"})


async def test_password_cannot_be_copied_into_logged_command_fields(workspace):
    w, _, provider, session = workspace
    await prepare(w, provider, session, permissions={"commands": True})
    for args, purpose in [(["root@example.org", "echo secret"], "connect"), (["root@example.org", "id"], "use secret")]:
        with pytest.raises(AppError, match="password 字段"):
            await w.execute(session, "run_command", {"command": "ssh", "args": args, "purpose": purpose, "password": "secret"})
    assert not session["commands"]


async def test_remote_completion_requires_nonempty_remote_verification(workspace, monkeypatch):
    import backend.workspace as workspace_module
    w, _, provider, session = workspace
    await prepare(w, provider, session, permissions={"commands": True})
    await w.execute(session, "update_plan", {"summary": "远程核验", "criteria": "返回实际状态", "next_action": "SSH"})
    async def fake_run(*args, **kwargs):
        return {"status": "passed", "exitCode": 0, "output": "", "bytes": 0, "finishedAt": "2026-10-29T00:00:00Z"}
    monkeypatch.setattr(workspace_module, "run_process", fake_run)
    await w.execute(session, "run_command", {"command": "ssh", "args": ["root@example.org", "true"], "purpose": "probe"})
    await settle(w)
    with pytest.raises(AppError, match="远端核验输出"):
        await w.execute(session, "finish_task", {"summary": "done", "evidence": "ran true"})
