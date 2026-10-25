import json

import httpx
import pytest

from backend.workspace import SYSTEM, task_kind
from conftest import ROOT, prepare, settle, tool_call


@pytest.mark.parametrize("message,requested,expected", [
    ("审查一下代码", "auto", "inspect"),
    ("审查开发过程文档和代码", None, "inspect"),
    ("review the code", "auto", "inspect"),
    ("分析并修复登录错误", "auto", "change"),
    ("实现查询功能", None, "change"),
    ("审查代码", "change", "change"),
    ("分析并修复", "inspect", "inspect"),
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


async def test_legacy_review_can_resume_as_read_only_without_restarting(workspace):
    w, _, provider, s = workspace
    await prepare(w, provider, s, message="审查代码", kind="change")
    s["task"].pop("requestedKind")
    await w.execute(s, "update_plan", {"summary": "审查", "criteria": "证据", "next_action": "交付"})
    await w.execute(s, "read_file", {"path": "app.mjs"})
    async def handler(request):
        return httpx.Response(200, json={"choices": [{"message": {"tool_calls": [tool_call("finish_task", {
            "summary": "加法实现错误 — app.mjs:1", "evidence": "a-b，静态审查未执行"})]}}]})
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        w.model_client = client
        await w.resume_run(s["id"])
        await settle(w)
    assert s["status"] == "completed", s["error"]
    assert s["task"]["kind"] == "inspect"
