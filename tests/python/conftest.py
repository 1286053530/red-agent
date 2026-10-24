import asyncio
from pathlib import Path
import socket

import httpx
import pytest
import uvicorn

from backend.common import uid
from backend.server import create_app
from backend.workspace import Workspace

ROOT = Path(__file__).resolve().parents[2]


def tool_call(name, args=None):
    import json
    return {"id": uid(), "type": "function", "function": {"name": name, "arguments": json.dumps(args or {})}}


@pytest.fixture
async def workspace(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    (project / "package.json").write_text('{"type":"module","scripts":{"test":"node --test app.test.mjs"}}', encoding="utf-8")
    (project / "app.mjs").write_text("export const add=(a,b)=>a-b;\n", encoding="utf-8")
    (project / "app.test.mjs").write_text("import {test} from 'node:test';import assert from 'node:assert/strict';import {add} from './app.mjs';test('adds',()=>{assert.equal(add(2,3),5);assert.equal(add(-2,3),1)});\n", encoding="utf-8")
    async def handler(request):
        return httpx.Response(200, json={"choices": [{"message": {"content": "需要反馈"}}]})
    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    value = Workspace(tmp_path / "data", model_client=client)
    imported = value.import_project(str(project))
    provider = value.save_provider({"name": "fixture", "protocol": "compatible", "baseUrl": "https://example.com/v1", "model": "fixture", "apiKey": "fixture-secret"})
    pub = value.create_session({"projectId": imported["id"]})
    session = value.session(pub["id"])
    yield value, imported, provider, session
    await value.shutdown()
    await client.aclose()


async def settle(workspace):
    while workspace.runs or workspace.executions:
        await asyncio.gather(*list(workspace.runs.values()), *list(workspace.executions.values()))


async def prepare(workspace, provider, session, **kwargs):
    await workspace.start_run(session["id"], {"providerId": provider["id"], "message": "修复并验证", **kwargs})
    await settle(workspace)


@pytest.fixture
async def live_server(workspace, tmp_path):
    w, _, _, _ = workspace
    app = create_app(ROOT, tmp_path / "http-data", workspace=w)
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    sock.listen(128)
    app.state.port = sock.getsockname()[1]
    server = uvicorn.Server(uvicorn.Config(app, log_level="warning", access_log=False))
    task = asyncio.create_task(server.serve(sockets=[sock]))
    while not server.started and not task.done():
        await asyncio.sleep(0.01)
    yield app, f"http://127.0.0.1:{app.state.port}"
    server.should_exit = True
    await task
    sock.close()
