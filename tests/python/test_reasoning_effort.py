import asyncio
import copy
import json

import httpx
import pytest
from playwright.async_api import async_playwright, expect

from backend.common import AppError
from backend.model import call_model
from backend.workspace import Workspace
from conftest import ROOT, settle, tool_call


@pytest.mark.parametrize('protocol', ['compatible', 'responses'])
@pytest.mark.parametrize('effort', ['default', 'none', 'minimal', 'low', 'medium', 'high', 'xhigh'])
async def test_openai_reasoning_request(protocol, effort):
    async def handler(request):
        body = json.loads(request.content)
        if effort == 'default':
            assert 'reasoning' not in body and 'reasoning_effort' not in body
        elif protocol == 'responses':
            assert body['reasoning'] == {'effort': effort}
            assert 'reasoning_effort' not in body
        else:
            assert body['reasoning_effort'] == effort and 'reasoning' not in body
        return httpx.Response(200, json={'choices': [{'message': {'content': 'ok'}}],
            'output': [{'type': 'message', 'content': [{'type': 'output_text', 'text': 'ok'}]}]})
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        answer = await call_model({'protocol': protocol, 'model': 'custom-model', 'baseUrl': 'https://example.com/v1',
            'reasoningEffort': effort}, [{'role': 'user', 'content': 'hello'}], client=client)
        assert answer['content'] == 'ok'


async def test_responses_official_endpoint_uses_standard_reasoning_field():
    async def handler(request):
        body = json.loads(request.content)
        assert body['reasoning'] == {'effort': 'high'}
        assert 'reasoning_effort' not in body
        return httpx.Response(200, json={'output': [{'type': 'message', 'content': [{'type': 'output_text', 'text': 'ok'}]}]})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        answer = await call_model({'protocol': 'responses', 'model': 'gpt-6.1-sol', 'baseUrl': 'https://api.openai.com/v1',
            'apiKey': 'fixture', 'reasoningEffort': 'high'}, [{'role': 'user', 'content': 'hello'}], client=client)
        assert answer['content'] == 'ok'


async def test_intent_classifier_preserves_selected_reasoning_effort(tmp_path):
    requests = []

    async def handler(request):
        requests.append(json.loads(request.content))
        return httpx.Response(200, json={'output': [{'type': 'message', 'content': [
            {'type': 'output_text', 'text': '{"type":"chat","reply":"你好"}'}]}]})

    provider = {'protocol': 'responses', 'model': 'gpt-6.1-sol', 'baseUrl': 'https://relay.example/v1',
                'reasoningEffort': 'high'}
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        workspace = Workspace(tmp_path / 'data', model_client=client)
        try:
            result = await workspace.classify_intent(provider, {'role': 'user', 'content': '你好'}, asyncio.Event())
        finally:
            await workspace.shutdown()
        assert result['type'] == 'chat'
        assert requests[0]['reasoning'] == {'effort': 'high'}
        assert 'reasoning_effort' not in requests[0]


async def test_responses_tools_do_not_receive_chat_completions_reasoning_alias():
    async def handler(request):
        body = json.loads(request.content)
        assert body['tools']
        assert body['reasoning'] == {'effort': 'high'}
        assert 'reasoning_effort' not in body
        return httpx.Response(200, json={'output': [{'type': 'message', 'content': [{'type': 'output_text', 'text': 'ok'}]}]})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        answer = await call_model({'protocol': 'responses', 'model': 'gpt-6.1-sol', 'baseUrl': 'https://codekey.ai',
            'reasoningEffort': 'high'}, [{'role': 'user', 'content': 'inspect'}], client=client)
        assert answer['content'] == 'ok'


@pytest.mark.parametrize('model,effort,thinking,output_config', [
    ('claude-opus-4-6', 'max', {'type': 'adaptive'}, {'effort': 'max'}),
    ('claude-sonnet-4-6', 'low', {'type': 'adaptive'}, {'effort': 'low'}),
    ('claude-opus-4-5-20251101', 'high', {'type': 'enabled', 'budget_tokens': 8192}, None),
    ('claude-sonnet-4-20250514', 'medium', {'type': 'enabled', 'budget_tokens': 4096}, None),
    ('custom-claude', 'low', {'type': 'enabled', 'budget_tokens': 1024}, None),
    ('claude-opus-4-6', 'none', {'type': 'disabled'}, None),
    ('claude-opus-4-6', 'default', None, None),
])
async def test_anthropic_reasoning_and_signed_tool_history(model, effort, thinking, output_config):
    content = [{'type': 'thinking', 'thinking': 'private thought', 'signature': 'opaque-signature'},
               {'type': 'redacted_thinking', 'data': 'opaque-redacted'},
               {'type': 'tool_use', 'id': 'call-one', 'name': 'list_files', 'input': {}}]
    requests = []

    async def handler(request):
        body = json.loads(request.content)
        requests.append(body)
        assert body.get('thinking') == thinking and body.get('output_config') == output_config
        assert 'reasoning_effort' not in body and 'reasoning' not in body
        if thinking and thinking['type'] == 'enabled':
            assert body['max_tokens'] == 8192 + thinking['budget_tokens']
        if len(requests) == 2:
            assert body['messages'][1]['content'] == content
            assert body['messages'][2]['content'][0]['tool_use_id'] == 'call-one'
            return httpx.Response(200, json={'content': [{'type': 'text', 'text': 'done'}]})
        return httpx.Response(200, json={'content': content})

    provider = {'protocol': 'anthropic', 'model': model, 'baseUrl': 'https://example.com/v1', 'reasoningEffort': effort}
    history = [{'role': 'user', 'content': 'inspect'}]
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        answer = await call_model(provider, history, client=client)
        # Persistence must keep opaque signatures and redacted blocks on continuation.
        history += [json.loads(json.dumps(answer)), {'role': 'tool', 'tool_call_id': 'call-one', 'content': '{}'}]
        assert (await call_model(provider, history, client=client))['content'] == 'done'


async def test_reasoning_persistence_validation_and_task_snapshot(workspace):
    w, project, provider, session = workspace
    record = w.find(w.data['providers'], provider['id'], '模型配置')
    original_secret = record['secret']
    w.save_reasoning_effort(record, {'reasoningEffort': 'high'})
    # Editing an existing model with an old client must retain its effort and key.
    legacy_edit = {key: value for key, value in provider.items() if key != 'reasoningEffort'}
    w.save_provider({**legacy_edit, 'name': 'renamed', 'apiKey': ''})
    assert record['reasoningEffort'] == 'high' and record['secret'] == original_secret
    before = copy.deepcopy(session)
    for invalid in ['ultra', '', None, {}, ['high']]:
        with pytest.raises(AppError):
            await w.start_run(session['id'], {'providerId': provider['id'], 'message': '检查项目', 'reasoningEffort': invalid})
        assert session == before
    requests = []

    async def handler(request):
        requests.append(json.loads(request.content))
        return httpx.Response(200, json={'choices': [{'message': {'tool_calls': [tool_call('request_user',
            {'question': '下一步？', 'reason': '确认范围', 'summary': '等待反馈'})]}}]})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        w.model_client = client
        await w.start_run(session['id'], {'providerId': provider['id'], 'message': '检查项目'})
        await settle(w)
        task_id = session['task']['id']
        assert session['task']['reasoningEffort'] == 'high'
        w.save_reasoning_effort(record, {'reasoningEffort': 'low'})
        restored = Workspace(w.data_dir, model_client=client, intent_classifier=lambda message: {'type': 'development'})
        try:
            assert restored.state()['providers'][0]['reasoningEffort'] == 'low'
            await restored.resume_run(session['id'], {'feedback': '继续', 'reasoningEffort': 'low'})
            await settle(restored)
            assert restored.session(session['id'])['task']['id'] == task_id
            assert [r['reasoning_effort'] for r in requests] == ['high', 'high']
            # A new task gets the new preference, while old tasks keep their snapshot.
            await restored.start_run(session['id'], {'providerId': provider['id'], 'message': '重新检查入口'})
            await settle(restored)
            assert requests[-1]['reasoning_effort'] == 'low'
        finally:
            await restored.shutdown()


async def test_reasoning_save_failure_rolls_back(workspace, monkeypatch):
    w, _, provider, _ = workspace
    record = w.find(w.data['providers'], provider['id'], '模型配置')
    before = copy.deepcopy(record)

    def fail():
        raise OSError('disk full')

    monkeypatch.setattr(w, 'save', fail)
    with pytest.raises(OSError):
        w.save_reasoning_effort(record, {'reasoningEffort': 'high'})
    assert record == before


@pytest.mark.parametrize('running_protocol', ['compatible', 'anthropic'])
async def test_reasoning_menu_persistence_protocols_and_real_request(workspace, live_server, running_protocol):
    w, project, provider, session = workspace
    _, origin = live_server
    claude = w.save_provider({'name': 'Claude', 'model': 'claude-opus-4-6', 'protocol': 'anthropic',
        'baseUrl': 'https://example.com/v1', 'apiKey': 'fixture'})
    requests = []

    async def handler(request):
        requests.append(json.loads(request.content))
        if running_protocol == 'anthropic':
            return httpx.Response(200, json={'content': [{'type': 'tool_use', 'id': 'ask-one', 'name': 'request_user',
                'input': {'question': '下一步？', 'reason': '确认范围', 'summary': '等待反馈'}}]})
        return httpx.Response(200, json={'choices': [{'message': {'tool_calls': [tool_call('request_user',
            {'question': '下一步？', 'reason': '确认范围', 'summary': '等待反馈'})]}}]})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client, async_playwright() as playwright:
        w.model_client = client
        browser = await playwright.chromium.launch(channel='msedge', headless=True)
        try:
            page = await browser.new_page(viewport={'width': 1440, 'height': 1000})
            await page.route('https://images.unsplash.com/**', lambda route: route.abort())
            await page.goto(origin)
            await page.locator(f'[data-project-id="{project["id"]}"]').click()
            await page.locator('#devModelPicker > summary').click()
            await expect(page.locator('#devReasoningSelect')).to_be_enabled()
            await page.locator('#devReasoningSelect').select_option('high')
            await expect(page.locator('#devReasoningHint')).to_contain_text('自动保存')
            await expect(page.locator('#devModelLabel')).to_have_text('fixture · 高')
            await page.reload()
            await page.locator('#devModelPicker > summary').click()
            await expect(page.locator('#devReasoningSelect')).to_have_value('high')
            output = ROOT / '.local/python-check'
            output.mkdir(parents=True, exist_ok=True)
            await page.screenshot(path=str(output / 'reasoning-desktop.png'))
            await page.set_viewport_size({'width': 390, 'height': 844})
            box = await page.locator('#devModelOptions').bounding_box()
            assert box['x'] >= 0 and box['x'] + box['width'] <= 390
            await page.screenshot(path=str(output / 'reasoning-mobile.png'))
            await page.set_viewport_size({'width': 1440, 'height': 1000})
            await page.locator('#devModelSelect').select_option(claude['id'])
            await page.locator('#devModelPicker > summary').click()
            assert await page.locator('#devReasoningSelect option[value="max"]').count() == 1
            assert await page.locator('#devReasoningSelect option[value="xhigh"]').count() == 0
            await page.locator('#devReasoningSelect').select_option('max')
            await expect(page.locator('#devReasoningHint')).to_contain_text('自动保存')
            await page.locator('#devModelSelect').select_option(provider['id'])
            await page.locator('#devModelPicker > summary').click()
            await expect(page.locator('#devReasoningSelect')).to_have_value('high')
            if running_protocol == 'anthropic':
                await page.locator('#devModelSelect').select_option(claude['id'])
                await page.locator('#devModelPicker > summary').click()
                await expect(page.locator('#devReasoningSelect')).to_have_value('max')
            await page.locator('#devPrompt').fill('检查项目')
            await page.locator('#devSendButton').click()
            await page.wait_for_function("document.querySelector('#devAgentStatus').textContent==='等待用户回答'")
            await expect(page.locator('#devConfirmationDialog')).to_be_visible()
            await page.locator('#devConfirmationLater').click()
            await page.locator('#devModelPicker > summary').click()
            await expect(page.locator('#devReasoningSelect')).to_be_disabled()
            await expect(page.locator('#devReasoningHint')).to_contain_text('沿用启动时')
            if running_protocol == 'anthropic':
                assert requests[0]['thinking'] == {'type': 'adaptive'}
                assert requests[0]['output_config'] == {'effort': 'max'}
                assert session['task']['reasoningEffort'] == 'max'
            else:
                assert requests[0]['reasoning_effort'] == 'high'
                assert session['task']['reasoningEffort'] == 'high'
        finally:
            await browser.close()


async def test_reasoning_menu_failed_save_and_pending_send(workspace, live_server):
    w, project, provider, _ = workspace
    _, origin = live_server
    release = asyncio.Event()
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(channel='msedge', headless=True)
        try:
            page = await browser.new_page(viewport={'width': 1440, 'height': 1000})
            await page.route('https://images.unsplash.com/**', lambda route: route.abort())
            await page.goto(origin)
            await page.locator(f'[data-project-id="{project["id"]}"]').click()

            async def fail(route):
                await release.wait()
                await route.fulfill(status=500, content_type='application/json', body='{"error":"保存失败"}')

            await page.route('**/providers/*/reasoning', fail)
            await page.locator('#devPrompt').fill('检查项目')
            await page.locator('#devModelPicker > summary').click()
            await page.locator('#devReasoningSelect').select_option('high')
            await expect(page.locator('#devReasoningHint')).to_have_text('正在保存…')
            await expect(page.locator('#devSendButton')).to_be_disabled()
            await page.locator('#devPrompt').press('Enter')
            assert not w.runs
            release.set()
            await expect(page.locator('#devReasoningSelect')).to_have_value('default')
            await expect(page.locator('#devError')).to_contain_text('推理强度保存失败')
            await expect(page.locator('#devPrompt')).to_have_value('检查项目')
            await expect(page.locator('#devSendButton')).to_be_enabled()
        finally:
            release.set()
            await browser.close()
