import json
from pathlib import Path

import httpx
import pytest
from playwright.async_api import async_playwright

from backend.common import AppError
from backend.workspace import Workspace
from conftest import ROOT, settle, tool_call
from conftest import prepare


PLAN = {"summary": "审查加法", "criteria": "提供源码证据", "next_action": "阅读入口"}
FINISH = {"summary": "app.mjs:1 使用了减法", "evidence": "已读取 a-b；静态审查未运行代码"}


async def run_steps(w, provider, session, steps):
    requests = []
    async def handler(request):
        requests.append(json.loads(request.content))
        name, args = steps.pop(0)
        return httpx.Response(200, json={"choices": [{"message": {"tool_calls": [tool_call(name, args)]}}]})
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        w.model_client = client
        await w.start_run(session["id"], {"providerId": provider["id"], "message": "审查代码"})
        await settle(w)
    return requests


async def test_tool_error_changes_strategy_and_finishes(workspace):
    w, _, provider, session = workspace
    requests = await run_steps(w, provider, session, [
        ('update_plan', PLAN), ('read_file', {'path': 'missing.py'}),
        ('list_files', {}), ('read_file', {'path': 'app.mjs'}), ('finish_task', FINISH)])
    assert session['status'] == 'completed'
    failure = json.loads(requests[2]['messages'][-1]['content'])
    assert failure['category'] == 'not_found' and 'list_files' in failure['recovery']
    assert 'recovery' in requests[2]['messages'][1]['content']
    assert session['task']['metrics']['toolErrors'] == 1
    assert session['task']['outcome']['code'] == 'static_review'
    await w.stop(session['id'])
    assert session['status'] == 'completed'


async def test_repeated_read_loop_fails_early_and_survives_restart(workspace):
    w, _, provider, session = workspace
    counter = 0
    async def handler(request):
        nonlocal counter
        counter += 1
        # Alternate equivalent default arguments to ensure semantic duplicates are detected.
        args = {'path': 'app.mjs'} if counter % 2 else {'path': 'app.mjs', 'start_line': 1, 'end_line': 200, 'max_chars': 12000}
        return httpx.Response(200, json={'choices': [{'message': {'tool_calls': [tool_call('read_file', args)]}}]})
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        w.model_client = client
        await w.start_run(session['id'], {'providerId': provider['id'], 'message': '审查代码'})
        await settle(w)
    assert session['status'] == 'failed' and counter <= 7
    assert session['task']['outcome']['code'] == 'no_progress'
    assert not session['task'].get('result')
    loaded = Workspace(w.data_dir)
    assert loaded.session(session['id'])['status'] == 'failed'
    assert loaded.session(session['id'])['task']['outcome'] == session['task']['outcome']
    await loaded.shutdown()


async def test_changing_plans_is_not_progress(workspace):
    w, _, provider, session = workspace
    count = 0
    async def handler(request):
        nonlocal count
        count += 1
        return httpx.Response(200, json={'choices': [{'message': {'tool_calls': [tool_call('update_plan', {**PLAN, 'summary': f'仍在分析 {count}'})]}}]})
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        w.model_client = client
        await w.start_run(session['id'], {'providerId': provider['id'], 'message': '审查代码'})
        await settle(w)
    assert session['status'] == 'failed' and count == 10
    assert session['task']['outcome']['code'] == 'no_progress'


async def test_waits_for_answer_then_resumes_same_task(workspace):
    w, _, provider, session = workspace
    await run_steps(w, provider, session, [('request_user', {'question': '只审查加法，还是整个模块？', 'reason': '需要确定用户选择的审查范围', 'summary': '尚未修改文件'})])
    task_id = session['task']['id']
    assert session['status'] == 'awaiting_user' and not session['error']
    assert session['id'] not in w.runs and not session['task'].get('finishedAt')
    with pytest.raises(AppError, match='回答'):
        await w.resume_run(session['id'])
    steps = [('update_plan', PLAN), ('read_file', {'path': 'app.mjs'}), ('finish_task', FINISH)]
    async def handler(request):
        body = json.loads(request.content)
        assert '只审查加法' in str(body['messages'])
        name, args = steps.pop(0)
        return httpx.Response(200, json={'choices': [{'message': {'tool_calls': [tool_call(name, args)]}}]})
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        w.model_client = client
        await w.resume_run(session['id'], {'feedback': '只审查加法'})
        await settle(w)
    assert session['status'] == 'completed' and session['task']['id'] == task_id
    assert session['task']['attempts'][0]['status'] == 'awaiting_user'


async def test_reported_failure_and_manual_retry(workspace):
    w, _, provider, session = workspace
    await run_steps(w, provider, session, [('fail_task', {'reason': '当前执行器不支持所需验证', 'evidence': '只完成静态检查，没有实际测试结果'})])
    assert session['status'] == 'failed' and not session['task'].get('result')
    task_id = session['task']['id']
    async def handler(request):
        return httpx.Response(200, json={'choices': [{'message': {'tool_calls': [tool_call('request_user', {'reason': '需要选择验证方法', 'question': '是否提供现有测试结果？'})]}}]})
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        w.model_client = client
        await w.resume_run(session['id'])
        await settle(w)
    assert session['status'] == 'awaiting_user' and session['task']['id'] == task_id
    assert session['task']['attempts'][0]['code'] == 'reported_failure'


async def test_model_service_error_is_failure_not_user_question(workspace):
    w, _, provider, session = workspace
    async def handler(request):
        return httpx.Response(503, json={'error': 'unavailable'})
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        w.model_client = client
        await w.start_run(session['id'], {'providerId': provider['id'], 'message': '审查代码'})
        await settle(w)
    assert session['status'] == 'failed'
    assert session['task']['outcome']['code'] == 'model_error'
    assert '503' in session['error'] and not session['task']['outcome'].get('question')


async def test_external_file_change_invalidates_duplicate_read_guard(workspace):
    w, project, provider, session = workspace
    count = 0
    async def handler(request):
        nonlocal count
        count += 1
        if count == 3:
            (Path(project['path']) / 'app.mjs').write_bytes(b'export const add=(a,b)=>a+b;\n')
        name, args = ('read_file', {'path': 'app.mjs'}) if count <= 3 else ('fail_task', {'reason': '范围已检查', 'evidence': '已看到外部修改的新版本，未执行测试'})
        return httpx.Response(200, json={'choices': [{'message': {'tool_calls': [tool_call(name, args)]}}]})
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        w.model_client = client
        await w.start_run(session['id'], {'providerId': provider['id'], 'message': '审查代码'})
        await settle(w)
    assert all(event['status'] == 'completed' for event in session['events'])


async def test_repeated_batch_is_cut_off_and_history_is_repaired(workspace):
    w, _, provider, session = workspace
    async def handler(request):
        calls = [tool_call('read_file', {'path': 'missing.py'}) for _ in range(30)]
        return httpx.Response(200, json={'choices': [{'message': {'tool_calls': calls}}]})
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        w.model_client = client
        await w.start_run(session['id'], {'providerId': provider['id'], 'message': '审查代码'})
        await settle(w)
    assert session['status'] == 'failed' and session['task']['calls'] <= 5
    calls = [c['id'] for m in session['history'] for c in m.get('tool_calls', [])]
    results = [m['tool_call_id'] for m in session['history'] if m['role'] == 'tool']
    assert sorted(calls) == sorted(results)


async def test_real_paging_is_progress_and_not_blocked(workspace):
    w, project, provider, session = workspace
    text = 'a' * 150000
    (Path(project['path']) / 'paging.txt').write_bytes(text.encode())
    steps = [('update_plan', PLAN)]
    steps.extend(('read_file', {'path': 'paging.txt', 'offset': offset}) for offset in range(0, len(text), 12000))
    steps.append(('finish_task', {'summary': '已阅读分页文件', 'evidence': 'paging.txt 已完成全部分页；未运行项目代码'}))
    await run_steps(w, provider, session, steps)
    assert session['status'] == 'completed' and session['task']['rounds'] > 10
    assert not session['task']['metrics'].get('toolErrors')


async def test_large_project_search_pagination_is_not_mistaken_for_idle(workspace):
    w, project, provider, session = workspace
    folder = Path(project['path']) / 'many'
    folder.mkdir()
    for index in range(2050):
        (folder / f'{index:04}.txt').write_bytes(b'no matching symbol\n')
    steps = [('update_plan', PLAN), ('read_file', {'path': 'app.mjs'})]
    steps.extend(('search_files', {'query': 'ABSENT_SYMBOL', 'path': 'many', 'file_offset': offset}) for offset in range(0, 2050, 200))
    steps.append(('finish_task', {'summary': '范围内没有找到目标符号', 'evidence': '已逐页搜索 many 目录的 2050 个文件，未执行代码'}))
    await run_steps(w, provider, session, steps)
    assert session['status'] == 'completed', session['error']
    assert not session['task']['metrics'].get('toolErrors')


async def test_failed_command_retries_are_bounded_without_source_change(workspace):
    w, _, provider, session = workspace
    await prepare(w, provider, session, kind='change', permissions={'commands': True})
    args = {'command': 'node', 'args': ['--test', 'app.test.mjs'], 'purpose': '检查加法'}
    first = await w.execute(session, 'run_command', args)
    await settle(w)
    assert first['status'] == 'failed'
    second = await w.execute(session, 'run_command', {**args, 'retry_id': first['id']})
    await settle(w)
    assert second['status'] == 'failed'
    with pytest.raises(AppError, match='失败两次'):
        await w.execute(session, 'run_command', {**args, 'retry_id': second['id'], 'purpose': '换措辞继续检查'})
    assert len(session['commands']) == 2


async def test_waiting_ui_answers_without_creating_new_task(live_server, workspace):
    w, _, provider, session = workspace
    await run_steps(w, provider, session, [('request_user', {'question': '请确定审查范围', 'reason': '存在两个候选模块'})])
    task_id = session['task']['id']
    steps = [('update_plan', PLAN), ('read_file', {'path': 'app.mjs'}), ('finish_task', FINISH)]
    async def handler(request):
        name, args = steps.pop(0)
        return httpx.Response(200, json={'choices': [{'message': {'tool_calls': [tool_call(name, args)]}}]})
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        w.model_client = client
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(channel='msedge', headless=True)
            try:
                page = await browser.new_page(viewport={'width': 1550, 'height': 1000})
                await page.goto(live_server[1])
                await page.locator(f'[data-session-id="{session["id"]}"]').click()
                await page.locator('#devTaskOutcome').wait_for()
                assert '等待用户回答' in await page.locator('#devAgentStatus').inner_text()
                assert await page.locator('#devResumeTask').is_disabled()
                assert not await page.locator('#devError').is_visible()
                await page.fill('#devPrompt', '只看加法')
                output = ROOT / '.local/reliability-check'
                output.mkdir(parents=True, exist_ok=True)
                await page.screenshot(path=str(output / 'waiting-user.png'))
                await page.get_by_role('button', name='回答并继续', exact=True).click()
                await page.wait_for_function("document.querySelector('#devAgentStatus').textContent==='已完成'")
                assert session['task']['id'] == task_id and not session.get('tasks')
                assert await page.locator('#devTaskOutcome').count() == 0
                steps.append(('fail_task', {'reason': '无法完成所需验证', 'evidence': '没有成功的行为测试'}))
                await page.fill('#devPrompt', '审查另一项内容')
                await page.get_by_role('button', name='发送', exact=True).click()
                await page.wait_for_function("document.querySelector('#devAgentStatus').textContent==='失败'")
                assert '没有成功的行为测试' in await page.locator('#devTaskOutcome').inner_text()
                failed_id = session['task']['id']
                await page.screenshot(path=str(output / 'failed.png'))
                steps.append(('request_user', {'reason': '需要范围选择', 'question': '选择哪个模块？'}))
                await page.get_by_role('button', name='重试当前任务', exact=True).click()
                await page.wait_for_function("document.querySelector('#devAgentStatus').textContent==='等待用户回答'")
                assert session['task']['id'] == failed_id
            finally:
                await browser.close()
