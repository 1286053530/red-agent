"""Project preferences survive new conversations without changing existing tasks."""
import asyncio
import copy
import json

import httpx
import pytest
from playwright.async_api import async_playwright, expect

from backend.common import AppError
from backend.workspace import Workspace
from conftest import settle, tool_call


@pytest.mark.parametrize("kind, permissions, expected", [
    ("auto", {"edits": True, "commands": True}, {"edits": True, "commands": True}),
    ("change", {"edits": True, "commands": False}, {"edits": True, "commands": False}),
    ("inspect", {"edits": True, "commands": True}, {"edits": False, "commands": False}),
])
async def test_project_settings_persist_independently(workspace, tmp_path, kind, permissions, expected):
    w, project, _, _ = workspace
    folder = tmp_path / "second-project"
    folder.mkdir()
    second = w.import_project(str(folder))
    settings = {"kind": kind, "permissions": expected}
    result = await w.handle("POST", ["projects", project["id"], "task-settings"],
                            {"kind": kind, "permissions": permissions}, {})
    assert result == settings
    result["permissions"]["edits"] = not expected["edits"]
    assert project["taskSettings"] == settings
    assert "taskSettings" not in second
    loaded = Workspace(w.data_dir)
    try:
        assert loaded.project(project["id"])["taskSettings"] == settings
        assert "taskSettings" not in loaded.project(second["id"])
    finally:
        await loaded.shutdown()


@pytest.mark.parametrize("previous", [None, {"kind": "inspect", "permissions": {"edits": False, "commands": False}}])
async def test_failed_settings_save_preserves_memory_and_disk(workspace, monkeypatch, previous):
    w, project, _, _ = workspace
    if previous:
        w.save_task_settings(project["id"], previous)
    persisted = (w.data_dir / "workspace.json").read_bytes()

    def fail_save():
        raise OSError("模拟磁盘写入失败")

    with monkeypatch.context() as patch:
        patch.setattr(w, "save", fail_save)
        with pytest.raises(OSError, match="磁盘写入失败"):
            w.save_task_settings(project["id"], {"kind": "auto", "permissions": {"edits": True, "commands": True}})
    assert project.get("taskSettings") == previous
    assert (w.data_dir / "workspace.json").read_bytes() == persisted


@pytest.mark.parametrize("settings", [
    {}, {"kind": "unknown", "permissions": {}},
    {"kind": "auto", "permissions": None},
    {"kind": "auto", "permissions": {"edits": "true"}},
])
async def test_invalid_preferences_do_not_replace_saved_settings(workspace, settings):
    w, project, _, _ = workspace
    previous = w.save_task_settings(project["id"], {"kind": "change", "permissions": {"commands": True}})
    with pytest.raises(AppError):
        w.save_task_settings(project["id"], settings)
    assert project["taskSettings"] == previous


@pytest.fixture
async def access_page(workspace, live_server):
    w, _, _, session = workspace
    _, origin = live_server

    async def handler(request):
        return httpx.Response(200, json={"choices": [{"message": {"tool_calls": [
            tool_call("request_user", {"question": "确认下一步？", "reason": "确认范围", "summary": "等待补充"})
        ]}}]})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as model, async_playwright() as playwright:
        w.model_client = model
        browser = await playwright.chromium.launch(channel="msedge", headless=True)
        try:
            page = await browser.new_page(viewport={"width": 1440, "height": 1000})
            await page.route("https://images.unsplash.com/**", lambda route: route.abort())
            await page.goto(origin)
            await page.locator(f'[data-session-id="{session["id"]}"]').click()
            await expect(page.locator("#devModelLabel")).to_have_text("fixture")
            yield page
        finally:
            await browser.close()


async def open_access(page):
    if await page.locator("#devAccessPicker").get_attribute("open") is None:
        await page.locator("#devAccessPicker>summary").click()


async def choose_mode(page, mode):
    await open_access(page)
    await page.check(f'input[name="devAccessMode"][value="{mode}"]')


async def wait_saved(page):
    await expect(page.locator("#devAccessSaveStatus")).to_have_text("已保存到本机，供本项目的新对话使用。")


@pytest.mark.parametrize("mode, kind, grants, label", [
    ("automatic", "auto", True, "自动执行"),
    ("readonly", "inspect", False, "只读分析"),
])
async def test_new_conversation_and_fresh_browser_restore_preferences(workspace, access_page, live_server, mode, kind, grants, label):
    w, project, _, original = workspace
    page = access_page
    await choose_mode(page, mode)
    await wait_saved(page)
    await page.locator("#devNewSessionButton").click()
    await expect(page.locator("#devAccessLabel")).to_have_text(label)
    await expect(page.locator("#devPrompt")).to_be_enabled()
    await expect(page.locator(f'input[name="devAccessMode"][value="{mode}"]')).to_be_checked()
    await expect(page.locator('input[name="devAccessMode"]')).to_have_count(3)
    await expect(page.locator('input[name="devAccessMode"][value="previous"]')).to_have_count(0)
    new_id = await page.evaluate("localStorage.getItem('devSession')")
    assert new_id != original["id"]
    # A clean browser context has no localStorage from the original window.
    fresh = await page.context.browser.new_page()
    try:
        await fresh.route("https://images.unsplash.com/**", lambda route: route.abort())
        await fresh.goto(live_server[1])
        await fresh.locator(f'[data-session-id="{new_id}"]').click()
        await expect(fresh.locator("#devAccessLabel")).to_have_text(label)
        await expect(fresh.locator(f'input[name="devAccessMode"][value="{mode}"]')).to_be_checked()
        await fresh.fill("#devPrompt", "修复加法，先确认任务范围")
        await fresh.click("#devSendButton")
        await expect(fresh.locator("#devAgentStatus")).to_have_text("等待用户回答")
        task = w.session(new_id)["task"]
        assert task["kind"] == ("change" if kind == "auto" else kind)
        assert task["permissions"] == {"edits": grants, "commands": grants}
        assert project["taskSettings"] == {"kind": kind, "permissions": task["permissions"]}
    finally:
        await fresh.close()


async def test_custom_permissions_are_isolated_by_project(workspace, access_page, live_server, tmp_path):
    w, first, _, _ = workspace
    folder = tmp_path / "another-project"
    folder.mkdir()
    second = w.import_project(str(folder))
    second_session = w.create_session({"projectId": second["id"]})
    page = access_page
    await open_access(page)
    await page.locator("#devAccessPicker .dev-task-options>summary").click()
    await page.select_option("#devTaskKind", "change")
    await page.check("#devAllowEdits")
    await wait_saved(page)
    custom = {"kind": "change", "permissions": {"edits": True, "commands": False}}
    assert first["taskSettings"] == custom
    await page.reload()
    await page.locator(f'[data-session-id="{second_session["id"]}"]').click()
    await expect(page.locator("#devAccessLabel")).to_have_text("逐项审核")
    await expect(page.locator('input[name="devAccessMode"][value="review"]')).to_be_checked()
    await choose_mode(page, "readonly")
    await wait_saved(page)
    first_session = workspace[3]
    await page.locator(f'[data-session-id="{first_session["id"]}"]').click()
    await expect(page.locator("#devAccessLabel")).to_have_text("自定义权限")
    assert await page.locator("#devTaskKind").input_value() == "change"
    assert await page.locator("#devAllowEdits").is_checked()
    assert not await page.locator("#devAllowCommands").is_checked()
    assert second["taskSettings"]["kind"] == "inspect"


async def test_changing_preferences_does_not_change_resumed_task(workspace, access_page):
    w, _, _, session = workspace
    page = access_page
    await choose_mode(page, "review")
    await page.fill("#devPrompt", "修复加法，先确认范围")
    await page.click("#devSendButton")
    await expect(page.locator("#devAgentStatus")).to_have_text("等待用户回答")
    task = copy.deepcopy(session["task"])
    await choose_mode(page, "automatic")
    await wait_saved(page)
    await page.fill("#devPrompt", "继续确认范围")
    await page.click("#devSendButton")
    await expect(page.locator("#devPrompt")).to_have_value("")
    await settle(w)
    assert session["task"]["id"] == task["id"]
    assert session["task"]["permissions"] == task["permissions"] == {"edits": False, "commands": False}
    assert session["task"]["accessScope"] == task["accessScope"]


async def test_failed_save_keeps_draft_and_blocks_creation_and_send(workspace, access_page):
    w, project, _, session = workspace
    page = access_page
    pattern = "**/projects/*/task-settings"

    async def fail(route):
        await route.fulfill(status=500, content_type="application/json", body=json.dumps({"error": "模拟保存失败"}))

    await page.route(pattern, fail)
    await choose_mode(page, "automatic")
    await expect(page.locator("#devAccessSaveStatus")).to_contain_text("权限保存失败")
    await page.click("#devNewSessionButton")
    await expect(page.locator("#devNewSessionButton")).to_be_enabled()
    assert len(w.data["sessions"]) == 1
    await page.fill("#devPrompt", "修复加法")
    await page.click("#devSendButton")
    await expect(page.locator("#devSendButton")).to_be_enabled()
    assert not session.get("task")
    assert "taskSettings" not in project
    await expect(page.locator("#devPrompt")).to_have_value("修复加法")
    await expect(page.locator("#devError")).to_contain_text("模拟保存失败")
    await page.unroute(pattern, fail)
    # Reselecting the mode retries the retained selection.
    await choose_mode(page, "review")
    await choose_mode(page, "automatic")
    await wait_saved(page)
    await page.click("#devNewSessionButton")
    await expect(page.locator("#devAccessLabel")).to_have_text("自动执行")
    assert len(w.data["sessions"]) == 2


async def test_serial_saves_finish_before_new_conversation(workspace, access_page):
    w, project, _, _ = workspace
    page = access_page
    started, release = asyncio.Event(), asyncio.Event()
    received = []

    async def delay(route):
        received.append(route.request.post_data_json)
        if len(received) == 1:
            started.set()
            await release.wait()
        await route.continue_()

    await page.route("**/projects/*/task-settings", delay)
    try:
        await choose_mode(page, "automatic")
        await asyncio.wait_for(started.wait(), 5)
        await choose_mode(page, "readonly")
        await page.fill("#devPrompt", "草稿内容")
        await page.click("#devNewSessionButton")
        await expect(page.locator("#devNewSessionButton")).to_be_disabled()
        await expect(page.locator("#devSendButton")).to_be_disabled()
        # Programmatic duplicate submissions also obey the in-flight guard.
        await page.locator("#devNewSessionButton").dispatch_event("click")
        await page.locator("#devComposer").evaluate("el => el.requestSubmit()")
        assert len(received) == 1 and len(w.data["sessions"]) == 1
        release.set()
        await expect(page.locator("#devNewSessionButton")).to_be_enabled()
        await expect(page.locator("#devAccessLabel")).to_have_text("只读分析")
        assert len(w.data["sessions"]) == 2
        assert len(received) == 2 and received[-1]["kind"] == "inspect"
        assert project["taskSettings"] == received[-1]
        assert not any(s.get("task") for s in w.data["sessions"])
    finally:
        release.set()


@pytest.mark.parametrize("action", ["create", "send"])
async def test_switching_project_cancels_action_waiting_for_save(workspace, access_page, tmp_path, action):
    w, _, _, session = workspace
    folder = tmp_path / "switch-project"
    folder.mkdir()
    second = w.import_project(str(folder))
    second_session = w.create_session({"projectId": second["id"]})
    page = access_page
    await page.reload()
    await page.locator(f'[data-session-id="{session["id"]}"]').click()
    started, release = asyncio.Event(), asyncio.Event()

    async def delay(route):
        started.set()
        await release.wait()
        await route.continue_()

    await page.route("**/projects/*/task-settings", delay)
    try:
        await choose_mode(page, "automatic")
        await asyncio.wait_for(started.wait(), 5)
        await page.fill("#devPrompt", "修复加法")
        await page.click("#devNewSessionButton" if action == "create" else "#devSendButton")
        await page.locator(f'[data-session-id="{second_session["id"]}"]').click()
        await expect(page.locator("#devAccessLabel")).to_have_text("逐项审核")
        release.set()
        await expect(page.locator("#devNewSessionButton")).to_be_enabled()
        assert len(w.data["sessions"]) == 2
        assert not any(s.get("task") for s in w.data["sessions"])
        assert await page.evaluate("localStorage.getItem('devSession')") == second_session["id"]
    finally:
        release.set()
