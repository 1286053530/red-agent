"""Model-driven selection, bounded resources, provenance and permission boundaries."""
import hashlib
import json
import asyncio

import httpx
import pytest

from backend.skill_catalog import SkillCatalog, task_skill_context
from conftest import ROOT, prepare, settle, tool_call


def test_bundled_upstream_pages_reconstruct_verified_sources():
    catalog = SkillCatalog()
    sources = json.loads((ROOT / 'backend/skills/sources.json').read_text(encoding='utf-8'))
    assert len(catalog.list()) == 11 and len(sources) == 10
    for entry in sources:
        snapshot = catalog.snapshot(entry['id'])
        assert snapshot['metadata']['upstreamCommit'] == entry['commit']
        assert len(entry['commit']) == 40
        for resource in entry['resources']:
            text = ''.join(snapshot['resources'][path] for path in resource['pages'])
            assert hashlib.sha256(text.encode()).hexdigest() == resource['sha256']
        folder = ROOT / 'backend/skills' / entry['id']
        assert any(p.name.startswith('LICENSE') for p in folder.iterdir())


@pytest.mark.parametrize('choice', ['humanizer', 'impeccable', 'graphify', 'none', '../../project', [], {'id': 'humanizer'}])
async def test_auto_selection_uses_only_the_chosen_entry_after_classification(workspace, choice):
    w, _, provider, session = workspace
    w.intent_classifier = None
    calls = []

    async def handler(request):
        body = json.loads(request.content)
        calls.append(body)
        if len(calls) == 1:
            prompt = body['messages'][0]['content']
            for entry in w.skills.list():
                assert entry['id'] in prompt and entry['description'] in prompt
                assert w.skills.snapshot(entry['id'])['content'] not in prompt
            assert 'tools' not in body
            payload = {'type': 'development', 'kind': 'inspect', 'skillId': choice, 'tasks': ['核对项目']}
            return httpx.Response(200, json={'choices': [{'message': {'content': json.dumps(payload)}}]})
        return httpx.Response(200, json={'choices': [{'message': {'tool_calls': [tool_call('fail_task', {
            'reason': '结束模拟任务', 'evidence': '已核对实际发送上下文'})]}}]})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        w.model_client = client
        await prepare(w, provider, session, message='按对话要求核对项目', kind='inspect')
    expected = choice if isinstance(choice, str) and choice in w.skills.entries else None
    assert len(calls) == 2 and not session['changes'] and not session['commands']
    prompt = calls[1]['messages'][0]['content']
    for entry in w.skills.list():
        assert (w.skills.snapshot(entry['id'])['content'] in prompt) == (entry['id'] == expected)
    assert session['task'].get('skill', {}).get('id') == expected


async def test_selected_writing_skill_changes_chat_response_without_project_tools(workspace):
    w, _, provider, session = workspace
    w.intent_classifier = None
    calls = []

    async def handler(request):
        body = json.loads(request.content)
        calls.append(body)
        assert 'tools' not in body
        if len(calls) == 1:
            payload = {'type': 'chat', 'skillId': 'humanizer', 'reply': '内部分类草稿'}
            content = json.dumps(payload)
        else:
            prompt = body['messages'][0]['content']
            snapshot = w.skills.snapshot('humanizer')
            assert snapshot['content'] in prompt
            assert all(snapshot['resources'][path] in prompt for path in snapshot['metadata']['chatResources'])
            assert '改写' in str(body['messages'])
            content = '我们已完成升级，页面加载更快了。'
        return httpx.Response(200, json={'choices': [{'message': {'content': content}}],
                                      'usage': {'prompt_tokens': 10, 'completion_tokens': 5}})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        w.model_client = client
        await prepare(w, provider, session, message='改写这段文案，去掉 AI 腔：我们致力于赋能卓越体验。')
    assert session['status'] == 'completed', session['error']
    assert session['task']['kind'] == 'chat' and session['task']['skill']['id'] == 'humanizer'
    assert session['task']['metrics']['inputTokens'] == 20
    assert session['task']['metrics']['outputTokens'] == 10
    assert [m['content'] for m in session['messages'] if m['role'] == 'assistant'] == ['我们已完成升级，页面加载更快了。']
    assert not session['changes'] and not session['commands'] and not session['observations']


@pytest.mark.parametrize('mode,expected', [('humanizer', 'humanizer'), ('none', None), ('auto', 'impeccable')])
async def test_manual_selection_and_opt_out_override_model(workspace, mode, expected):
    w, _, provider, session = workspace
    w.intent_classifier = lambda _: {'type': 'development', 'skillId': 'impeccable'}
    await prepare(w, provider, session, skillId=mode)
    assert session['task'].get('skill', {}).get('id') == expected


async def test_supplements_can_change_automatic_skill_but_not_task_permissions(workspace):
    w, _, provider, session = workspace
    w.intent_classifier = lambda _: {'type': 'development', 'kind': 'inspect', 'skillId': 'graphify'}
    await prepare(w, provider, session, kind='inspect')
    permissions = session['task']['permissions'].copy()
    w.intent_classifier = lambda _: {'type': 'development', 'kind': 'change', 'skillId': 'ponytail'}
    await w.route_user_message(session, provider, {'role': 'user', 'content': '用最少代码修复'},
                               asyncio.Event(), 'supplement')
    assert session['task']['skill']['id'] == 'ponytail'
    assert session['task']['permissions'] == permissions == {'edits': False, 'commands': False}
    assert session['task']['kind'] == 'inspect'
    w.intent_classifier = lambda _: {'type': 'development', 'skillId': 'none'}
    await w.route_user_message(session, provider, {'role': 'user', 'content': '关闭技能'},
                               asyncio.Event(), 'supplement')
    assert task_skill_context(session['task']) == ''


async def test_references_are_bounded_and_remain_rereadable(workspace):
    w, _, provider, session = workspace
    await prepare(w, provider, session, skillId='ui-ux-pro-max', kind='inspect')
    paths = [p for p in session['task']['_skillSnapshot']['resources'] if 'styles' in p]
    assert len(paths) > 6
    for path in paths:
        await w.execute(session, 'read_skill_resource', {'path': path})
    task = session['task']
    assert sum(len(task['_skillSnapshot']['resources'][p]) for p in task['skill']['loadedResources']) <= 48000
    assert paths[0] not in task['skill']['loadedResources']
    result = await w.execute(session, 'read_skill_resource', {'path': paths[0]})
    assert result['content'] == task['_skillSnapshot']['resources'][paths[0]]
    assert paths[0] in task['skill']['loadedResources']


async def test_router_uses_recent_conversation_to_resolve_followup(workspace):
    w, _, provider, session = workspace
    w.intent_classifier = None
    session['messages'] = [{'role': 'user', 'content': '请把宣传文案改得自然一些'},
                           {'role': 'assistant', 'content': '请提供原文。'}]
    calls = []

    async def handler(request):
        body = json.loads(request.content)
        calls.append(body)
        return httpx.Response(200, json={'choices': [{'message': {'content': json.dumps({
            'type': 'chat', 'skillId': 'none', 'reply': '收到这段文字。'})}}]})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        w.model_client = client
        await prepare(w, provider, session, message='就是这一段')
    assert '请把宣传文案改得自然一些' in calls[0]['messages'][0]['content']
    assert '请提供原文。' in calls[0]['messages'][0]['content']
    assert 'skill' not in session['task']


async def test_writing_failure_retries_original_skill_reply_without_project_tools(workspace):
    w, _, provider, session = workspace
    w.intent_classifier = lambda _: {'type': 'chat', 'skillId': 'humanizer', 'reply': '分类草稿'}
    requests = []

    async def handler(request):
        body = json.loads(request.content)
        requests.append(body)
        assert 'tools' not in body and 'Humanizer 自然表达' in body['messages'][0]['content']
        if len(requests) == 1:
            return httpx.Response(400, json={'error': {'message': 'fixture failure'}})
        return httpx.Response(200, json={'choices': [{'message': {'content': '完成自然改写。'}}]})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        w.model_client = client
        await prepare(w, provider, session, message='改写这段文字')
        assert session['status'] == 'failed'
        assert not session['task'].get('classificationComplete')
        assert session['history'][0]['content'] == '改写这段文字'
        task_id = session['task']['id']
        await w.resume_run(session['id'], {'feedback': '继续'})
        await settle(w)
    assert session['status'] == 'completed', session['error']
    assert session['task']['id'] == task_id and session['task']['kind'] == 'chat'
    assert session['messages'][-1]['content'] == '完成自然改写。'
    assert len(requests) == 2 and not session['changes'] and not session['commands']


async def test_requirement_during_writing_is_not_lost_on_chat_completion(workspace):
    w, _, provider, session = workspace
    w.intent_classifier = lambda message: ({'type': 'development', 'kind': 'inspect', 'skillId': 'none'}
                                           if '改为' in message['content'] else
                                           {'type': 'chat', 'skillId': 'humanizer', 'reply': '分类草稿'})
    entered, release = asyncio.Event(), asyncio.Event()
    calls = []

    async def handler(request):
        body = json.loads(request.content)
        calls.append(body)
        if len(calls) == 1:
            entered.set()
            await release.wait()
            return httpx.Response(200, json={'choices': [{'message': {'content': '过期的旧改写'}}]})
        assert '改为只读审查项目' in str(body['messages'])
        return httpx.Response(200, json={'choices': [{'message': {'tool_calls': [tool_call('request_user', {
            'question': '需要审查哪个页面？', 'reason': '新要求未指定页面'})]}}]})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        w.model_client = client
        await w.start_run(session['id'], {'providerId': provider['id'], 'message': '自然改写这段话'})
        await asyncio.wait_for(entered.wait(), 5)
        w.supplement_run(session['id'], {'taskId': session['task']['id'], 'message': '改为只读审查项目'})
        release.set()
        await settle(w)
    assert session['status'] == 'awaiting_user', session['error']
    assert session['task']['supplements'][0]['status'] == 'included'
    assert not any('过期的旧改写' in message['content'] for message in session['messages'])
    assert len(calls) == 2 and not session['changes'] and not session['commands']
