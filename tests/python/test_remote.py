import asyncio
import json
from pathlib import Path
import stat
from types import SimpleNamespace

import httpx
import pytest
from playwright.async_api import async_playwright, expect

from backend.common import AppError
from backend import remote as ssh
from conftest import prepare, settle, tool_call


FINGERPRINT = "SHA256:" + "A" * 43


def connection(password="test-password"):
    return {"host": "192.0.2.10", "port": 22, "username": "root", "hostKey": FINGERPRINT, "password": password}


@pytest.mark.parametrize("change", [{"host": "bad/host"}, {"hostKey": "unknown"}, {"port": 0}, {"username": "root;cmd"}, {"password": "bad\x00secret"}])
def test_invalid_remote_settings_rejected(change):
    with pytest.raises(AppError):
        ssh.validate_remote({**connection(), **change})


@pytest.mark.parametrize("path", ["relative", "/tmp/../app", "/tmp//app", "/tmp/./app", "/tmp/app/", "/tmp/\napp"])
def test_remote_upload_requires_clean_absolute_path(path):
    with pytest.raises(AppError):
        ssh.validate_remote_path(path)


def test_host_key_is_checked_before_password(monkeypatch):
    calls = []

    class Key:
        def asbytes(self):
            return b"public-key"

        def get_name(self):
            return "ssh-ed25519"

    class Transport:
        def __init__(self, socket):
            calls.append("connect")

        def start_client(self, timeout):
            calls.append("handshake")

        def get_remote_server_key(self):
            return Key()

        def auth_password(self, username, password, fallback):
            calls.append("auth")
            assert (username, password, fallback) == ("root", "test-password", False)

        def is_authenticated(self):
            return True

        def close(self):
            calls.append("close")

    monkeypatch.setattr(ssh.socket, "create_connection", lambda *args, **kwargs: object())
    monkeypatch.setattr(ssh.paramiko, "Transport", Transport)
    with pytest.raises(AppError, match="发送密码前"):
        ssh._transport("192.0.2.10", 22, FINGERPRINT, "test-password", "root")
    assert calls == ["connect", "handshake", "close"]
    actual = ssh.key_fingerprint(Key())
    transport, fingerprint = ssh._transport("192.0.2.10", 22, actual, "test-password", "root")
    assert fingerprint == actual and calls[-3:] == ["connect", "handshake", "auth"]
    transport.close()


def test_failed_transport_constructor_closes_socket(monkeypatch):
    class Socket:
        closed = False

        def close(self):
            self.closed = True

    socket = Socket()
    monkeypatch.setattr(ssh.socket, "create_connection", lambda *args, **kwargs: socket)

    def fail_transport(_socket):
        raise OSError("simulated transport failure")

    monkeypatch.setattr(ssh.paramiko, "Transport", fail_transport)
    with pytest.raises(AppError, match="SSH 连接失败"):
        ssh._transport("192.0.2.10", 22)
    assert socket.closed


def test_stop_during_handshake_prevents_command_and_upload(tmp_path, monkeypatch):
    stop = asyncio.Event()
    closed = []

    class Transport:
        def open_session(self, **kwargs):
            pytest.fail("Stopped task opened an SSH command channel")

        def close(self):
            closed.append(True)

    def connect(*args):
        stop.set()
        return Transport(), FINGERPRINT

    monkeypatch.setattr(ssh, "_transport", connect)
    monkeypatch.setattr(ssh.paramiko.SFTPClient, "from_transport", lambda _: pytest.fail("Stopped task opened SFTP"))
    command = ssh.run_remote(connection(), "test-password", "echo ok", stop)
    assert command["status"] == "interrupted"
    stop.clear()
    local = tmp_path / "bundle.jar"
    local.write_bytes(b"package")
    upload = ssh.upload_remote(connection(), "test-password", [(local, "")], "/tmp/stage", stop)
    assert upload["status"] == "interrupted"
    assert len(closed) == 2


@pytest.mark.parametrize("interrupt", [False, True])
def test_upload_never_overwrites_temporary_file_and_cleans_own_partial(tmp_path, monkeypatch, interrupt):
    local = tmp_path / "bundle.jar"
    local.write_bytes(b"package")
    stop = asyncio.Event()

    class Transport:
        closed = False

        def close(self):
            self.closed = True

    class RemoteFile:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def write(self, chunk):
            sftp.files["/tmp/stage.shujin-uploading"].extend(chunk)
            stop.set()

        def flush(self):
            pass

    class SFTP:
        def __init__(self):
            self.files = {"/tmp/stage.shujin-uploading": bytearray(b"existing")} if not interrupt else {}
            self.removed = []
            self.closed = False

        def stat(self, path):
            if path == "/tmp":
                return SimpleNamespace(st_mode=stat.S_IFDIR)
            if path in self.files:
                return SimpleNamespace(st_mode=stat.S_IFREG)
            raise FileNotFoundError(path)

        def open(self, path, mode):
            assert mode == "wx"
            if path in self.files:
                raise FileExistsError(path)
            self.files[path] = bytearray()
            return RemoteFile()

        def remove(self, path):
            self.removed.append(path)
            del self.files[path]

        def rename(self, source, target):
            assert target not in self.files
            self.files[target] = self.files.pop(source)

        def close(self):
            self.closed = True

    transport, sftp = Transport(), SFTP()
    monkeypatch.setattr(ssh, "_transport", lambda *args: (transport, FINGERPRINT))
    monkeypatch.setattr(ssh.paramiko.SFTPClient, "from_transport", lambda _: sftp)
    if interrupt:
        result = ssh.upload_remote(connection(), "test-password", [(local, "")], "/tmp/stage", stop)
        assert result["status"] == "interrupted" and result["files"] == 0
        assert "/tmp/stage.shujin-uploading" in sftp.removed
        assert not sftp.files
    else:
        with pytest.raises(AppError, match="SFTP 上传失败"):
            ssh.upload_remote(connection(), "test-password", [(local, "")], "/tmp/stage")
        assert sftp.files["/tmp/stage.shujin-uploading"] == b"existing"
        assert not sftp.removed
    assert transport.closed and sftp.closed


async def test_remote_profile_is_encrypted_scoped_and_not_public(workspace, monkeypatch):
    w, project, provider, session = workspace
    saved = w.save_remote(project["id"], connection())
    assert saved == {"id": saved["id"], "projectId": project["id"], "host": "192.0.2.10", "port": 22,
                     "username": "root", "hostKey": FINGERPRINT}
    assert "test-password" not in json.dumps(w.state())
    assert "test-password" not in (w.data_dir / "workspace.json").read_text(encoding="utf-8")
    await prepare(w, provider, session, kind="change")
    with pytest.raises(AppError, match="未授权"):
        await w.execute(session, "remote_command", {"command": "pwd", "purpose": "inspect"})

    called = []
    monkeypatch.setattr("backend.workspace.run_remote", lambda remote, password, command, stop, timeout:
                        (called.append((remote["host"], password, command)) or
                         {"status": "passed", "exitCode": 0, "output": "/srv/app", "bytes": 8}))
    await w.start_run(session["id"], {"providerId": provider["id"], "message": "部署并核验", "kind": "change", "remote": True})
    await settle(w)
    assert session["task"]["remoteScope"] == saved
    result = await w.execute(session, "remote_command", {"command": "pwd", "purpose": "确认目录"})
    assert result["status"] == "passed" and called == [("192.0.2.10", "test-password", "pwd")]
    await w.execute(session, "update_plan", {"summary": "目标已部署", "criteria": "远程核验成功", "next_action": "交付"})
    with pytest.raises(AppError, match="最终成功"):
        await w.execute(session, "finish_task", {"summary": "已核验", "evidence": "SSH 命令退出码 0"})
    await w.execute(session, "remote_command", {"command": "test -d /srv/app", "purpose": "核验远端部署结果", "verification": True})
    completed = await w.execute(session, "finish_task", {"summary": "已核验", "evidence": "SSH 命令退出码 0"})
    assert completed["status"] == "completed"
    assert "test-password" not in json.dumps(w.public_session(session))
    w.save_remote(project["id"], {**connection("new-password"), "host": "192.0.2.11"})
    with pytest.raises(AppError, match="配置已变化"):
        w.checked_remote(session)


async def test_remote_upload_scopes_local_files_and_records_errors(workspace, monkeypatch):
    w, project, provider, session = workspace
    w.save_remote(project["id"], connection())
    bundle = Path(project["path"]) / "bundle"
    bundle.mkdir()
    (bundle / "app.jar").write_bytes(b"package")
    (bundle / ".env").write_text("SECRET")
    await w.start_run(session["id"], {"providerId": provider["id"], "message": "部署并核验", "kind": "change", "remote": True})
    await settle(w)
    captured = []
    monkeypatch.setattr("backend.workspace.upload_remote", lambda remote, password, sources, target, stop:
                        (captured.append((password, [(p.name, rel) for p, rel in sources], target)) or
                         {"status": "passed", "files": len(sources), "bytes": 7}))
    output = await w.execute(session, "remote_upload", {"local_path": "bundle", "remote_path": "/tmp/new-stage", "purpose": "上传包"})
    assert output["files"] == 1 and captured == [("test-password", [("app.jar", "app.jar")], "/tmp/new-stage")]
    with pytest.raises(AppError, match="路径"):
        await w.execute(session, "remote_upload", {"local_path": "bundle/.env", "remote_path": "/tmp/private", "purpose": "bad"})
    assert session["task"]["remoteActions"][-1]["status"] == "error"
    await w.execute(session, "update_plan", {"summary": "上传中断", "criteria": "远程核验通过", "next_action": "排查"})
    with pytest.raises(AppError, match="远程任务缺少"):
        await w.execute(session, "finish_task", {"summary": "完成", "evidence": "尚未核验"})


async def test_remote_requires_explicit_change_task_grant(workspace):
    w, _, provider, session = workspace
    with pytest.raises(AppError, match="配置"):
        await w.start_run(session["id"], {"providerId": provider["id"], "message": "部署", "kind": "change", "remote": True})
    with pytest.raises(AppError, match="只读"):
        await w.start_run(session["id"], {"providerId": provider["id"], "message": "部署", "kind": "inspect", "remote": True})


async def test_auto_task_with_ssh_stays_executable_after_read_only_routing(workspace):
    w, project, provider, session = workspace
    w.save_remote(project["id"], connection())
    await w.start_run(session["id"], {"providerId": provider["id"], "message": "查看远端目录", "kind": "auto", "remote": True})
    assert session["task"]["kind"] == "change"
    await settle(w)
    assert session["task"]["kind"] == "change"
    assert session["task"]["lastIntent"]["effectiveKind"] == "change"


async def test_remote_finish_requires_local_checks_when_source_changed(workspace, monkeypatch):
    w, project, provider, session = workspace
    w.save_remote(project["id"], connection())
    monkeypatch.setattr("backend.workspace.run_remote", lambda *args: {"status": "passed", "exitCode": 0, "output": "ok", "bytes": 2})
    await w.start_run(session["id"], {"providerId": provider["id"], "message": "修改并部署", "kind": "change", "remote": True})
    await settle(w)
    session["changes"].append({"taskId": session["task"]["id"], "status": "applied"})
    await w.execute(session, "remote_command", {"command": "true", "purpose": "部署后核验", "verification": True})
    await w.execute(session, "update_plan", {"summary": "修改并部署", "criteria": "本地及远端测试通过", "next_action": "交付"})
    with pytest.raises(AppError, match="当前源码的成功行为测试"):
        await w.execute(session, "finish_task", {"summary": "完成", "evidence": "远程测试通过"})
    assert "verification" not in session["task"]


async def test_browser_remote_config_and_new_session_grant(workspace, live_server, tmp_path, monkeypatch):
    w, _, _, _ = workspace
    folder = tmp_path / "remote-project"
    folder.mkdir()
    project = w.import_project(str(folder))
    monkeypatch.setattr("backend.workspace.probe_remote", lambda host, port: {"host": host, "port": port, "hostKey": FINGERPRINT, "algorithm": "ssh-ed25519"})

    async def handler(request):
        return httpx.Response(200, json={"choices": [{"message": {"tool_calls": [
            tool_call("request_user", {"question": "确认下一步？", "reason": "确认范围", "summary": "等待补充"})
        ]}}]})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as model, async_playwright() as playwright:
        w.model_client = model
        browser = await playwright.chromium.launch(channel="msedge", headless=True)
        try:
            page = await browser.new_page()
            await page.goto(live_server[1])
            await page.locator(f'[data-project-id="{project["id"]}"]').click()
            await expect(page.locator("#devAllowRemote")).to_be_disabled()
            await page.locator("#devAccessPicker>summary").click()
            await page.locator("#devAccessPicker .dev-task-options>summary").click()
            await page.locator("#devConfigureRemote").click()
            await page.fill("#devRemoteHost", "192.0.2.10")
            await page.fill("#devRemoteUser", "root")
            await page.fill("#devRemotePassword", "test-password")
            await page.locator("#devRemoteProbe").click()
            await expect(page.locator("#devRemoteKey")).to_have_value(FINGERPRINT)
            await page.locator("#devRemoteSave").click()
            await expect(page.locator("#devAllowRemote")).to_be_enabled()
            assert "test-password" not in json.dumps(w.state())
            await page.locator("#devCloseSettings").click()
            if await page.locator("#devAccessPicker").get_attribute("open") is None:
                await page.locator("#devAccessPicker>summary").click()
            if await page.locator("#devAccessPicker .dev-task-options").get_attribute("open") is None:
                await page.locator("#devAccessPicker .dev-task-options>summary").click()
            await page.check("#devAllowRemote")
            await page.fill("#devPrompt", "部署并核验")
            await page.locator("#devSendButton").click()
            await expect(page.locator("#devAgentStatus")).to_have_text("等待用户回答")
            sessions = [item for item in w.data["sessions"] if item["projectId"] == project["id"]]
            assert len(sessions) == 1
            assert sessions[0]["task"]["remoteScope"] == w.public_remote(w.remote_for_project(project["id"]))
        finally:
            await browser.close()
