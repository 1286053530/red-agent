"""Exercise execution limits through the real task loop and progress guard."""
import json
from pathlib import Path

import httpx
import pytest

from backend.workspace import Workspace
from conftest import settle, tool_call


PLAN = {
    "summary": "逐页审查源码",
    "criteria": "交付已读取范围的证据",
    "next_action": "读取不同分页",
    "todo": ["汇总已读取的范围"],
}
FINISH = {
    "summary": "已审查分页源码，内容为字符 a",
    "evidence": "paging.mjs 已读取范围见 observations；静态审查未运行代码",
}
WARNING = "本次执行预算即将耗尽"
DELIVERY = "现在进入只读分析交付阶段"


@pytest.mark.parametrize("batch_size, investigation_rounds", [(1, 20), (20, 4)])
@pytest.mark.parametrize("extra_read", [False, True], ids=["normal-delivery", "reject-unavailable-tool"])
async def test_inspection_hands_off_to_delivery_before_exhausting_budget(
    workspace, batch_size, investigation_rounds, extra_read,
):
    w, project, provider, session = workspace
    (Path(project["path"]) / "paging.mjs").write_bytes(b"a" * 4096)
    requests = []

    async def handler(request):
        body = json.loads(request.content)
        requests.append(body)
        number = len(requests)
        available = {tool["function"]["name"] for tool in body["tools"]}
        if number == 1:
            name, args = "update_plan", PLAN
        elif number <= investigation_rounds:
            assert "read_file" in available
            return httpx.Response(200, json={"choices": [{"message": {"tool_calls": [
                tool_call("read_file", {"path": "paging.mjs", "offset": ((number - 2) * batch_size + index) * 16, "max_chars": 16})
                for index in range(batch_size)
            ]}}]})
        else:
            assert number == investigation_rounds + 1
            assert available == {"finish_task", "request_user", "fail_task"}
            assert DELIVERY in body["messages"][0]["content"]
            if extra_read:
                return httpx.Response(200, json={"choices": [{"message": {"tool_calls": [
                    tool_call("read_file", {"path": "paging.mjs", "offset": 2000, "max_chars": 16}),
                    tool_call("finish_task", FINISH),
                ]}}]})
            name, args = "finish_task", FINISH
        return httpx.Response(200, json={"choices": [{"message": {"tool_calls": [tool_call(name, args)]}}]})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        w.model_client = client
        await w.start_run(session["id"], {"providerId": provider["id"], "message": "阅读 README 和主要源码，说明运行步骤与改进建议"})
        await settle(w)
    assert session["status"] == "completed", session["error"]
    assert len(requests) == investigation_rounds + 1
    assert session["task"]["calls"] == 2 + (investigation_rounds - 1) * batch_size + int(extra_read)
    assert session["task"]["outcome"]["code"] == "static_review"
    assert session["observations"]["paging.mjs"]["ranges"] == [[0, (investigation_rounds - 1) * batch_size * 16]]
    assert session["task"]["metrics"].get("toolErrors", 0) == int(extra_read)
    if extra_read:
        assert session["events"][-2]["status"] == "error"
        assert "交付阶段" in session["events"][-2]["error"]


@pytest.mark.parametrize("has_plan", [True, False])
async def test_inspection_stops_searching_even_before_reading_source(workspace, monkeypatch, has_plan):
    w, project, provider, session = workspace
    monkeypatch.setattr("backend.workspace.INSPECT_DELIVERY_ROUNDS", 3)
    source = "marker1\nmarker2\nmarker3\n"
    (Path(project["path"]) / "paging.mjs").write_bytes(source.encode("utf-8"))
    requests = []
    read_round = 4 if has_plan else 5

    async def handler(request):
        body = json.loads(request.content)
        requests.append(body)
        number = len(requests)
        available = {tool["function"]["name"] for tool in body["tools"]}
        if number == 1 and has_plan:
            name, args = "update_plan", PLAN
        elif number <= 3:
            assert "search_files" in available
            name, args = "search_files", {"path": "paging.mjs", "query": f"marker{number}"}
        elif number < read_round:
            assert "search_files" not in available and "update_plan" in available
            name, args = "update_plan", PLAN
        elif number == read_round:
            assert "search_files" not in available and "read_file" in available
            name, args = "read_file", {"path": "paging.mjs"}
        else:
            assert number == read_round + 1
            assert available == {"finish_task", "request_user", "fail_task"}
            name, args = "finish_task", {"summary": "已读取 paging.mjs", "evidence": "已核实 marker1、marker2 和 marker3；静态分析未运行代码"}
        return httpx.Response(200, json={"choices": [{"message": {"tool_calls": [tool_call(name, args)]}}]})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        w.model_client = client
        await w.start_run(session["id"], {"providerId": provider["id"], "kind": "inspect", "message": "阅读 README 和主要源码，说明运行步骤与改进建议"})
        await settle(w)
    assert session["status"] == "completed", session["error"]
    assert len(requests) == read_round + 1
    assert session["observations"]["paging.mjs"]["ranges"] == [[0, len(source)]]
    assert session["task"]["metrics"].get("toolErrors", 0) == 0


async def test_supplement_reopens_focused_inspection_after_handoff(workspace, monkeypatch):
    w, project, provider, session = workspace
    monkeypatch.setattr("backend.workspace.INSPECT_DELIVERY_ROUNDS", 3)
    requests = []
    stale_finish = tool_call("finish_task", {"summary": "旧的结论", "evidence": "原有文件"})

    async def handler(request):
        body = json.loads(request.content)
        requests.append(body)
        number = len(requests)
        available = {tool["function"]["name"] for tool in body["tools"]}
        if number == 1:
            name, args = "update_plan", PLAN
        elif number == 2:
            name, args = "read_file", {"path": "app.mjs"}
        elif number == 3:
            name, args = "list_files", {}
        elif number == 4:
            assert available == {"finish_task", "request_user", "fail_task"}
            w.supplement_run(session["id"], {"taskId": session["task"]["id"], "message": "再阅读 package.json，说明测试命令"})
            return httpx.Response(200, json={"choices": [{"message": {"tool_calls": [stale_finish]}}]})
        elif number == 5:
            assert "read_file" in available
            assert "再阅读 package.json" in json.dumps(body, ensure_ascii=False)
            name, args = "read_file", {"path": "package.json"}
        else:
            assert number == 6
            name, args = "finish_task", {"summary": "测试命令为 npm test", "evidence": "package.json 的 test 脚本运行 node --test app.test.mjs；未运行代码"}
        return httpx.Response(200, json={"choices": [{"message": {"tool_calls": [tool_call(name, args)]}}]})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        w.model_client = client
        await w.start_run(session["id"], {"providerId": provider["id"], "kind": "inspect", "message": "分析 app.mjs"})
        await settle(w)
    assert session["status"] == "completed", session["error"]
    assert len(requests) == 6
    assert "package.json" in session["observations"]
    assert session["task"]["supplements"][0]["status"] == "included"
    assert all(event["id"] != stale_finish["id"] for event in session["events"])
    assert session["task"]["result"]["summary"] == "测试命令为 npm test"


async def run_pages(w, project, provider, session, batch_sizes, *, finish_in_batch=False):
    (Path(project["path"]) / "paging.mjs").write_bytes(b"a" * 4096)
    batches = [[tool_call("update_plan", PLAN)]]
    offset = 0
    for size in batch_sizes:
        batches.append([
            tool_call("read_file", {"path": "paging.mjs", "offset": index * 16, "max_chars": 16})
            for index in range(offset, offset + size)
        ])
        offset += size
    finish = tool_call("finish_task", FINISH)
    if finish_in_batch:
        batches[-1].append(finish)
    else:
        batches.append([finish])
    requests = []

    async def handler(request):
        requests.append(json.loads(request.content))
        assert batches, "The task requested an unexpected model round"
        return httpx.Response(200, json={"choices": [{"message": {"tool_calls": batches.pop(0)}}]})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        w.model_client = client
        await w.start_run(session["id"], {"providerId": provider["id"], "message": "审查分页源码"})
        await settle(w)
    return requests, finish["id"]


def assert_saved_progress(w, session, read_count):
    task = session["task"]
    assert task["metrics"].get("toolErrors", 0) == 0
    assert all(event["status"] == "completed" for event in session["events"])
    assert session["observations"]["paging.mjs"]["ranges"] == [[0, read_count * 16]]
    calls = [call["id"] for message in session["history"] for call in message.get("tool_calls", [])]
    results = [message["tool_call_id"] for message in session["history"] if message["role"] == "tool"]
    assert sorted(calls) == sorted(results)
    saved = json.loads((w.data_dir / "workspace.json").read_text(encoding="utf-8"))
    persisted = next(item for item in saved["sessions"] if item["id"] == session["id"])
    assert persisted["status"] == session["status"]
    assert persisted["task"]["checkpoint"] == task["checkpoint"]
    assert persisted["task"]["checkpoint"]["summary"] == PLAN["summary"]
    assert persisted["task"]["checkpoint"]["todo"] == PLAN["todo"]
    assert persisted["task"]["outcome"] == task["outcome"]
    assert persisted["observations"] == session["observations"]
    assert persisted["history"] == session["history"]


@pytest.mark.parametrize("batch_sizes, rounds, calls, warning_start", [
    pytest.param([1] * 58, 60, 60, 55, id="finish-on-model-round-60"),
    pytest.param([30] * 5 + [14, 14], 9, 180, 7, id="finish-on-tool-call-180"),
])
async def test_can_finish_at_extended_budget_boundary(workspace, monkeypatch, batch_sizes, rounds, calls, warning_start):
    # Exercise the independent hard budget without the earlier inspection handoff.
    monkeypatch.setattr("backend.workspace.INSPECT_DELIVERY_ROUNDS", 1000)
    monkeypatch.setattr("backend.workspace.INSPECT_DELIVERY_CALLS", 1000)
    w, project, provider, session = workspace
    requests, finish_id = await run_pages(w, project, provider, session, batch_sizes)
    assert session["status"] == "completed", session["error"]
    assert session["task"]["outcome"]["code"] == "static_review"
    assert session["task"]["rounds"] == len(requests) == rounds
    assert session["task"]["calls"] == calls
    assert session["events"][-1]["id"] == finish_id
    assert_saved_progress(w, session, sum(batch_sizes))
    assert [WARNING in request["messages"][0]["content"] for request in requests] == [
        index >= warning_start for index in range(rounds)
    ]


@pytest.mark.parametrize("batch_sizes, finish_in_batch, rounds, calls, read_count", [
    pytest.param([1] * 59, False, 60, 60, 59, id="model-round-limit"),
    pytest.param([30] * 5 + [14, 30], True, 8, 180, 179, id="tool-limit-cuts-off-batch"),
])
async def test_budget_exhaustion_preserves_progress_and_allows_retry(
    workspace, monkeypatch, batch_sizes, finish_in_batch, rounds, calls, read_count,
):
    monkeypatch.setattr("backend.workspace.INSPECT_DELIVERY_ROUNDS", 1000)
    monkeypatch.setattr("backend.workspace.INSPECT_DELIVERY_CALLS", 1000)
    w, project, provider, session = workspace
    requests, finish_id = await run_pages(
        w, project, provider, session, batch_sizes, finish_in_batch=finish_in_batch,
    )
    task = session["task"]
    task_id = task["id"]
    assert session["status"] == "failed"
    assert task["outcome"]["code"] == "budget_exhausted"
    assert task["outcome"]["retryable"] is True
    assert not task.get("result")
    assert task["rounds"] == len(requests) == rounds
    assert task["calls"] == calls
    assert all(event["id"] != finish_id for event in session["events"])
    assert_saved_progress(w, session, read_count)
    if finish_in_batch:
        repaired = [message for message in session["history"] if message.get("tool_call_id") == finish_id]
        assert len(repaired) == 1 and json.loads(repaired[0]["content"])["error"]

    # Restart and retry the same task using saved evidence and a fresh per-attempt budget.
    loaded = Workspace(w.data_dir, intent_classifier=lambda _: {"type": "development"})
    resumed = loaded.session(session["id"])

    async def handler(request):
        body = json.loads(request.content)
        assert WARNING not in body["messages"][0]["content"]
        assert "汇总已读取的范围" in body["messages"][1]["content"]
        assert "paging.mjs" in body["messages"][1]["content"]
        return httpx.Response(200, json={"choices": [{"message": {
            "tool_calls": [tool_call("finish_task", FINISH)],
        }}]})

    try:
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            loaded.model_client = client
            await loaded.resume_run(resumed["id"])
            await settle(loaded)
        assert resumed["status"] == "completed", resumed["error"]
        assert resumed["task"]["id"] == task_id
        assert resumed["task"]["rounds"] == rounds + 1
        assert resumed["task"]["calls"] == calls + 1
        assert resumed["task"]["attempts"][0]["code"] == "budget_exhausted"
        assert resumed["observations"] == session["observations"]
    finally:
        await loaded.shutdown()
