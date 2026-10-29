import copy

import pytest
from playwright.async_api import async_playwright, expect

from backend.common import AppError
from backend.model import TOOLS
from backend.workspace import Workspace
from conftest import prepare


def test_ssh_tools_and_configuration_methods_are_removed():
    names = {tool["function"]["name"] for tool in TOOLS}
    assert "remote_command" not in names
    assert "remote_upload" not in names
    for method in ("save_remote", "remove_remote", "remote_for_project", "checked_remote"):
        assert not hasattr(Workspace, method)


@pytest.mark.parametrize("remote", [True, False])
async def test_legacy_remote_run_flag_is_rejected_without_mutating_session(workspace, remote):
    w, _, provider, session = workspace
    before = copy.deepcopy(session)
    with pytest.raises(AppError, match="SSH 功能已移除") as error:
        await w.start_run(session["id"], {"providerId": provider["id"], "message": "检查代码", "remote": remote})
    assert error.value.status == 400
    assert session == before


async def test_legacy_ssh_routes_and_tool_calls_are_unavailable(workspace):
    w, project, provider, session = workspace
    for suffix in (("remote",), ("remote", "probe"), ("remote", "remove")):
        with pytest.raises(AppError, match="接口不存在") as error:
            await w.handle("POST", ["projects", project["id"], *suffix], {}, {})
        assert error.value.status == 404
    await prepare(w, provider, session)
    for name in ("remote_command", "remote_upload"):
        with pytest.raises(AppError, match="不支持的工具"):
            await w.execute(session, name, {})
    assert "remotes" not in w.state()


async def test_old_ssh_settings_are_dropped_on_workspace_start(workspace):
    w, _, provider, session = workspace
    await prepare(w, provider, session)
    w.data["remotes"] = [{"projectId": session["projectId"], "secret": "legacy-encrypted-password"}]
    session["task"]["remoteScope"] = {"host": "192.0.2.10"}
    session["task"]["remoteActions"] = [{"name": "remote_command"}]
    w.save()
    restored = Workspace(w.data_dir)
    try:
        assert "remotes" not in restored.data
        assert "remotes" not in restored.state()
        old_task = restored.session(session["id"])["task"]
        assert "remoteScope" not in old_task
        assert "remoteActions" not in old_task
        assert "legacy-encrypted-password" not in (w.data_dir / "workspace.json").read_text(encoding="utf-8")
    finally:
        await restored.shutdown()


async def test_permissions_and_settings_ui_has_no_ssh_controls(live_server):
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(channel="msedge", headless=True)
        try:
            page = await browser.new_page()
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            await page.goto(live_server[1])
            await page.locator('.activity-rail [data-view="developer"]').click()
            await expect(page.locator("#devWorkbench")).to_be_visible()
            await expect(page.locator("#devAccessPicker")).to_be_visible()
            await page.locator("#devModelPicker > summary").click()
            await page.locator("#devManageModel").click()
            await expect(page.locator("#devSettingsModal")).to_be_visible()
            for selector in ("#devAllowRemote", "#devConfigureRemote", "#devRemoteSection", "#devRemoteForm"):
                assert await page.locator(selector).count() == 0
            assert not errors
        finally:
            await browser.close()
