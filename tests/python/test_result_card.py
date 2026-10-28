import json
from pathlib import Path

import httpx
import pytest
from playwright.async_api import async_playwright, expect

from conftest import ROOT, settle, tool_call


async def test_completed_result_card_and_history(workspace, live_server):
    w, project, provider, s = workspace
    _, origin = live_server
    steps = [
        ('update_plan', {'summary': '修复加法', 'criteria': '加法行为通过', 'next_action': '读取源码', 'todo': []}),
        ('read_file', {'path': 'app.mjs'}),
        ('run_command', {'command': 'node', 'args': ['--test', 'app.test.mjs'], 'purpose': '先复现加法错误'}),
        ('propose_file', {'path': 'app.mjs', 'content': 'export const add=(a,b)=>a+b;\n', 'reason': '修复加法计算'}),
        ('run_command', {'command': 'node', 'args': ['--test', 'app.test.mjs'], 'purpose': '加法行为回归'}),
        ('review_diff', {}),
        ('finish_task', {'summary': '已修复加法计算\n\n支持负数相加。', 'evidence': 'Node 加法行为测试通过，最终差异已复核。'}),
    ]

    async def handler(request):
        name, args = steps.pop(0)
        return httpx.Response(200, json={'choices': [{'message': {'tool_calls': [tool_call(name, args)]}}]})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        w.model_client = client
        await w.start_run(s['id'], {'providerId': provider['id'], 'message': '修复加法', 'permissions': {'edits': True, 'commands': True}})
        await settle(w)
    assert s['status'] == 'completed', s.get('error')
    assert s['messages'][-1]['type'] == 'task_result'
    assert s['messages'][-1]['taskId'] == s['task']['id']
    first_task = s['task']['id']

    async with async_playwright() as p:
        browser = await p.chromium.launch(channel='msedge', headless=True)
        try:
            page = await browser.new_page(viewport={'width': 1440, 'height': 1100})
            await page.route('https://images.unsplash.com/**', lambda route: route.abort())
            await page.goto(origin)
            await page.locator(f'[data-project-id="{project["id"]}"]').click()
            card = page.locator('[data-result-task]')
            await expect(card).to_have_count(1)
            await expect(card).to_contain_text('Node 加法行为测试通过')
            await expect(card.locator('.dev-result-number')).to_have_text(['1'])
            await expect(card.locator('.dev-result-note')).to_have_text('说明：Node 加法行为测试通过，最终差异已复核。')
            assert await card.evaluate('el => el.lastElementChild.classList.contains("dev-result-note")')
            await expect(card).to_contain_text('1 个文件')
            await expect(card).to_contain_text('app.mjs')
            await expect(card.locator('.dev-result-files-head .dev-result-stats')).to_have_text('+1−1')
            await expect(card.locator('.dev-result-heading, .dev-result-section')).to_have_count(0)
            await expect(card.locator('.dev-result-warning')).to_have_count(0)
            await card.get_by_text('检查记录（2）', exact=True).click()
            await expect(card.locator('pre').last).to_contain_text('pass 1')
            await card.get_by_role('button', name='查看修改').click()
            diff = page.locator('[data-diff-details][open]')
            await expect(diff).to_contain_text('+export const add=(a,b)=>a+b;')
            await card.get_by_role('button', name='撤销 ↶').click()
            await expect(page.locator('[data-change-action="revert"]')).to_be_focused()
            await card.get_by_role('button', name='任务记录').click()
            await expect(page.locator('#devTraceTab')).to_have_attribute('aria-selected', 'true')
            await page.reload()
            await expect(card).to_have_count(1)
            # Legacy completion messages have no marker; recover from exact saved result text.
            s['messages'][-1].pop('type')
            s['messages'][-1].pop('taskId')
            w.save()
            await page.reload()
            await expect(card).to_have_count(1)
            Path(ROOT / '.local/python-check').mkdir(parents=True, exist_ok=True)
            await card.screenshot(path=str(ROOT / '.local/python-check/result-card-desktop.png'))
            await page.set_viewport_size({'width': 390, 'height': 1000})
            await expect(card).to_be_visible()
            assert await card.evaluate('el => el.scrollWidth <= el.clientWidth + 1')
            await card.screenshot(path=str(ROOT / '.local/python-check/result-card-mobile.png'))
            await page.set_viewport_size({'width': 1440, 'height': 1100})
            # A new readonly result is kept distinct from the old change result.
            readonly_steps = [
                ('update_plan', {'summary': '只读分析', 'criteria': '阅读源码', 'next_action': '读取', 'todo': ['请人工确认边界输入']}),
                ('read_file', {'path': 'app.mjs'}),
                ('finish_task', {'summary': '<img src=x onerror=alert(1)>源码分析完成', 'evidence': '已阅读 app.mjs，没有执行代码。', 'cards': [
                    {'title': '项目结构', 'items': ['入口位于 `app.mjs:1`。', '项目使用 Node。']},
                    {'title': '运行步骤', 'items': ['运行 `node --test app.test.mjs` 检查加法。']},
                    {'title': '优先改进', 'items': ['<img src=x onerror=alert(2)>保留边界测试。']},
                    {'title': '分析依据与范围', 'items': ['历史补充依据仍保存在任务数据中。']},
                ]}),
            ]
            async def inspect_handler(request):
                name, args = readonly_steps.pop(0)
                return httpx.Response(200, json={'choices': [{'message': {'tool_calls': [tool_call(name, args)]}}]})
            async with httpx.AsyncClient(transport=httpx.MockTransport(inspect_handler)) as client:
                w.model_client = client
                await w.start_run(s['id'], {'providerId': provider['id'], 'message': '只读分析', 'taskKind': 'inspect'})
                await settle(w)
            assert s['status'] == 'completed', s.get('error')
            assert s['task']['result']['cards'][0]['title'] == '项目结构'
            assert '1. 项目结构' in s['messages'][-1]['content']
            assert '保留边界测试' in s['messages'][-1]['content']
            await page.reload()
            await expect(card).to_have_count(2)
            latest = card.last
            await expect(latest).to_contain_text('没有执行代码')
            await expect(latest.locator('.dev-result-files')).to_have_count(0)
            await expect(latest.locator('.dev-result-warning')).to_have_count(0)
            await expect(latest).not_to_contain_text('请人工确认边界输入')
            await expect(page.locator('#devExecution')).to_contain_text('请人工确认边界输入')
            assert await latest.locator('img').count() == 0
            await expect(latest.locator('.dev-result-number')).to_have_text(['1', '2', '3'])
            await expect(latest.locator('.dev-result-topic-heading h4')).to_have_text(['项目结构', '运行步骤', '优先改进'])
            await expect(latest.locator('.dev-result-note')).to_have_text('说明：已阅读 app.mjs，没有执行代码。')
            assert await latest.evaluate('el => el.lastElementChild.classList.contains("dev-result-note")')
            await expect(latest).not_to_contain_text('历史补充依据仍保存在任务数据中')
            await expect(latest.locator('code').first).to_have_text('app.mjs:1')
            assert await latest.locator('.dev-result-verification, .dev-result-evidence').count() == 0
            await latest.screenshot(path=str(ROOT / '.local/python-check/result-topics-desktop.png'))
            await page.set_viewport_size({'width': 390, 'height': 1000})
            assert await latest.evaluate('el => el.scrollWidth <= el.clientWidth + 1')
            await latest.screenshot(path=str(ROOT / '.local/python-check/result-topics-mobile.png'))
            await page.set_viewport_size({'width': 1440, 'height': 1100})
            # Reloading the workspace also retains topic cards (not just in-memory UI state).
            from backend.workspace import Workspace
            assert Workspace(w.data_dir).session(s['id'])['task']['result']['cards'] == s['task']['result']['cards']
            assert await latest.get_by_role('button', name='查看修改').count() == 0
            assert await card.first.get_by_role('button', name='任务记录').count() == 0
            assert await card.first.get_by_role('button', name='撤销 ↶').count() == 0
            await card.first.get_by_text('检查记录（2）', exact=True).click()
            await expect(card.first.locator('pre').last).to_contain_text('pass 1')
            # Expired command evidence is never displayed as current behavioral success.
            s['commands'][-1]['stale'] = True
            w.save()
            await page.reload()
            await expect(card.first).to_contain_text('源码已变化 · 需重新验证')
            assert await card.first.get_by_text('已完成 · 行为测试通过', exact=True).count() == 0
            # Legacy dense evidence becomes a short footer; full text stays in task records.
            s['task']['result'].pop('cards')
            evidence = '项目根 pom.xml 声明 Java 17；' + 'scripts/start-all.ps1:26-64 负责构建与启动；' * 12 + '静态审查，未运行项目代码。'
            s['task']['result']['evidence'] = evidence
            w.save()
            await page.reload()
            note = card.last.locator('.dev-result-note')
            await expect(note).to_contain_text('详细依据与范围见任务记录')
            assert len(await note.inner_text()) < 150
            assert (await page.locator('#devExecution .dev-verification').inner_text()).count('scripts/start-all.ps1:26-64') == 12
            assert await card.last.locator('.dev-result-verification, .dev-result-evidence').count() == 0
        finally:
            await browser.close()


@pytest.mark.parametrize('cards', [None, [], 'text', [{'title': '', 'items': ['item']}],
    [{'title': 'topic', 'items': []}], [{'title': 'topic', 'items': [123]}],
    [{'title': 'topic', 'items': ['x' * 1501]}], [{'title': 'topic', 'items': ['item'], 'html': '<b>'}]])
def test_invalid_result_topics_rejected(cards):
    from backend.common import AppError
    from backend.result_delivery import result_cards
    with pytest.raises(AppError):
        result_cards({'cards': cards})


def test_legacy_and_structured_result_messages():
    from backend.result_delivery import result_cards, result_message
    assert result_cards({}) == []
    result = {'summary': '已完成', 'evidence': '静态审查，未运行代码。'}
    assert result_message(result) == '已完成\n\n验证依据：静态审查，未运行代码。'
    result['cards'] = result_cards({'cards': [{'title': ' 项目结构 ', 'items': [' app.mjs:1 是入口。 ']}]})
    assert result_message(result) == '已完成\n\n1. 项目结构\n- app.mjs:1 是入口。\n\n验证依据：静态审查，未运行代码。'


def test_result_file_stats_count_net_changes():
    from backend.workspace import Workspace
    changes = [
        {'taskId': 'first', 'path': 'same.py', 'original': 'before\n', 'content': 'middle\n', 'status': 'applied'},
        {'taskId': 'first', 'path': 'same.py', 'original': 'middle\n', 'content': 'after\nextra\n', 'status': 'applied'},
        {'taskId': 'first', 'path': 'new.py', 'original': None, 'content': 'one\ntwo\n', 'status': 'applied'},
        {'taskId': 'second', 'path': 'other.py', 'original': '', 'content': 'ignored', 'status': 'applied'},
        {'taskId': 'first', 'path': 'pending.py', 'original': '', 'content': 'ignored', 'status': 'pending'},
    ]
    assert Workspace.result_files({'changes': changes}, 'first') == [
        {'path': 'same.py', 'additions': 2, 'deletions': 1},
        {'path': 'new.py', 'additions': 2, 'deletions': 0},
    ]
    changes[-1] = {'taskId': 'first', 'path': 'same.py', 'original': 'middle\n', 'content': 'after\nextra\n', 'status': 'reverted'}
    assert Workspace.result_files({'changes': changes}, 'first')[0] == {'path': 'same.py', 'additions': 1, 'deletions': 1}

async def test_unfinished_and_invalidated_result_is_not_success(workspace, live_server):
    from conftest import prepare
    w, project, provider, s = workspace
    _, origin = live_server
    await prepare(w, provider, s)
    assert not s['task'].get('result')
    async with async_playwright() as p:
        browser = await p.chromium.launch(channel='msedge', headless=True)
        try:
            page = await browser.new_page()
            await page.route('https://images.unsplash.com/**', lambda route: route.abort())
            await page.goto(origin)
            await page.locator(f'[data-project-id="{project["id"]}"]').click()
            await expect(page.locator('[data-result-task]')).to_have_count(0)
            s['messages'].append({'role': 'assistant', 'type': 'task_result', 'taskId': s['task']['id'], 'content': '已恢复修改前内容'})
            s['status'] = 'stopped'
            w.save()
            await page.reload()
            await expect(page.locator('.dev-result-warning')).to_contain_text('此结果已失效，请重新验证。')
            await expect(page.locator('[data-result-task]')).to_have_count(0)
        finally:
            await browser.close()
