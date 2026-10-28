"""Running-task steering is durable and reaches the next model request before new tools."""
import asyncio
import copy
import json

import httpx
import pytest
from playwright.async_api import async_playwright, expect

from backend.common import AppError
from backend.workspace import Workspace
from conftest import ROOT, settle, tool_call
from test_composer import paste_png


def answer(*calls):
    return httpx.Response(200, json={"choices": [{"message": {"tool_calls": list(calls)}}]})


async def begin(w, provider, s):
    await w.start_run(s["id"], {"providerId": provider["id"], "message": "修改 app.mjs 并验证", "permissions": {"edits": True, "commands": True}})


@pytest.mark.parametrize("use_enter", [False, True])
async def test_running_composer_receipt_and_next_request(workspace, live_server, use_enter):
    w, _, provider, s = workspace
    arrived, release, second, finish = (asyncio.Event() for _ in range(4))
    requests = []

    async def handler(request):
        requests.append(json.loads(request.content))
        if len(requests) == 1:
            arrived.set()
            await release.wait()
            # The old answer must never run after the user changes direction.
            return answer(tool_call("propose_file", {"path": "app.mjs", "content": "stale", "reason": "old plan"}),
                          tool_call("finish_task", {"summary": "stale", "evidence": "stale"}))
        second.set()
        await finish.wait()
        return answer(tool_call("request_user", {"question": "需要新的登录页文件吗？", "reason": "确认范围"}))

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client, async_playwright() as p:
        w.model_client = client
        browser = await p.chromium.launch(channel="msedge", headless=True)
        try:
            await begin(w, provider, s)
            await asyncio.wait_for(arrived.wait(), 5)
            task_id = s["task"]["id"]
            original = copy.deepcopy({k: s["task"][k] for k in ("goal", "permissions", "accessScope")})
            page = await browser.new_page(viewport={"width": 1440, "height": 1000})
            await page.route("https://images.unsplash.com/**", lambda route: route.abort())
            await page.goto(live_server[1])
            await page.locator(f'[data-session-id="{s["id"]}"]').click()
            await page.fill("#devPrompt", "只修改登录页 <script>，保留原来的配色")
            await paste_png(page.locator("#devPrompt"))
            await expect(page.locator("#devImageDrafts img")).to_have_count(1)
            await expect(page.locator("#devSendButton")).to_be_enabled()
            await expect(page.locator("#devSendButton")).to_have_text("补充要求")
            if use_enter:
                await page.press("#devPrompt", "Enter")
            else:
                await page.click("#devSendButton")
            receipt = page.locator(".dev-supplement-status")
            await expect(receipt).to_contain_text("待接收")
            await expect(receipt).to_contain_text("当前操作已开始，后续步骤生效")
            await expect(page.locator("#devPrompt")).to_have_value("")
            await expect(page.locator("#devImageDrafts img")).to_have_count(0)
            assert s["task"]["id"] == task_id and len(requests) == 1
            assert json.loads((w.data_dir / "workspace.json").read_text(encoding="utf-8"))["sessions"][0]["task"]["supplements"][0]["status"] == "pending"
            release.set()
            await asyncio.wait_for(second.wait(), 5)
            await expect(receipt).to_have_text("已纳入本次任务")
            assert s["changes"] == [] and s["commands"] == []
            assert {k: s["task"][k] for k in original} == original
            user_input = [m for m in requests[1]["messages"] if m["role"] == "user"]
            assert "只修改登录页 <script>，保留原来的配色" in str(user_input)
            assert "data:image/png;base64," in json.dumps(user_input)
            assert len([m for m in s["history"] if m["role"] == "user" and "本任务新增要求" in m["content"]]) == 1
            # Status text and literal user text must remain safe in a narrow viewport.
            assert await page.locator("#devConversation script").count() == 0
            await page.set_viewport_size({"width": 390, "height": 844})
            await page.fill("#devPrompt", "继续保持配色")
            await expect(page.locator("#devSendButton")).to_be_visible()
            button = await page.locator("#devSendButton").bounding_box()
            assert button["x"] >= 0 and button["x"] + button["width"] <= 391
            await page.screenshot(path=str(ROOT / ".local/python-check/supplement-mobile.png"), full_page=True)
            await page.set_viewport_size({"width": 1440, "height": 1000})
            await page.screenshot(path=str(ROOT / ".local/python-check/supplement-desktop.png"), full_page=True)
            finish.set()
            await settle(w)
        finally:
            release.set()
            finish.set()
            await browser.close()


async def test_inflight_tool_finishes_then_unstarted_tools_are_skipped(workspace):
    w, _, provider, s = workspace
    entered, release = asyncio.Event(), asyncio.Event()
    executed, requests = [], []
    original_execute = w.execute

    async def execute(session, name, args, stop):
        executed.append(name)
        if name == "read_file":
            entered.set()
            await release.wait()
        return await original_execute(session, name, args, stop)

    async def handler(request):
        requests.append(json.loads(request.content))
        if len(requests) == 1:
            return answer(tool_call("read_file", {"path": "app.mjs"}), tool_call("propose_file", {"path": "app.mjs", "content": "stale", "reason": "old"}))
        return answer(tool_call("request_user", {"question": "登录页路径？", "reason": "按新要求确认"}))

    w.execute = execute
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        w.model_client = client
        try:
            await begin(w, provider, s)
            await asyncio.wait_for(entered.wait(), 5)
            for text in ("只修改登录页", "保留配色"):
                await w.handle("POST", ["sessions", s["id"], "supplement"], {"taskId": s["task"]["id"], "message": text}, {})
            release.set()
            await settle(w)
        finally:
            release.set()
    assert executed == ["read_file", "request_user"]
    assert not s["changes"]
    assert [i["status"] for i in s["task"]["supplements"]] == ["included", "included"]
    contents = [m["content"] for m in requests[1]["messages"] if m["role"] == "user"]
    assert contents[-2:] == ["本任务新增要求（后续步骤按此调整）：\n只修改登录页", "本任务新增要求（后续步骤按此调整）：\n保留配色"]


async def test_pending_survives_stop_restart_and_resume(workspace):
    w, _, provider, s = workspace
    entered, release = asyncio.Event(), asyncio.Event()

    async def handler(request):
        entered.set()
        await release.wait()
        return answer(tool_call("request_user", {"question": "下一步？", "reason": "待确认"}))

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        w.model_client = client
        await begin(w, provider, s)
        await asyncio.wait_for(entered.wait(), 5)
        w.supplement_run(s["id"], {"taskId": s["task"]["id"], "message": "保留配色"})
        await w.stop(s["id"])
        release.set()
    assert s["task"]["supplements"][0]["status"] == "pending"
    restored = Workspace(w.data_dir, intent_classifier=lambda _: {"type": "development"})
    requests = []

    async def resume_handler(request):
        requests.append(json.loads(request.content))
        return answer(tool_call("request_user", {"question": "下一步？", "reason": "待确认"}))

    try:
        async with httpx.AsyncClient(transport=httpx.MockTransport(resume_handler)) as client:
            restored.model_client = client
            await restored.resume_run(s["id"])
            await settle(restored)
        assert restored.session(s["id"])["task"]["supplements"][0]["status"] == "included"
        assert "保留配色" in str(requests[0]["messages"])
    finally:
        await restored.shutdown()


async def test_classifier_cannot_finish_before_pending_requirement(workspace):
    w, _, provider, s = workspace
    entered, release = asyncio.Event(), asyncio.Event()

    async def classify(_):
        entered.set()
        await release.wait()
        return {"type": "chat", "reply": "你好"}

    requests = []

    async def handler(request):
        requests.append(json.loads(request.content))
        return answer(tool_call("request_user", {"question": "登录页路径？", "reason": "确认补充范围"}))

    w.intent_classifier = classify
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        w.model_client = client
        await begin(w, provider, s)
        await asyncio.wait_for(entered.wait(), 5)
        w.supplement_run(s["id"], {"taskId": s["task"]["id"], "message": "只修改登录页"})
        release.set()
        await settle(w)
    assert "只修改登录页" in str(requests[0]["messages"])
    assert s["status"] == "awaiting_user" and not s["task"].get("result")


async def test_review_queue_waits_for_approval_and_keeps_task_scope(workspace):
    w, _, provider, s = workspace
    requests = []

    async def handler(request):
        requests.append(json.loads(request.content))
        if len(requests) == 1:
            return answer(tool_call("read_file", {"path": "app.mjs"}))
        if len(requests) == 2:
            return answer(tool_call("propose_file", {"path": "app.mjs", "content": "export const add=(a,b)=>a+b;\n", "reason": "修复加法"}))
        return answer(tool_call("request_user", {"question": "下一步？", "reason": "确认新范围"}))

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        w.model_client = client
        await w.start_run(s["id"], {"providerId": provider["id"], "message": "修复加法"})
        await settle(w)
        assert s["status"] == "review"
        w.supplement_run(s["id"], {"taskId": s["task"]["id"], "message": "保留配色"})
        assert s["task"]["supplements"][0]["status"] == "pending" and len(requests) == 2
        await w.apply_change(s["id"], s["changes"][0]["id"], "discard")
        await settle(w)
    assert "保留配色" in str(requests[-1]["messages"])
    assert s["task"]["supplements"][0]["status"] == "included"


async def test_finished_task_rejection_preserves_composer_draft(workspace, live_server):
    w, _, provider, s = workspace
    entered, release = asyncio.Event(), asyncio.Event()

    async def handler(request):
        entered.set()
        await release.wait()
        return answer(tool_call("request_user", {"question": "下一步？", "reason": "确认范围"}))

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client, async_playwright() as p:
        w.model_client = client
        browser = await p.chromium.launch(channel="msedge", headless=True)
        try:
            await begin(w, provider, s)
            await asyncio.wait_for(entered.wait(), 5)
            page = await browser.new_page()
            await page.route("https://images.unsplash.com/**", lambda route: route.abort())
            await page.goto(live_server[1])
            await page.locator(f'[data-session-id="{s["id"]}"]').click()
            await page.fill("#devPrompt", "保留原来的配色")

            async def finish_before_delivery(route):
                release.set()
                await settle(w)
                await route.continue_()

            await page.route("**/supplement", finish_before_delivery)
            await page.click("#devSendButton")
            await expect(page.locator("#devError")).to_contain_text("补充要求未发送")
            await expect(page.locator("#devPrompt")).to_have_value("保留原来的配色")
            assert not s["task"].get("supplements")
        finally:
            release.set()
            await browser.close()


@pytest.mark.parametrize("status,archived,task_id,message", [("completed", False, "same", "test"), ("running", True, "same", "test"), ("running", False, "old", "test"), ("running", False, "same", ""), ("running", False, "same", 42), ("running", False, "same", "x" * 16001)])
async def test_rejected_supplements_never_mutate_task(workspace, status, archived, task_id, message):
    w, _, _, s = workspace
    s.update(status=status, archivedAt="test" if archived else None, task={"id": "same"})
    before = copy.deepcopy(s)
    with pytest.raises(AppError):
        w.supplement_run(s["id"], {"taskId": task_id, "message": message})
    assert s == before
