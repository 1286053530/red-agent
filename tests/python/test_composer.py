import httpx
from playwright.async_api import async_playwright

from conftest import ROOT, tool_call


async def test_composer_access_modes_control_real_task_permissions(workspace, live_server):
    w, project, _, session = workspace
    _, origin = live_server
    steps = [
        ("update_plan", {"summary": "审查加法", "criteria": "源码证据", "next_action": "读入口"}),
        ("read_file", {"path": "app.mjs"}),
        ("finish_task", {"summary": "加法错误 — app.mjs:1", "evidence": "使用 a-b；静态审查"}),
        ("update_plan", {"summary": "修复加法", "criteria": "测试通过", "next_action": "读入口"}),
        ("read_file", {"path": "app.mjs"}),
        ("propose_file", {"path": "app.mjs", "content": "export const add=(a,b)=>a+b;\n", "reason": "修复加法"}),
        ("run_command", {"command": "node", "args": ["--test", "app.test.mjs"], "purpose": "加法回归"}),
        ("review_diff", {}),
        ("finish_task", {"summary": "修复完成", "evidence": "加法回归测试通过"}),
    ]
    async def handler(request):
        name, args = steps.pop(0)
        return httpx.Response(200, json={"choices": [{"message": {"tool_calls": [tool_call(name, args)]}}]})
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as model, async_playwright() as playwright:
        w.model_client = model
        browser = await playwright.chromium.launch(channel="msedge", headless=True)
        try:
            page = await browser.new_page(viewport={"width": 1440, "height": 1000})
            await page.goto(origin)
            await page.locator(f'[data-project-id="{project["id"]}"]').click()
            await page.wait_for_function("document.querySelector('#devModelLabel').textContent==='fixture'")
            assert not await page.locator("#devModelSelect").is_visible()
            assert await page.locator("#devComposer #devAccessPicker").count() == 1
            assert await page.locator(".dev-agent-panel>.dev-model-row").count() == 0
            await page.locator("#devAccessPicker>summary").click()
            output = ROOT / ".local/composer-check"
            output.mkdir(parents=True, exist_ok=True)
            await page.locator('#devAccessScope>summary').click()
            scope_text = await page.locator('#devAccessScopeBody').inner_text()
            assert project['path'] in scope_text and 'https://example.com/v1' in scope_text
            assert '联网未隔离' in scope_text and '敏感配置' in scope_text
            await page.screenshot(path=str(output / "permissions.png"))
            await page.check('input[name="devAccessMode"][value="readonly"]')
            assert await page.locator("#devAccessLabel").inner_text() == "只读分析"
            assert await page.locator('#devAllowEdits').is_disabled()
            assert await page.locator('#devAllowCommands').is_disabled()
            await page.fill("#devPrompt", "审查加法")
            await page.locator("#devAccessPicker>summary").click()
            await page.locator("#devAccessPicker .dev-task-options>summary").click()
            await page.fill("#devAcceptance", "给出源码证据")
            await page.locator("#devAcceptance").press("Enter")
            assert not session.get("task"), "editing task criteria must not submit a task"
            await page.locator("#devPrompt").click()
            await page.click("#devSendButton")
            await page.wait_for_function("document.querySelector('#devAgentStatus').textContent==='已完成'")
            assert session["task"]["kind"] == "inspect"
            assert session["task"]["permissions"] == {"edits": False, "commands": False}
            assert '当前任务权限：只读分析' in await page.locator('#devTaskAccess').inner_text()
            assert not session["changes"] and not session["commands"]
            old_task_id = session["task"]["id"]
            await page.locator("#devAccessPicker>summary").click()
            await page.check('input[name="devAccessMode"][value="automatic"]')
            assert '当前任务权限：只读分析' in await page.locator('#devTaskAccess').inner_text()
            assert session["task"]["id"] == old_task_id
            assert session["task"]["permissions"] == {"edits": False, "commands": False}
            await page.fill("#devPrompt", "修复加法并测试")
            await page.click("#devSendButton")
            await page.wait_for_function("document.querySelector('#devAgentStatus').textContent==='已完成' && document.querySelector('#devTaskAccess').textContent.includes('当前任务权限：自动执行')", timeout=20000)
            assert session["task"]["kind"] == "change"
            assert session["task"]["permissions"] == {"edits": True, "commands": True}
            assert '当前任务权限：自动执行' in await page.locator('#devTaskAccess').inner_text()
            assert session["changes"][-1]["status"] == "applied"
            assert session["commands"][-1]["status"] == "passed"
            assert not steps
            await page.locator("#devModelPicker>summary").click()
            await page.screenshot(path=str(output / "models.png"))
            await page.keyboard.press("Escape")
            assert not await page.locator("#devModelSelect").is_visible()
        finally:
            await browser.close()
