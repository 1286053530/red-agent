import asyncio
import json

import httpx
import pytest

from backend.common import uid
from backend.workspace import Workspace
from conftest import settle, tool_call


async def test_new_conversation_classifies_greeting_without_tools_or_project_reads(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    calls = []

    async def handler(request):
        body = json.loads(request.content)
        calls.append(body)
        assert "tools" not in body
        assert body["model"] == "fixture"
        assert "任务路由器" in body["messages"][0]["content"]
        assert "kind=inspect" in body["messages"][0]["content"]
        assert "kind=change" in body["messages"][0]["content"]
        return httpx.Response(200, json={"choices": [{"message": {"content": json.dumps({
            "type": "chat", "reply": "你好！有什么我可以帮你处理？"
        }, ensure_ascii=False)}}], "usage": {"prompt_tokens": 12, "completion_tokens": 8}})

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    workspace = Workspace(tmp_path / "data", model_client=client)
    imported = workspace.import_project(str(project))
    provider = workspace.save_provider({"name": "fixture", "protocol": "compatible", "baseUrl": "https://example.com/v1", "model": "fixture"})
    session = workspace.session(workspace.create_session({"projectId": imported["id"]})["id"])

    await workspace.start_run(session["id"], {"providerId": provider["id"], "message": "你好", "permissions": {"edits": True, "commands": True}})
    while workspace.runs:
        await asyncio.gather(*list(workspace.runs.values()))

    assert session["status"] == "completed"
    assert session["task"]["kind"] == "chat"
    assert session["task"]["permissions"] == {"edits": True, "commands": True}
    assert session["task"]["rounds"] == 1
    assert session["task"]["metrics"]["inputTokens"] == 12
    assert session["task"]["metrics"]["outputTokens"] == 8
    assert [message["content"] for message in session["messages"] if message["role"] == "assistant"] == ["你好！有什么我可以帮你处理？"]
    assert len(calls) == 1

    await workspace.shutdown()
    await client.aclose()


async def test_model_classification_overrides_automatic_keyword_guess(workspace):
    w, _, provider, session = workspace
    w.intent_classifier = None
    requests = []
    steps = [("update_plan", {"summary": "阅读项目", "criteria": "说明入口", "next_action": "读取源码"}),
             ("read_file", {"path": "app.mjs"}),
             ("finish_task", {"summary": "入口位于 app.mjs", "evidence": "静态读取 app.mjs 第 1 行"})]

    async def handler(request):
        body = json.loads(request.content)
        requests.append(body)
        if "tools" not in body:
            return httpx.Response(200, json={"choices": [{"message": {"content": json.dumps({
                "type": "development", "kind": "inspect", "tasks": ["阅读入口"],
                "tools": ["read_file", "finish_task", "unknown_tool"]
            }, ensure_ascii=False)}}]})
        assert not {"propose_file", "run_command", "review_diff", "command_result"} & {
            item["function"]["name"] for item in body["tools"]}
        name, args = steps.pop(0)
        return httpx.Response(200, json={"choices": [{"message": {"tool_calls": [tool_call(name, args)]}}]})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        w.model_client = client
        await w.start_run(session["id"], {"providerId": provider["id"], "message": "处理一下这个项目",
                                            "kind": "auto", "permissions": {"edits": True, "commands": True}})
        await settle(w)
    assert session["status"] == "completed", session["error"]
    assert session["task"]["kind"] == "inspect"
    assert session["task"]["permissions"] == {"edits": False, "commands": False}
    assert session["task"]["requestedPermissions"] == {"edits": True, "commands": True}
    assert session["task"]["lastIntent"]["tasks"] == ["阅读入口"]
    assert session["task"]["lastIntent"]["tools"] == ["read_file", "finish_task"]
    assert not steps and len(requests) == 4


async def test_running_supplement_is_classified_before_next_tool_round(workspace):
    w, _, provider, session = workspace
    w.intent_classifier = None
    requests, classifications = [], []
    first_started, release = asyncio.Event(), asyncio.Event()
    steps = [("update_plan", {"summary": "改为静态阅读", "criteria": "说明入口", "next_action": "读取源码"}),
             ("read_file", {"path": "app.mjs"}),
             ("finish_task", {"summary": "已阅读 app.mjs", "evidence": "静态读取第 1 行，未运行代码"})]

    async def handler(request):
        body = json.loads(request.content)
        requests.append(body)
        if "tools" not in body:
            kind = "change" if not classifications else "inspect"
            classifications.append(kind)
            return httpx.Response(200, json={"choices": [{"message": {"content": json.dumps({
                "type": "development", "kind": kind, "tasks": ["按最新要求处理"],
                "tools": ["read_file", "finish_task"]
            }, ensure_ascii=False)}}]})
        if len(classifications) == 1:
            first_started.set()
            await release.wait()
            return httpx.Response(200, json={"choices": [{"message": {"tool_calls": [tool_call(
                "propose_file", {"path": "app.mjs", "content": "stale", "reason": "旧要求"})]}}]})
        assert "run_command" not in {item["function"]["name"] for item in body["tools"]}
        name, args = steps.pop(0)
        return httpx.Response(200, json={"choices": [{"message": {"tool_calls": [tool_call(name, args)]}}]})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        w.model_client = client
        await w.start_run(session["id"], {"providerId": provider["id"], "message": "修改 app.mjs",
                                            "kind": "auto", "permissions": {"edits": True, "commands": True}})
        await asyncio.wait_for(first_started.wait(), 5)
        w.supplement_run(session["id"], {"taskId": session["task"]["id"],
                                       "message": "只阅读 app.mjs 并总结，不修改代码"})
        release.set()
        await settle(w)
    assert session["status"] == "completed", session["error"]
    assert classifications == ["change", "inspect"]
    assert session["task"]["kind"] == "inspect"
    assert session["task"]["supplements"][0]["routingKind"] == "inspect"
    assert len(session["task"]["messageIntents"]) == 2
    assert not session["changes"] and not session["commands"] and not steps


async def test_explicit_readonly_mode_cannot_be_expanded_by_model(workspace):
    w, _, provider, session = workspace
    w.intent_classifier = lambda message: {"type": "development", "kind": "change",
                                           "tasks": ["修改代码"], "tools": ["propose_file", "run_command"]}
    requests = []

    async def handler(request):
        body = json.loads(request.content)
        requests.append(body)
        names = {item["function"]["name"] for item in body["tools"]}
        assert "propose_file" not in names and "run_command" not in names
        assert "用户明确选择只读分析" in str(body["messages"])
        return httpx.Response(200, json={"choices": [{"message": {"tool_calls": [tool_call(
            "request_user", {"question": "请新建修改任务", "reason": "当前任务明确选择只读"})]}}]})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        w.model_client = client
        await w.start_run(session["id"], {"providerId": provider["id"], "message": "修复登录错误",
                                            "kind": "inspect", "permissions": {"edits": True, "commands": True}})
        await settle(w)
    assert session["status"] == "awaiting_user", session["error"]
    assert session["task"]["kind"] == "inspect"
    assert session["task"]["permissions"] == {"edits": False, "commands": False}
    assert session["task"]["lastIntent"]["suggestedKind"] == "change"
    assert session["task"]["lastIntent"]["effectiveKind"] == "inspect"
    assert len(requests) == 1


@pytest.mark.parametrize("goal", ["分析 app.py", "请先浏览项目文件，总结项目结构、使用的技术栈和主要入口文件。"])
async def test_development_classification_enters_tool_loop_without_interim_replies(tmp_path, goal):
    project = tmp_path / "project"
    project.mkdir()
    (project / "app.py").write_text("answer = 42\n", encoding="utf-8")
    requests = []

    async def handler(request):
        body = json.loads(request.content)
        requests.append(body)
        if len(requests) == 1:
            assert "tools" not in body
            reply = json.dumps({"type": "development", "kind": "inspect", "tasks": ["阅读入口并总结"],
                                "tools": ["read_file", "finish_task"]})
            return httpx.Response(200, json={"choices": [{"message": {"content": reply}}]})
        assert body.get("tools")
        name, args = [("read_file", {"path": "app.py"}),
                      ("update_plan", {"summary": "分析 app.py", "criteria": "说明文件用途", "next_action": "交付结论"}),
                      ("finish_task", {"summary": "app.py 定义了 answer 常量。", "evidence": "读取 app.py 第 1 行。"})][len(requests) - 2]
        tool_call = {"id": uid(), "type": "function", "function": {"name": name, "arguments": json.dumps(args)}}
        return httpx.Response(200, json={"choices": [{"message": {"content": "正在检查项目…", "tool_calls": [tool_call]}}]})

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    workspace = Workspace(tmp_path / "data", model_client=client)
    imported = workspace.import_project(str(project))
    provider = workspace.save_provider({"name": "fixture", "protocol": "compatible", "baseUrl": "https://example.com/v1", "model": "fixture"})
    session = workspace.session(workspace.create_session({"projectId": imported["id"]})["id"])
    await workspace.start_run(session["id"], {"providerId": provider["id"], "message": goal,
                                            "permissions": {"edits": True, "commands": True}})
    while workspace.runs:
        await asyncio.gather(*list(workspace.runs.values()))

    assert session["status"] == "completed", session["error"]
    assert session["task"]["kind"] == "inspect"
    assert session["task"]["permissions"] == {"edits": False, "commands": False}
    assert session["task"]["outcome"]["code"] == "static_review"
    assert session["task"]["lastIntent"]["tasks"] == ["阅读入口并总结"]
    assert session["task"]["lastIntent"]["tools"] == ["read_file", "finish_task"]
    assert not session["changes"] and not session["commands"]
    assert len(requests) == 4
    assert [message["content"] for message in session["messages"] if message["role"] == "assistant"] == ["app.py 定义了 answer 常量。\n\n验证依据：读取 app.py 第 1 行。"]

    await workspace.shutdown()
    await client.aclose()
