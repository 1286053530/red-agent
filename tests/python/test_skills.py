import copy
import json
from pathlib import Path
import shutil

import httpx
import pytest

from backend.common import AppError, digest
from backend.model import TOOLS
from backend.skill_catalog import SkillCatalog, task_skill_context
from backend.workspace import Workspace
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
    assert all(reference in body["messages"][0]["content"] for body in seen[1:])
    assert s["task"]["skill"]["loadedResources"] == ["references/javascript-node.md"]
    names = [tool["function"]["name"] for tool in seen[0]["tools"]]
    assert "read_skill_resource" in names
    assert not s["changes"] and not s["commands"]
    logs = [json.loads(line) for line in (w.data_dir / "runs" / (s["task"]["id"] + ".jsonl")).read_text(encoding="utf-8").splitlines()]
    assert sum(event["type"] == "skill_activated" for event in logs) == 1
    assert sum(event["type"] == "skill_resource_loaded" for event in logs) == 1


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
        restored = Workspace(w.data_dir, model_client=client, skill_catalog=SkillCatalog(root))
        try:
            await restored.resume_run(s["id"])
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
    restored = Workspace(w.data_dir, model_client=w.model_client)
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
        assert set(detail["resources"]) == {"references/javascript-node.md", "references/python.md", "references/code-review.md"}
        assert (await client.post("/api/dev/skills", json={})).status_code != 200
        assert (await client.get("/backend/skills/software-development/SKILL.md")).status_code == 404
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(channel="msedge", headless=True)
        try:
            page = await browser.new_page(viewport={"width": 1550, "height": 1100})
            await page.goto(origin + "/#developer")
            await page.evaluate("showView('developer')")
            await page.wait_for_function("document.querySelector('#devSkillSelect').options.length===2")
            assert await page.locator("#devSkillSelect").input_value() == "software-development"
            await page.click("#devViewSkill")
            await page.locator("#devSkillContent:not(.hidden)").wait_for()
            assert (await page.locator("#devSkillContent").inner_text()).startswith("---")
            await page.select_option("#devSkillSelect", "none")
            assert await page.locator("#devViewSkill").is_disabled()
            assert "基础工具" in await page.locator("#devSkillDescription").inner_text()
            await page.select_option("#devSkillSelect", "software-development")
            folder = ROOT / ".local/skill-check"
            folder.mkdir(parents=True, exist_ok=True)
            await page.screenshot(path=str(folder / "developer-skills.png"))
        finally:
            await browser.close()
