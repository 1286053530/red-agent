"""Composer continuations preserve unfinished tasks and recover legacy placeholders."""
import copy
import json
from contextlib import asynccontextmanager

import httpx
import pytest
from playwright.async_api import async_playwright, expect

from backend.common import AppError
from backend.workspace import Workspace, continuation_request
from conftest import settle, tool_call


GOAL = "修复加法并验证现有用例"


@asynccontextmanager
async def model_steps(w, steps, requests=None):
    async def handler(request):
        if requests is not None:
            requests.append(json.loads(request.content))
        name, args = steps.pop(0)
        return httpx.Response(200, json={"choices": [{"message": {"tool_calls": [tool_call(name, args)]}}]})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        w.model_client = client
        yield


async def failed_task(workspace, stopped=False):
    w, _, provider, session = workspace
    steps = [
        ("read_file", {"path": "app.mjs"}),
        ("update_plan", {"summary": "已定位加法实现", "criteria": "现有回归通过", "next_action": "修改加法", "todo": ["修复运算符", "验证现有用例"]}),
        ("fail_task", {"reason": "本次执行未完成", "evidence": "已读取 app.mjs，尚未修改"}),
    ]
    async with model_steps(w, steps):
        await w.start_run(session["id"], {"providerId": provider["id"], "message": GOAL, "kind": "change",
                                          "permissions": {"edits": True, "commands": True}})
        await settle(w)
    assert session["status"] == "failed"
    if stopped:
        await w.stop(session["id"])
    return copy.deepcopy(session["task"])


QUESTION = ("request_user", {"question": "是否继续验证？", "reason": "回归在此暂停"})


@pytest.mark.parametrize("message", ["继续", "继续完成未完成的任务", "请继续执行当前任务！", "接着处理上次的工作", "重试", "再试一次", "Continue.", "resume", "retry"])
async def test_old_client_run_endpoint_resumes_same_task(workspace, message):
    w, _, _, session = workspace
    task = await failed_task(workspace)
    history, observations = copy.deepcopy(session["history"]), copy.deepcopy(session["observations"])
    requests = []
    async with model_steps(w, [QUESTION], requests):
        # A new-task provider or permission selection must not alter a continuation.
        await w.handle("POST", ["sessions", session["id"], "run"],
                       {"message": message, "providerId": "unused-new-provider", "kind": "inspect", "permissions": {}}, {})
        await settle(w)
    assert session["task"]["id"] == task["id"] and not session.get("tasks")
    assert session["task"]["goal"] == GOAL
    assert session["task"]["acceptance"] == task["acceptance"]
    assert session["task"]["permissions"] == task["permissions"]
    assert session["task"]["accessScope"] == task["accessScope"]
    assert session["observations"] == observations
    assert session["history"][:len(history)] == history
    assert session["task"]["attempt"] == 2
    assert session["task"]["attempts"][-1]["status"] == "failed"
    persisted = json.loads(requests[0]["messages"][1]["content"].split("\n", 1)[1])
    assert persisted["goal"] == GOAL
    assert persisted["checkpoint"] == task["checkpoint"]


@pytest.mark.parametrize("message", ["继续开发登录页面", "继续：修改另一个文件", "重新实现搜索", "重试按钮的样式", "continue with a different feature", "", None])
def test_new_goals_are_not_continuation_phrases(message):
    assert not continuation_request(message)


@pytest.mark.parametrize("stopped, use_enter", [(False, False), (True, True)])
async def test_composer_continues_with_original_model_and_permissions(workspace, live_server, stopped, use_enter):
    w, project, provider, session = workspace
    task = await failed_task(workspace, stopped)
    alternate = w.save_provider({"name": "new-task-model", "baseUrl": "https://example.org/v1", "model": "other", "protocol": "compatible"})
    requests, endpoints = [], []
    async with model_steps(w, [QUESTION], requests), async_playwright() as playwright:
        browser = await playwright.chromium.launch(channel="msedge", headless=True)
        try:
            page = await browser.new_page(viewport={"width": 1440, "height": 1000})
            await page.route("https://images.unsplash.com/**", lambda route: route.abort())
            await page.goto(live_server[1])
            await page.locator(f'[data-session-id="{session["id"]}"]').click()
            await expect(page.locator("#devAgentStatus")).to_have_text("已停止" if stopped else "失败")
            await page.locator("#devModelPicker>summary").click()
            await page.select_option("#devModelSelect", alternate["id"])
            await page.locator("#devAccessPicker>summary").click()
            await page.check('input[name="devAccessMode"][value="readonly"]')
            await expect(page.locator("#devAccessSaveStatus")).to_contain_text("已保存到本机")
            page.on("request", lambda req: endpoints.append(req.url) if req.method == "POST" else None)
            await page.fill("#devPrompt", "继续完成未完成的任务" if stopped else "继续")
            await expect(page.locator("#devSendButton")).to_have_attribute("aria-label", "继续当前任务")
            if use_enter:
                await page.press("#devPrompt", "Enter")
            else:
                await page.click("#devSendButton")
            await expect(page.locator("#devAgentStatus")).to_have_text("等待用户回答")
            await expect(page.locator("#devPrompt")).to_have_value("")
            assert any(url.endswith("/resume") for url in endpoints)
            assert not any(url.endswith("/run") for url in endpoints)
            assert session["task"]["id"] == task["id"] and not session.get("tasks")
            assert session["task"]["permissions"] == {"edits": True, "commands": True}
            assert session["task"]["checkpoint"] == task["checkpoint"]
            assert session["task"]["accessScope"] == task["accessScope"]
            assert session["providerId"] == provider["id"]
            assert requests[0]["model"] == provider["model"]
            assert project["taskSettings"]["kind"] == "inspect"
        finally:
            await browser.close()


@pytest.mark.parametrize("state", ["idle", "completed", "failed"])
async def test_new_requests_still_create_tasks(workspace, state):
    w, _, provider, session = workspace
    old = None
    if state != "idle":
        old = await failed_task(workspace)
        if state == "completed":
            session["status"] = "completed"
            session["task"]["outcome"]["status"] = "completed"
    message = "继续" if state != "failed" else "继续开发登录页面"
    async with model_steps(w, [QUESTION]):
        await w.start_run(session["id"], {"providerId": provider["id"], "message": message})
        await settle(w)
    assert session["task"]["goal"] == message
    if old:
        assert session["task"]["id"] != old["id"]
        assert session["tasks"][-1]["id"] == old["id"]


async def legacy_placeholder(workspace):
    w, _, provider, session = workspace
    original = await failed_task(workspace)
    session["messages"].insert(0, {"role": "user", "content": "本对话更早的独立任务，不属于当前目标"})
    session["messages"].append({"role": "user", "content": "本目标补充：保持公开接口兼容"})
    # Simulate a persisted pre-fix task: /run had archived the original and lost history.
    async with model_steps(w, [QUESTION]):
        await w.start_run(session["id"], {"providerId": provider["id"], "message": "新任务占位"})
        await settle(w)
    session["task"]["goal"] = "继续完成未完成的任务"
    next(m for m in session["messages"] if m.get("content") == "新任务占位")["content"] = session["task"]["goal"]
    session["history"] = [{"role": "user", "content": "继续完成未完成的任务"}]
    w.save()
    return original, copy.deepcopy(session["task"])


async def test_legacy_placeholder_recovers_original_checkpoint_after_restart(workspace):
    w, _, _, session = workspace
    original, placeholder = await legacy_placeholder(workspace)
    loaded = Workspace(w.data_dir)
    loaded.intent_classifier = lambda message: {"type": "development"}
    requests = []
    try:
        async with model_steps(loaded, [QUESTION], requests):
            await loaded.resume_run(session["id"], {"feedback": "继续"})
            await settle(loaded)
        restored = loaded.session(session["id"])
        assert restored["task"]["id"] == original["id"]
        assert restored["task"]["permissions"] == original["permissions"]
        assert restored["task"]["accessScope"] == original["accessScope"]
        assert restored["task"]["checkpoint"] == original["checkpoint"]
        assert restored["task"]["attempt"] == 2
        assert restored["tasks"][-1]["id"] == placeholder["id"]
        assert restored["tasks"][-1]["recoveredToTaskId"] == original["id"]
        assert restored["history"][0]["content"] == GOAL
        assert "旧工具上下文已丢失" in str(requests[0]["messages"])
        assert "本次任务未完成" in str(requests[0]["messages"])
        assert "本目标补充：保持公开接口兼容" in str(requests[0]["messages"])
        assert "本对话更早的独立任务" not in str(requests[0]["messages"])
        assert any("已恢复原任务" in msg["content"] for msg in restored["messages"])
        persisted = json.loads((loaded.data_dir / "workspace.json").read_text(encoding="utf-8"))
        assert persisted["sessions"][0]["task"]["id"] == original["id"]
    finally:
        await loaded.shutdown()


@pytest.mark.parametrize("barrier", ["archived", "pending", "changed_model", "changed_root"])
async def test_resume_rejection_preserves_legacy_task_and_draft_data(workspace, barrier):
    w, project, provider, session = workspace
    await legacy_placeholder(workspace)
    if barrier == "archived":
        session["archivedAt"] = "2026-10-27"
    elif barrier == "pending":
        session["changes"].append({"status": "pending", "taskId": session["task"]["id"]})
    elif barrier == "changed_model":
        w.find(w.data["providers"], provider["id"], "模型")["model"] = "changed"
    else:
        project["path"] += "-moved"
    before = copy.deepcopy(session)
    with pytest.raises(AppError):
        await w.resume_run(session["id"], {"feedback": "继续"})
    assert session == before
    assert not w.runs


@pytest.mark.parametrize("barrier", ["completed_original", "placeholder_changed", "placeholder_command"])
async def test_recovery_does_not_replace_completed_or_active_work(workspace, barrier):
    w, _, _, session = workspace
    await legacy_placeholder(workspace)
    if barrier == "completed_original":
        session["tasks"][-1]["outcome"]["status"] = "completed"
    elif barrier == "placeholder_changed":
        session["changes"].append({"status": "applied", "taskId": session["task"]["id"]})
    else:
        session["commands"].append({"status": "passed", "taskId": session["task"]["id"]})
    assert w.continuation_target(session) is session["task"]


async def test_continuation_uses_only_current_unfinished_conversation(workspace):
    w, project, provider, session = workspace
    task = await failed_task(workspace)
    session["history"].append({"role": "user", "content": "本对话补充：保留既有接口"})
    other_id = w.create_session({"projectId": project["id"]})["id"]
    async with model_steps(w, [QUESTION]):
        await w.start_run(other_id, {"providerId": provider["id"], "message": "另一对话：新增报表"})
        await settle(w)
    other = copy.deepcopy(w.session(other_id))
    requests = []
    async with model_steps(w, [QUESTION], requests):
        await w.start_run(session["id"], {"message": "继续"})
        await settle(w)
    context = str(requests[0]["messages"])
    assert GOAL in context and "本对话补充：保留既有接口" in context
    assert "另一对话：新增报表" not in context
    assert session["task"]["id"] == task["id"]
    assert w.session(other_id) == other
    new_id = w.create_session({"projectId": project["id"]})["id"]
    requests = []
    async with model_steps(w, [QUESTION], requests):
        await w.start_run(new_id, {"providerId": provider["id"], "message": "继续"})
        await settle(w)
    assert w.session(new_id)["task"]["goal"] == "继续"
    assert GOAL not in str(requests[0]["messages"])
    assert "另一对话：新增报表" not in str(requests[0]["messages"])
