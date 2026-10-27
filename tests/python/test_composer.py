import asyncio
import base64
import json
import httpx
import pytest
from playwright.async_api import async_playwright, expect

from conftest import ROOT, tool_call


PNG = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jRZkAAAAASUVORK5CYII=')


async def paste_png(prompt):
    await prompt.evaluate("""(el, encoded) => {
      const bytes = Uint8Array.from(atob(encoded), c => c.charCodeAt(0));
      const data = new DataTransfer();
      data.items.add(new File([bytes], 'clipboard.png', {type: 'image/png'}));
      el.dispatchEvent(new ClipboardEvent('paste', {clipboardData: data, bubbles: true, cancelable: true}));
    }""", base64.b64encode(PNG).decode())


@pytest.mark.parametrize('transition', ['stop', 'question'])
async def test_running_task_keeps_editable_draft(workspace, live_server, transition):
    w, project, _, session = workspace
    _, origin = live_server
    release_model = asyncio.Event()
    requests = []

    async def handler(request):
        requests.append(json.loads(request.content))
        await release_model.wait()
        return httpx.Response(200, json={"choices": [{"message": {"tool_calls": [
            tool_call('request_user', {'question': '确认下一步？', 'reason': '确认范围', 'summary': '等待补充'})
        ]}}]})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as model, async_playwright() as playwright:
        w.model_client = model
        browser = await playwright.chromium.launch(channel='msedge', headless=True)
        try:
            page = await browser.new_page(viewport={'width': 1440, 'height': 1000})
            await page.route('https://images.unsplash.com/**', lambda route: route.abort())
            await page.goto(origin)
            await page.locator(f'[data-project-id="{project["id"]}"]').click()
            prompt = page.locator('#devPrompt')
            await prompt.fill('分析项目，先确认任务范围')
            await page.locator('#devSendButton').click()
            await page.wait_for_function("document.querySelector('#devAgentStatus').textContent==='执行中' && !document.querySelector('#devPrompt').disabled")
            await expect(prompt).to_be_enabled()
            task_id = session['task']['id']
            await prompt.press_sequentially('补充要求：保留已有修改')
            await prompt.press('Enter')
            await prompt.press_sequentially('完成后给出验证结果')
            draft = '补充要求：保留已有修改\n完成后给出验证结果'
            assert await prompt.input_value() == draft
            await paste_png(prompt)
            await page.locator('#devImageDrafts img').wait_for()
            await page.locator('[data-remove-image]').click()
            assert await page.locator('#devImageDrafts img').count() == 0
            await paste_png(prompt)
            await page.locator('#devImageDrafts img').wait_for()
            assert await page.locator('#devSendButton').is_disabled()
            assert await page.locator('#devStopButton').is_visible()
            # Real polling must not disable or overwrite the draft, focus or selection.
            await prompt.focus()
            await prompt.evaluate('el => el.setSelectionRange(2, 6)')
            for _ in range(2):
                async with page.expect_response(lambda r: r.url.endswith('/sessions/' + session['id']) and r.request.method == 'GET'):
                    pass
            assert await prompt.input_value() == draft
            assert await prompt.evaluate('el => [document.activeElement === el, el.selectionStart, el.selectionEnd]') == [True, 2, 6]
            await expect(prompt).to_be_enabled()
            await page.locator('#devComposer').evaluate('el => el.requestSubmit()')
            assert session['task']['id'] == task_id and len(requests) == 1
            assert len([m for m in session['messages'] if m['role'] == 'user']) == 1
            if transition == 'stop':
                await page.locator('#devStopButton').click()
                await page.wait_for_function("document.querySelector('#devAgentStatus').textContent==='已停止'")
            else:
                release_model.set()
                await page.wait_for_function("document.querySelector('#devAgentStatus').textContent==='等待用户回答'")
            assert await prompt.input_value() == draft
            assert await page.locator('#devImageDrafts img').count() == 1
            assert await page.locator('#devSendButton').is_enabled()
            release_model.set()
            await page.locator('#devSendButton').click()
            await page.wait_for_function("document.querySelector('#devAgentStatus').textContent==='等待用户回答' && document.querySelector('#devPrompt').value===''")
            assert len(requests) == 2
            user_messages = [m for m in session['messages'] if m['role'] == 'user']
            assert user_messages[-1]['content'] == draft and user_messages[-1]['images']
            assert 'data:image/png;base64,' in json.dumps(requests[-1])
            assert await page.locator('#devImageDrafts img').count() == 0
        finally:
            release_model.set()
            await browser.close()


async def test_composer_draft_without_selected_project(workspace, live_server):
    w, project, _, session = workspace
    _, origin = live_server
    w.archive_session(session['id'], True)
    requests = []

    async def handler(request):
        requests.append(json.loads(request.content))
        return httpx.Response(200, json={"choices": [{"message": {"tool_calls": [
            tool_call('request_user', {'question': '确认任务范围？', 'reason': '确认预期', 'summary': '等待回答'})
        ]}}]})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as model, async_playwright() as playwright:
        w.model_client = model
        browser = await playwright.chromium.launch(channel='msedge', headless=True)
        try:
            page = await browser.new_page(viewport={'width': 1440, 'height': 1000})
            await page.route('https://images.unsplash.com/**', lambda route: route.abort())
            await page.add_init_script("localStorage.setItem('devProject','removed-project');localStorage.setItem('devSession','removed-session');")
            await page.goto(origin)
            prompt = page.locator('#devPrompt')
            await page.wait_for_function("document.querySelector('#devModelLabel').textContent==='fixture'")
            await expect(prompt).to_be_enabled()
            assert await page.locator('#devAddImage, #devImageInput').count() == 0
            assert await page.locator('#devSessionCount').inner_text() == '选择项目后开始'
            assert await page.locator('[data-session-id]').count() == 1
            assert '选择项目后发送' in await prompt.get_attribute('placeholder')
            await page.click('#devBrowserTab')
            await prompt.fill('检查项目中的问题')
            await paste_png(prompt)
            await page.locator('#devImageDrafts img').wait_for()
            await prompt.click()
            assert not await page.evaluate("document.querySelector('#developerView').classList.contains('files-collapsed')")
            assert await page.locator('#devSendButton').is_disabled()
            assert await page.locator('#devSendButton').get_attribute('title') == '请先选择左侧项目'
            await prompt.press('Enter')
            assert not requests
            await page.locator(f'[data-project-id="{project["id"]}"]').click()
            assert await prompt.input_value() == '检查项目中的问题'
            assert await page.locator('#devImageDrafts img').count() == 1
            assert await page.locator('#devImageDrafts figcaption').inner_text() == 'clipboard.png'
            await expect(prompt).to_be_enabled()
            assert await page.locator('#devSendButton').is_enabled()
            assert len(w.data['sessions']) == 1
            await page.locator('#devSendButton').click()
            await page.wait_for_function("document.querySelector('#devAgentStatus').textContent==='等待用户回答'")
            assert len(requests) == 1
            assert 'data:image/png;base64,' in json.dumps(requests[0])
            assert len(w.data['sessions']) == 2
            await expect(prompt).to_be_enabled()
            assert await prompt.input_value() == ''
            await page.locator('.dev-archived-sessions>summary').click()
            await page.locator(f'[data-session-id="{session["id"]}"]').click()
            assert await prompt.is_disabled()
            await page.locator('#devNewSessionButton').click()
            await page.wait_for_function("!document.querySelector('#devPrompt').disabled")
            await expect(prompt).to_be_enabled()
            output = ROOT / '.local/composer-check'
            output.mkdir(parents=True, exist_ok=True)
            await page.screenshot(path=str(output / 'project-draft.png'))
        finally:
            await browser.close()


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
            await page.route('https://images.unsplash.com/**', lambda route: route.abort())
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
