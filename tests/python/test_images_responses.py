import base64
import json

import httpx
import pytest
from playwright.async_api import async_playwright, expect

from backend.common import AppError
from backend.images import validate_images
from backend.model import call_model
from backend.runtime import bounded_history
from backend.workspace import Workspace
from conftest import ROOT, settle


PNG = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jRZkAAAAASUVORK5CYII=')
IMAGE = {"name": "截图.png", "dataUrl": "data:image/png;base64," + base64.b64encode(PNG).decode()}


def output_call(name, args, call_id):
    return {"type": "function_call", "id": "fc_" + call_id, "call_id": call_id, "name": name, "arguments": json.dumps(args), "status": "completed"}


@pytest.mark.parametrize('images', ["bad", [{}], [IMAGE] * 5,
    [{"dataUrl": "https://example.com/image.png"}], [{"dataUrl": "data:image/svg+xml;base64,PHN2Zz4="}],
    [{"dataUrl": "data:image/png;base64,abcd"}], [{"dataUrl": "data:image/jpeg;base64," + base64.b64encode(PNG).decode()}],
    [{"dataUrl": "data:image/png;base64," + "a" * (7 * 1024 * 1024)}]])
def test_reject_invalid_images(images):
    with pytest.raises(AppError):
        validate_images(images)


async def test_images_use_each_protocol():
    messages = [{"role": "user", "content": [{"type": "text", "text": "分析图片"}, {"type": "image_url", "image_url": {"url": IMAGE["dataUrl"]}}]}]
    for protocol in ("compatible", "responses", "anthropic"):
        async def handler(request):
            body = json.loads(request.content)
            if protocol == "responses":
                assert str(request.url).endswith('/responses')
                assert body['input'][0]['content'][1] == {"type": "input_image", "image_url": IMAGE['dataUrl']}
                assert all(t['type'] == 'function' and t['name'] and t['strict'] is False for t in body['tools'])
                assert body['store'] is False and body['include'] == ['reasoning.encrypted_content']
                return httpx.Response(200, json={"output": [{"type": "message", "role": "assistant", "content": [{"type": "output_text", "text": "图片已读取"}]}]})
            content = body['messages'][0]['content']
            if protocol == 'anthropic':
                assert content[1]['source'] == {"type": "base64", "media_type": "image/png", "data": IMAGE['dataUrl'].split(',')[1]}
                return httpx.Response(200, json={"content": [{"type": "text", "text": "图片已读取"}]})
            assert content == messages[0]['content']
            return httpx.Response(200, json={"choices": [{"message": {"content": "图片已读取"}}]})
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            answer = await call_model({"protocol": protocol, "baseUrl": "https://example.com/v1", "model": "fixture"}, messages, client=client)
            assert answer['content'] == '图片已读取'


@pytest.mark.parametrize('response', [
    {"status": "incomplete", "output": [output_call('list_files', {}, 'one')]},
    {"status": "failed", "error": {"code": "server_error"}, "output": []},
    {"output": []}, {"output": [output_call('list_files', {}, '')]},
    {"choices": [{"message": {"content": "wrong protocol"}}]},
])
async def test_responses_rejects_invalid_or_incomplete_output(response):
    async with httpx.AsyncClient(transport=httpx.MockTransport(lambda request: httpx.Response(200, json=response))) as client:
        with pytest.raises(AppError, match='无效响应'):
            await call_model({"protocol": "responses", "baseUrl": "https://example.com/v1", "model": "fixture"}, [], client=client)


async def test_responses_images_tools_restart_and_compaction(workspace, live_server):
    w, _, provider, session = workspace
    _, origin = live_server
    provider = w.save_provider({**provider, 'protocol': 'responses'})
    reasoning = {'type': 'reasoning', 'id': 'rs_one', 'summary': [], 'encrypted_content': 'opaque-reasoning'}
    steps = [('update_plan', {'summary': '分析截图与源码', 'criteria': '给出证据', 'next_action': '读取入口'}),
             ('read_file', {'path': 'app.mjs'}),
             ('request_user', {'question': '请补充截图', 'reason': '确认预期', 'summary': '已读取源码'})]
    requests = []
    async def handler(request):
        body = json.loads(request.content)
        requests.append(body)
        if len(requests) > 1:
            assert reasoning in body['input']
            assert any(item.get('type') == 'function_call_output' and item['call_id'] == 'one' for item in body['input'])
        name, args = steps.pop(0)
        call_id = 'one' if len(requests) == 1 else 'call_' + str(len(requests))
        output = ([reasoning] if len(requests) == 1 else []) + [output_call(name, args, call_id)]
        return httpx.Response(200, json={"status": "completed", "output": output, "usage": {"input_tokens": 10, "output_tokens": 3}})
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as model, httpx.AsyncClient(base_url=origin, trust_env=False) as api:
        w.model_client = model
        # This payload exceeds the old 1 MB JSON limit, but is a valid image message.
        large = {**IMAGE, 'dataUrl': 'data:image/png;base64,' + base64.b64encode(PNG + b'\0' * 800001).decode()}
        result = await api.post(f'/api/dev/sessions/{session["id"]}/run', json={'providerId': provider['id'], 'message': '审查图片', 'kind': 'inspect', 'images': [large]})
        assert result.status_code == 200, result.text
        await settle(w)
        assert session['status'] == 'awaiting_user'
        assert session['task']['metrics']['inputTokens'] == 30
        metadata = session['messages'][0]['images'][0]
        image_response = await api.get(f'/api/dev/sessions/{session["id"]}/images/{metadata["id"]}')
        assert image_response.status_code == 200 and image_response.content.startswith(PNG)
        assert image_response.headers['cache-control'] == 'no-store'
        assert (await api.get(f'/api/dev/sessions/{session["id"]}/images/not-found')).status_code == 404
        other = w.create_session({'projectId': session['projectId']})
        assert (await api.get(f'/api/dev/sessions/{other["id"]}/images/{metadata["id"]}')).status_code == 404
        assert 'data:image' not in (w.data_dir / 'workspace.json').read_text(encoding='utf-8')
        assert 'data:image' not in json.dumps(w.public_session(session))
        task_id = session['task']['id']
        loaded = Workspace(w.data_dir, model_client=model,
                           intent_classifier=lambda _: {"type": "development"})
        restored = loaded.session(session['id'])
        steps.append(('finish_task', {'summary': '已分析', 'evidence': 'app.mjs:1 为减法；已结合两张截图进行静态审查'}))
        await loaded.resume_run(session['id'], {'feedback': '', 'images': [IMAGE]})
        await settle(loaded)
        assert restored['status'] == 'completed' and restored['task']['id'] == task_id
        content = [item for item in requests[-1]['input'] if item.get('role') == 'user' and isinstance(item.get('content'), list)]
        assert len(content) == 2 and all(item['content'][-1]['type'] == 'input_image' for item in content)
        history = restored['history'] + [{'role': 'user', 'content': 'latest'}]
        compacted = bounded_history(history, max_chars=20)
        assert len([message for message in compacted if message.get('images')]) == 2
        hydrated = loaded.model_history(compacted)
        assert hydrated[0]['content'][-1]['image_url']['url'].startswith('data:image/png;base64,')
        await loaded.shutdown()


async def test_image_composer_and_dynamic_height(workspace, live_server):
    w, project, provider, session = workspace
    _, origin = live_server
    provider = w.save_provider({**provider, 'protocol': 'responses'})
    steps = [('request_user', {'question': '请补充图片', 'reason': '确认预期', 'summary': '等待补充'})]
    requests = []
    async def handler(request):
        requests.append(json.loads(request.content))
        name, args = steps.pop(0)
        return httpx.Response(200, json={'output': [output_call(name, args, 'call_' + str(len(requests)))]})
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as model, async_playwright() as playwright:
        w.model_client = model
        browser = await playwright.chromium.launch(channel='msedge', headless=True)
        try:
            page = await browser.new_page(viewport={'width': 1440, 'height': 1000})
            errors = []
            page.on('pageerror', lambda error: errors.append(str(error)))
            await page.route('https://images.unsplash.com/**', lambda route: route.abort())
            await page.goto(origin)
            await page.locator(f'[data-project-id="{project["id"]}"]').click()
            await page.wait_for_function("document.querySelector('#devModelLabel').textContent==='fixture'")
            prompt = page.locator('#devPrompt')
            initial = (await prompt.bounding_box())['height']
            await prompt.fill('\n'.join(['内容'] * 10))
            expanded = (await prompt.bounding_box())['height']
            assert expanded > initial
            await prompt.fill('\n'.join(['内容'] * 80))
            assert (await prompt.bounding_box())['height'] <= 320
            assert await prompt.evaluate("el=>el.scrollHeight>el.clientHeight && getComputedStyle(el).overflowY==='auto'")
            await prompt.fill('')
            assert (await prompt.bounding_box())['height'] == initial
            async def paste_image(name='paste.png'):
                encoded = base64.b64encode(PNG).decode()
                await prompt.evaluate("""(el, args) => {const bytes=Uint8Array.from(atob(args.encoded),c=>c.charCodeAt(0));const data=new DataTransfer();data.items.add(new File([bytes],args.name,{type:'image/png'}));el.dispatchEvent(new ClipboardEvent('paste',{clipboardData:data,bubbles:true,cancelable:true}));}""", {'encoded': encoded, 'name': name})
            await paste_image('截图.png')
            await page.locator('#devImageDrafts img').wait_for()
            assert await page.locator('#devSendButton').is_enabled()
            await page.locator('[data-remove-image]').click()
            assert not await page.locator('#devImageDrafts').is_visible()
            # Exercise real clipboard file handling without requiring OS clipboard permissions.
            await prompt.evaluate("""(el, encoded) => {const bytes=Uint8Array.from(atob(encoded),c=>c.charCodeAt(0));const data=new DataTransfer();data.items.add(new File([bytes],'paste.png',{type:'image/png'}));el.dispatchEvent(new ClipboardEvent('paste',{clipboardData:data,bubbles:true,cancelable:true}));}""", base64.b64encode(PNG).decode())
            await page.locator('#devImageDrafts img').wait_for()
            await page.route('**/api/dev/sessions/*/run', lambda route: route.fulfill(status=400, content_type='application/json', body='{"error":"fixture rejection"}'))
            await prompt.fill('审查截图')
            await page.locator('#devSendButton').click()
            await page.wait_for_function("document.querySelector('#devError').textContent==='fixture rejection'")
            assert await prompt.input_value() == '审查截图'
            assert await page.locator('#devImageDrafts img').count() == 1
            await page.unroute('**/api/dev/sessions/*/run')
            await page.locator('#devSendButton').click()
            await page.wait_for_function("document.querySelector('#devAgentStatus').textContent==='等待用户回答'")
            assert await prompt.input_value() == ''
            assert not await page.locator('#devImageDrafts').is_visible()
            await page.locator('.dev-message-images img').wait_for()
            assert await page.locator('.dev-message-images img').evaluate('el=>el.complete && el.naturalWidth>0')
            await page.reload()
            await page.locator('.dev-message-images img').wait_for()
            await expect(page.locator('#devConfirmationDialog')).to_be_visible()
            await page.locator('#devConfirmationLater').click()
            await page.locator('[data-view-image]').click()
            assert await page.locator('#devImageViewer').is_visible()
            await page.keyboard.press('Escape')
            assert not await page.locator('#devImageViewer').is_visible()
            await paste_image()
            await page.locator('#devImageDrafts img').wait_for()
            steps.append(('request_user', {'question': '已收到补充图', 'reason': '确认下一步', 'summary': '图片已保留'}))
            await page.locator('#devSendButton').click()
            await page.wait_for_function("document.querySelector('#devConversation').textContent.includes('已收到补充图')")
            assert len(session['messages'][-2]['images']) == 1
            output = ROOT / '.local/composer-check'
            output.mkdir(parents=True, exist_ok=True)
            await page.screenshot(path=str(output / 'images-responses.png'))
            assert not errors
            assert len(requests) == 2
        finally:
            await browser.close()
