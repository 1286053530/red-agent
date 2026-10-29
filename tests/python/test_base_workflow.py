import json

import httpx
import pytest

from backend.common import now
from backend.model import TOOLS
from backend.workspace import SYSTEM, Workspace, task_kind
from conftest import ROOT, prepare, settle, tool_call


def test_uncertainty_confirmation_policy_is_loaded_for_every_task():
    base = (ROOT / "backend/BASE.md").read_text(encoding="utf-8")
    request_user = next(tool["function"] for tool in TOOLS if tool["function"]["name"] == "request_user")
    assert "不猜测、不擅自采用假设，也不拖到总结阶段" in base
    assert "遇到时暂停" in base
    assert "遇到时暂停" in SYSTEM
    assert "Call immediately" in request_user["description"]
    assert "do not guess or defer" in request_user["description"]


@pytest.mark.parametrize("message,requested,expected", [
    ("审查一下代码", "auto", "inspect"),
    ("审查开发过程文档和代码", None, "inspect"),
    ("review the code", "auto", "inspect"),
    ("分析并修复登录错误", "auto", "change"),
    ("实现查询功能", None, "change"),
    ("审查代码", "change", "change"),
    ("分析并修复", "inspect", "inspect"),
    ("请先浏览项目文件，总结项目结构、使用的技术栈和主要入口文件。", "auto", "inspect"),
    ("总结项目结构和技术栈", None, "inspect"),
    ("Browse the project and summarize its structure and entry points", None, "inspect"),
    ("Read the project and implement a login page", None, "change"),
    ("浏览项目，然后修改登录页", "auto", "change"),
    ("总结项目后添加导出功能", "auto", "change"),
])
def test_task_kind_respects_explicit_mode_and_routes_reviews(message, requested, expected):
    assert task_kind(message, requested) == expected


async def test_review_delivers_findings_without_edits_or_commands_even_without_skill(workspace):
    w, _, provider, s = workspace
    steps = [
        ("update_plan", {"summary": "审查加法实现", "criteria": "给出源码证据和影响", "next_action": "读入口"}),
        ("read_file", {"path": "app.mjs", "start_line": 1, "end_line": 1}),
        ("finish_task", {"summary": "[P2] 加法执行减法 — app.mjs:1；2+3 实际为 -1，应返回 5。",
                         "evidence": "app.mjs:1 使用 a-b；静态审查，未运行项目代码。"}),
    ]
    async def handler(request):
        body = json.loads(request.content)
        assert (ROOT / "backend/BASE.md").read_text(encoding="utf-8") in body["messages"][0]["content"]
        assert '"kind":"inspect"' in body["messages"][1]["content"]
        name, args = steps.pop(0)
        return httpx.Response(200, json={"choices": [{"message": {"tool_calls": [tool_call(name, args)]}}]})
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        w.model_client = client
        await w.start_run(s["id"], {"providerId": provider["id"], "message": "审查一下代码", "kind": "auto", "skillId": "none"})
        await settle(w)
    assert s["status"] == "completed", s["error"]
    assert not steps and not s["changes"] and not s["commands"]
    assert "app.mjs:1" in s["task"]["result"]["summary"]


async def test_repeated_context_gets_actionable_feedback_and_can_finish(workspace):
    w, _, provider, s = workspace
    requests = []
    async def handler(request):
        body = json.loads(request.content)
        requests.append(body)
        index = len(requests)
        if index == 1:
            name, args = "update_plan", {"summary": "审查入口", "criteria": "源码证据", "next_action": "读入口"}
        elif index <= 4:
            name, args = "read_file", {"path": "app.mjs"}
        else:
            assert "相同范围已读取两次" in body["messages"][-1]["content"]
            name, args = "finish_task", {"summary": "app.mjs:1 加法错误", "evidence": "a-b，静态审查未执行"}
        return httpx.Response(200, json={"choices": [{"message": {"tool_calls": [tool_call(name, args)]}}]})
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        w.model_client = client
        await w.start_run(s["id"], {"providerId": provider["id"], "message": "审查代码"})
        await settle(w)
    assert s["status"] == "completed", s["error"]
    assert s["task"]["rounds"] == 5
    assert sum(e["status"] == "error" for e in s["events"]) == 1


async def test_long_review_is_prompted_to_deliver_existing_evidence(workspace):
    w, _, provider, s = workspace
    count = 0
    async def handler(request):
        nonlocal count
        body = json.loads(request.content)
        count += 1
        if count == 1:
            name, args = "update_plan", {"summary": "审查", "criteria": "结论", "next_action": "读入口"}
        elif count == 2:
            name, args = "read_file", {"path": "app.mjs"}
        elif count <= 10:
            name, args = "search_files", {"query": f"related_symbol_{count}"}
        else:
            assert "审查收敛提醒" in body["messages"][0]["content"]
            name, args = "finish_task", {"summary": "加法实现错误 — app.mjs:1", "evidence": "a-b，静态审查；范围为入口"}
        return httpx.Response(200, json={"choices": [{"message": {"tool_calls": [tool_call(name, args)]}}]})
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        w.model_client = client
        await w.start_run(s["id"], {"providerId": provider["id"], "message": "审查代码"})
        await settle(w)
    assert s["status"] == "completed", s["error"]
    assert count == 11


@pytest.mark.parametrize("requested", [None, "auto"])
async def test_legacy_review_can_resume_as_read_only_without_restarting(workspace, requested):
    w, _, provider, s = workspace
    await prepare(w, provider, s, message="请先浏览项目文件，总结项目结构、使用的技术栈和主要入口文件。", kind="change")
    if requested is None:
        s["task"].pop("requestedKind")
    else:
        s["task"]["requestedKind"] = requested
    await w.execute(s, "update_plan", {"summary": "审查", "criteria": "证据", "next_action": "交付"})
    await w.execute(s, "read_file", {"path": "app.mjs"})
    task_id = s["task"]["id"]
    observations = dict(s["observations"])
    if requested == "auto":
        w.save()
        w = Workspace(w.data_dir)
        s = w.session(s["id"])
    async def handler(request):
        body = json.loads(request.content)
        if "tools" not in body:
            return httpx.Response(200, json={"choices": [{"message": {"content": json.dumps({
                "type": "development", "kind": "inspect", "tasks": ["总结项目结构"], "tools": ["read_file", "finish_task"]
            }, ensure_ascii=False)}}]})
        assert '"kind":"inspect"' in body["messages"][1]["content"]
        assert "Task workflow: code-analysis" in body["messages"][0]["content"]
        assert "系统已纠正自动任务分类" in str(body["messages"])
        return httpx.Response(200, json={"choices": [{"message": {"tool_calls": [tool_call("finish_task", {
            "summary": "加法实现错误 — app.mjs:1", "evidence": "a-b，静态审查未执行"})]}}]})
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        w.model_client = client
        await w.resume_run(s["id"])
        await settle(w)
    assert s["status"] == "completed", s["error"]
    assert s["task"]["kind"] == "inspect"
    assert s["task"]["id"] == task_id
    assert s["observations"] == observations
    assert s["task"]["permissions"] == {"edits": False, "commands": False}
    assert s["task"]["outcome"]["code"] == "static_review"
    assert not s["changes"] and not s["commands"]
    if requested == "auto":
        await w.shutdown()


@pytest.mark.parametrize("barrier", ["explicit_change", "supplement_change", "feedback_change"])
async def test_auto_inspection_recovery_preserves_requested_changes(workspace, barrier):
    w, _, provider, s = workspace
    await prepare(w, provider, s, message="浏览项目，总结入口文件", kind="change")
    if barrier != "explicit_change":
        s["task"]["requestedKind"] = "auto"
    if barrier == "supplement_change":
        s["task"]["supplements"] = [{"status": "included", "content": "然后修复登录错误", "includedAt": now()}]
    async def handler(request):
        return httpx.Response(200, json={"choices": [{"message": {"tool_calls": [tool_call("request_user", {
            "question": "确认修改范围？", "reason": "保留修改任务的完成检查"})]}}]})
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        w.model_client = client
        await w.resume_run(s["id"], {"feedback": "然后添加登录页"} if barrier == "feedback_change" else {})
        await settle(w)
    assert s["status"] == "awaiting_user", s["error"]
    assert s["task"]["kind"] == "change"
