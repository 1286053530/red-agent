import asyncio
import json
from pathlib import Path

import httpx
import pytest

from backend.common import AppError
from backend.model import call_model
from backend.server import create_app
from conftest import ROOT, tool_call


async def test_api_host_origin_methods_and_private_assets(live_server):
    _, origin = live_server
    async with httpx.AsyncClient(base_url=origin, trust_env=False) as client:
        assert (await client.get("/")).status_code == 200
        assert "开发" in (await client.get("/developer.js")).text
        assert (await client.get("/api/dev/state")).status_code == 200
        for path in ["/backend/workspace.py", "/.local/developer/key", "/package.json", "/xhs-dom.mjs"]:
            assert (await client.get(path)).status_code == 404
        assert (await client.get("/api/dev/state", headers={"Origin": "https://evil.example"})).status_code == 403
        assert (await client.get("/api/dev/state", headers={"Host": "evil.example"})).status_code == 403
        assert (await client.get("/api/dev/state", headers={"Sec-Fetch-Site": "cross-site"})).status_code == 403
        assert (await client.post("/api/dev/projects", content='{}')).status_code == 415
        assert (await client.post("/api/dev/projects", content='x', headers={"Content-Type": "application/json"})).status_code == 400
        assert (await client.post("/api/dev/projects", json=[])).status_code == 400
        assert (await client.post("/api/dev/projects", content='x' * 1000001, headers={"Content-Type": "application/json"})).status_code == 413
        assert (await client.get("/api/xhs/connect")).status_code == 405
        assert (await client.post("/api/xhs/recommendations")).status_code == 410
        assert (await client.post("/api/xhs/messages")).status_code == 410


async def test_desktop_requires_session_cookie(workspace, tmp_path):
    w, _, _, _ = workspace
    app = create_app(ROOT, tmp_path, "desktop-secret", workspace=w)
    app.state.port = 3000
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://127.0.0.1:3000") as client:
        assert (await client.get("/api/dev/state")).status_code == 403
        assert (await client.get("/", headers={"Cookie": "shujin_session=desktop-secret"})).status_code == 200


async def test_openai_and_anthropic_protocols_and_failures():
    async def compatible(request):
        assert str(request.url) == "https://example.com/v1/chat/completions"
        assert request.headers["Authorization"] == "Bearer fixture"
        body = json.loads(request.content)
        assert body["tools"] and body["model"] == "fixture"
        return httpx.Response(200, json={"choices": [{"message": {"content": "ok"}}], "usage": {"prompt_tokens": 4}})
    provider = {"baseUrl": "https://example.com/v1", "protocol": "compatible", "model": "fixture", "apiKey": "fixture"}
    async with httpx.AsyncClient(transport=httpx.MockTransport(compatible)) as client:
        assert (await call_model(provider, [{"role": "user", "content": "ok"}], client=client))["usage"]["prompt_tokens"] == 4
    async def anthropic(request):
        assert str(request.url).endswith("/messages") and request.headers["x-api-key"] == "fixture"
        body = json.loads(request.content)
        assert body["system"] == "system"
        assert body["messages"][1]["content"][0]["type"] == "tool_use"
        assert body["messages"][2]["content"][0]["tool_use_id"] == "one"
        return httpx.Response(200, json={"content": [{"type": "text", "text": "done"}], "usage": {"input_tokens": 2}})
    async with httpx.AsyncClient(transport=httpx.MockTransport(anthropic)) as client:
        result = await call_model({**provider, "protocol": "anthropic"}, [{"role": "system", "content": "system"}, {"role": "user", "content": "read"},
            {"role": "assistant", "content": "", "tool_calls": [{"id": "one", "function": {"name": "list_files", "arguments": "{}"}}]},
            {"role": "tool", "tool_call_id": "one", "content": "{}"}], client=client)
        assert result["content"] == "done"
    for status in [401, 403, 404, 429, 500, 302]:
        async with httpx.AsyncClient(transport=httpx.MockTransport(lambda request: httpx.Response(status))) as client:
            with pytest.raises(AppError, match=str(status)):
                await call_model(provider, [{"role": "user", "content": "test"}], client=client)


async def test_developer_ui_uses_python_backend_and_exports_logs(workspace, live_server, tmp_path):
    from playwright.async_api import async_playwright
    w, project, provider, s = workspace
    _, origin = live_server
    steps = [("read_file", {"path": "app.mjs"}), ("update_plan", {"summary": "修复加法", "criteria": "测试通过", "next_action": "修正实现"}),
             ("propose_file", {"path": "app.mjs", "content": "export const add=(a,b)=>a+b;\n", "reason": "修复"}),
             ("run_command", {"command": "node", "args": ["--test", "app.test.mjs"], "purpose": "验证加法"}),
             ("review_diff", {}), ("finish_task", {"summary": "已修复加法", "evidence": "真实测试通过并复核变更"})]
    release_model = asyncio.Event()
    async def handler(request):
        await release_model.wait()
        name, args = steps.pop(0)
        return httpx.Response(200, json={"choices": [{"message": {"tool_calls": [tool_call(name, args)]}}]})
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as model, async_playwright() as playwright:
        w.model_client = model
        browser = await playwright.chromium.launch(channel="msedge", headless=True)
        try:
            page = await browser.new_page(viewport={"width": 1440, "height": 1000}, accept_downloads=True)
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            await page.goto(origin + "/#developer")
            await page.evaluate("showView('developer')")
            await page.locator(f'[data-project-id="{project["id"]}"]').click()
            await page.locator("#devModelPicker summary").click()
            await page.select_option("#devModelSelect", provider["id"])
            await page.locator("#devPrompt").click()
            assert await page.locator("#devSkillSelect").input_value() == "software-development"
            await page.fill("#devPrompt", "修复加法并测试")
            await page.click("#devSendButton")
            running = page.locator(f'[data-session-id="{s["id"]}"] .dev-session-status.running')
            await running.wait_for(state="visible")
            assert await running.get_attribute("aria-label") == "执行中"
            await page.locator('.activity-rail [data-view="account"]').click()
            assert not await page.locator(".sidebar").is_visible()
            await page.locator(f'.xhs-task-name[data-task-session-id="{s["id"]}"]').wait_for(state="visible")
            release_model.set()
            await page.locator('.activity-rail [data-view="developer"]').click()
            await page.locator('[data-change-action="apply"]').wait_for(timeout=15000)
            assert "a-b" in (Path(project["path"]) / "app.mjs").read_text()
            await page.click('[data-change-action="apply"]')
            await page.locator('[data-command-action="approve"]').wait_for(timeout=15000)
            await page.click('[data-command-action="approve"]')
            await page.wait_for_function("document.querySelector('#devExecution').innerText.includes('已完成')", timeout=15000)
            async with page.expect_download() as download:
                await page.click("#devExportLogs")
            downloaded = await download.value
            file = tmp_path / "logs.json"
            await downloaded.save_as(file)
            report = json.loads(file.read_text(encoding="utf-8"))
            assert report["entries"][-1]["type"] == "task_completed"
            assert report["task"]["skill"]["id"] == "software-development"
            assert "任务 Skill：软件开发" in await page.locator("#devExecution").inner_text()
            assert await page.locator("#devTraceTabPanel #devExecution").count() == 1
            assert not await page.locator(".dev-agent-panel #devExecution").count()
            assert not await page.locator(".dev-session-status.running").count()
            await page.click("#devFilesTab")
            await page.locator('[data-file-path="app.mjs"]').click()
            await page.wait_for_function("document.querySelector('#devFilePreview').textContent.includes('a+b')")
            composer = await page.locator("#devPrompt").bounding_box()
            assert composer["y"] + composer["height"] <= 1000
            output = ROOT / ".local/theme-check"
            output.mkdir(parents=True, exist_ok=True)
            await page.screenshot(path=str(output / "conversation.png"))
            await page.locator("#devModelPicker summary").click()
            await page.click("#devManageModel")
            assert await page.locator("#devSettingsModal").is_visible()
            await page.screenshot(path=str(output / "settings.png"))
            await page.click("#devCloseSettings")
            await page.locator('.activity-rail [data-view="account"]').click()
            completed_task = page.locator(f'.xhs-task-name[data-task-session-id="{s["id"]}"]')
            await completed_task.wait_for(state="visible")
            assert await page.locator('.xhs-task-group[aria-label="已完成"] .xhs-task-name').count() == 1
            await completed_task.click()
            await page.wait_for_function("document.body.dataset.view==='developer'")
            assert not errors
        finally:
            release_model.set()
            await browser.close()
