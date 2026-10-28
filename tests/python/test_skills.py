import copy
import json
from pathlib import Path
import shutil

import httpx
import pytest

from backend.common import AppError, digest
from backend.model import TOOLS
from backend.skill_catalog import SkillCatalog, task_skill_context
from backend.workspace import Workspace, task_kind
from conftest import ROOT, prepare, settle, tool_call


async def test_skill_is_automatically_sent_to_model_and_references_are_progressive(workspace):
    w, _, provider, s = workspace
    seen = []
    steps = [("read_skill_resource", {"path": "references/javascript-node.md"}),
             ("update_plan", {"summary": "读取实现", "criteria": "确认加法行为", "next_action": "读源码"}),
             ("read_file", {"path": "app.mjs"}),
             ("finish_task", {"summary": "实现使用减法", "evidence": "app.mjs 中为 a-b；只读未执行代码"})]
    async def handler(request):
        body = json.loads(request.content)
        seen.append(body)
        name, args = steps.pop(0)
        return httpx.Response(200, json={"choices": [{"message": {"tool_calls": [tool_call(name, args)]}}]})
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        w.model_client = client
        await w.start_run(s["id"], {"providerId": provider["id"], "message": "分析加法", "kind": "inspect"})
        await settle(w)
    assert s["status"] == "completed", s["error"]
    assert s["task"]["skill"]["id"] == "software-development"
    main = s["task"]["_skillSnapshot"]["content"]
    reference = s["task"]["_skillSnapshot"]["resources"]["references/javascript-node.md"]
    assert main in seen[0]["messages"][0]["content"]
    assert reference not in seen[0]["messages"][0]["content"]
    for path, content in s['task']['_skillSnapshot']['resources'].items():
        if path != 'references/code-analysis.md':
            assert content not in seen[0]['messages'][0]['content']
    assert all(reference in body["messages"][0]["content"] for body in seen[1:])
    assert s["task"]["skill"]["loadedResources"] == ["references/code-analysis.md", "references/javascript-node.md"]
    names = [tool["function"]["name"] for tool in seen[0]["tools"]]
    assert "read_skill_resource" in names
    assert not s["changes"] and not s["commands"]
    logs = [json.loads(line) for line in (w.data_dir / "runs" / (s["task"]["id"] + ".jsonl")).read_text(encoding="utf-8").splitlines()]
    assert sum(event["type"] == "skill_activated" for event in logs) == 1
    assert sum(event["type"] == "skill_resource_loaded" for event in logs) == 2


@pytest.mark.parametrize('goal,requested,workflow,kind', [
    ('审查登录接口', None, 'code-review', 'inspect'),
    ('Review the bug fix for token validation', None, 'code-review', 'inspect'),
    ('审查新增接口的权限实现', None, 'code-review', 'inspect'),
    ('审查并修复发现的问题', None, 'bug-fix', 'change'),
    ('Review and fix token validation', None, 'bug-fix', 'change'),
    ('修复审查中发现的报错', None, 'bug-fix', 'change'),
    ('Debug the timeout in the worker', None, 'bug-fix', 'change'),
    ('新增导出接口', None, 'feature-development', 'change'),
    ('Implement CSV export', None, 'feature-development', 'change'),
    ('先分析接口，然后添加重试', None, 'feature-development', 'change'),
    ('分析日志，修复错误', None, 'bug-fix', 'change'),
    ('重构缓存模块', None, 'refactoring', 'change'),
    ('Refactor the request handler', None, 'refactoring', 'change'),
    ('排查超时原因', None, 'code-analysis', 'inspect'),
    ('Explain the module architecture', None, 'code-analysis', 'inspect'),
    ('不要修改代码，分析原因', None, 'code-analysis', 'inspect'),
    ('Do not modify files; review the patch', None, 'code-review', 'inspect'),
    ('修复登录错误', 'inspect', 'code-analysis', 'inspect'),
    ('审查缓存模块', 'change', 'general-development', 'change'),
    ('处理这个任务', None, 'general-development', 'change'),
])
async def test_task_workflow_routes_actual_model_context_without_unrelated_guides(workspace, goal, requested, workflow, kind):
    w, _, provider, session = workspace
    observed = []
    async def handler(request):
        observed.append(json.loads(request.content))
        return httpx.Response(200, json={'choices': [{'message': {'tool_calls': [tool_call('fail_task', {'reason': '测试终止模型循环', 'evidence': '仅核对路由上下文'})]}}]})
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        w.model_client = client
        await w.start_run(session['id'], {'providerId': provider['id'], 'message': goal, 'kind': requested})
        await settle(w)
    task = session['task']
    assert task_kind(goal, requested) == task['kind'] == kind
    assert task['skill']['workflow']['id'] == workflow
    assert task['permissions'] == {'edits': False, 'commands': False}
    assert len(observed) == 1
    prompt = observed[0]['messages'][0]['content']
    selected = task['skill']['workflow']['resources']
    assert task['skill']['loadedResources'] == selected
    for path, content in task['_skillSnapshot']['resources'].items():
        assert (content in prompt) == (path in selected)
    # The default prompt sends one workflow at most, rather than every workflow/language.
    all_guides = ''.join(task['_skillSnapshot']['resources'].values())
    assert len(task_skill_context(task)) < len(all_guides)
    assert not session['changes'] and not session['commands']


async def test_automatic_workflow_resource_is_not_activated_twice(workspace):
    w, _, provider, session = workspace
    await prepare(w, provider, session, message='审查接口', kind='inspect')
    path = 'references/code-review.md'
    result = await w.execute(session, 'read_skill_resource', {'path': path})
    assert result['content'] in task_skill_context(session['task'])
    assert session['task']['skill']['loadedResources'] == [path]
    logs = [json.loads(line) for line in (w.data_dir / 'runs' / (session['task']['id'] + '.jsonl')).read_text(encoding='utf-8').splitlines()]
    events = [event for event in logs if event['type'] == 'skill_resource_loaded']
    assert len(events) == 1 and events[0]['automatic'] is True


async def test_skill_snapshot_survives_restart_catalog_changes_and_history_compaction(workspace, tmp_path):
    w, _, provider, s = workspace
    root = tmp_path / "bundled-skills"
    shutil.copytree(ROOT / "backend/skills", root)
    w.skills = SkillCatalog(root)
    await prepare(w, provider, s, kind="inspect")
    reference = await w.execute(s, "read_skill_resource", {"path": "references/code-review.md"})
    pinned = copy.deepcopy(s["task"]["skill"])
    original_system = task_skill_context(s["task"])
    # A later application update changes its resources. Existing tasks keep the exact snapshot.
    source = root / "software-development/references/code-review.md"
    source.write_text("# New review guidance for future tasks", encoding="utf-8")
    assert w.skills.snapshot()["metadata"]["digest"] != pinned["digest"]
    s["history"] = [{"role": "user", "content": "oversized history" * 5000}]
    w.save()
    observed = []
    async def handler(request):
        observed.append(json.loads(request.content))
        return httpx.Response(200, json={"choices": [{"message": {"content": "need more input"}}]})
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        restored = Workspace(w.data_dir, model_client=client, skill_catalog=SkillCatalog(root),
                             intent_classifier=lambda _: {"type": "development"})
        try:
            await restored.resume_run(s["id"], {'feedback': '继续核对代码审查证据'})
            await settle(restored)
            current = restored.session(s["id"])
            assert current["task"]["skill"] == pinned
            assert task_skill_context(current["task"]) == original_system
            assert reference["content"] in observed[0]["messages"][0]["content"]
            assert "New review guidance" not in observed[0]["messages"][0]["content"]
            public = restored.public_session(current)
            assert "_skillSnapshot" not in public["task"]
            assert public["task"]["skill"]["digest"] == pinned["digest"]
        finally:
            await restored.shutdown()


async def test_skills_cannot_read_arbitrary_files_or_bypass_task_permissions(workspace):
    w, _, provider, s = workspace
    await prepare(w, provider, s, kind="inspect", permissions={"commands": True, "edits": True})
    for path in ["../workspace.json", "../../.env", "SKILL.md", "/etc/passwd", "references/unknown.md"]:
        with pytest.raises(AppError, match="资源"):
            await w.execute(s, "read_skill_resource", {"path": path})
    await w.execute(s, "read_skill_resource", {"path": "references/python.md"})
    with pytest.raises(AppError, match="只读"):
        await w.execute(s, "run_command", {"command": "node", "args": ["--test"], "purpose": "not permitted"})
    with pytest.raises(AppError, match="只读"):
        await w.execute(s, "propose_file", {"path": "new.py", "content": "print(1)"})
    await prepare(w, provider, s)
    await w.execute(s, "read_file", {"path": "app.mjs"})
    change = await w.execute(s, "propose_file", {"path": "app.mjs", "content": "export const add=(a,b)=>a+b;\n", "reason": "fix"})
    assert change["status"] == "pending_review"
    assert s["task"]["permissions"] == {"edits": False, "commands": False}


async def test_explicit_opt_out_and_unknown_skill_do_not_change_task_state(workspace):
    w, _, provider, s = workspace
    before = copy.deepcopy(s)
    for skill_id in ["unknown", "../../project", None, []]:
        with pytest.raises(AppError, match="Skill"):
            await w.start_run(s["id"], {"providerId": provider["id"], "message": "analyze", "skillId": skill_id})
        assert s == before
    await prepare(w, provider, s, skillId="none", kind="inspect")
    assert "skill" not in s["task"] and task_skill_context(s["task"]) == ""
    with pytest.raises(AppError, match="资源"):
        await w.execute(s, "read_skill_resource", {"path": "references/python.md"})
    # Legacy tasks without a snapshot are not silently changed during resume.
    w.save()
    restored = Workspace(w.data_dir, model_client=w.model_client,
                         intent_classifier=lambda _: {"type": "development"})
    try:
        await restored.resume_run(s["id"])
        await settle(restored)
        assert "skill" not in restored.session(s["id"])["task"]
    finally:
        await restored.shutdown()


async def test_skill_catalog_api_and_frontend_controls(live_server):
    from playwright.async_api import async_playwright
    _, origin = live_server
    async with httpx.AsyncClient(base_url=origin, trust_env=False) as client:
        skills = (await client.get("/api/dev/skills")).json()["skills"]
        assert skills[0]["id"] == "software-development"
        detail = (await client.get("/api/dev/skills/software-development")).json()
        assert detail["content"].startswith("---")
        assert set(detail["resources"]) == {"references/javascript-node.md", "references/python.md", "references/code-review.md", "references/code-analysis.md", "references/bug-fix.md", "references/feature-development.md", "references/refactoring.md"}
        assert (await client.post("/api/dev/skills", json={})).status_code != 200
        assert (await client.get("/backend/skills/software-development/SKILL.md")).status_code == 404
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(channel="msedge", headless=True)
        try:
            page = await browser.new_page(viewport={"width": 1550, "height": 1100})
            await page.goto(origin + "/#developer")
            await page.evaluate("showView('developer')")
            await page.wait_for_function("document.querySelector('#devSkillSelect').options.length===13")
            assert await page.locator("#devSkillSelect").input_value() == "auto"
            assert not await page.locator(".dev-agent-info").is_visible()
            assert not await page.locator("#devSkillSelect").is_visible()
            assert not await page.locator("#devViewSkill").is_visible()
            assert not await page.locator("#devSkillDetails").is_visible()
            await page.locator('#devModelPicker > summary').click()
            assert await page.locator('#devSkillSelect').is_visible()
            await page.locator('#devViewSkill').click()
            assert await page.locator('#devSkillContent').is_visible()
            assert 'humanizer' in await page.locator('#devSkillContent').inner_text()
            await page.locator('#devSkillSelect').select_option('humanizer')
            await page.locator('#devViewSkill').click()
            await page.wait_for_function("document.querySelector('#devSkillContent').textContent.includes('Humanizer 自然表达')")
            await page.locator('#devSkillSelect').select_option('none')
            assert await page.locator('#devViewSkill').is_disabled()
            await page.locator('#devSkillSelect').select_option('auto')
            folder = ROOT / ".local/skill-check"
            folder.mkdir(parents=True, exist_ok=True)
            await page.screenshot(path=str(folder / "developer-skills.png"))
        finally:
            await browser.close()
