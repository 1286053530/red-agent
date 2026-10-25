import argparse
import asyncio
import json
import os
from pathlib import Path
import secrets
import socket
import sys
import tempfile

import uvicorn

from .browser import NativeBrowser
from .common import AppError, dumps, uid
from .server import create_app
from .workspace import Workspace
from .runtime import run_process
from .skill_catalog import SkillCatalog


class DesktopBridge:
    """Private inherited stdio, never an HTTP endpoint or a model tool."""
    def __init__(self):
        self.pending = {}

    async def call(self, method, params):
        request_id = uid()
        future = asyncio.get_running_loop().create_future()
        self.pending[request_id] = future
        print(dumps({"type": "native", "id": request_id, "method": method, "params": params}), flush=True)
        try:
            return await asyncio.wait_for(future, timeout=180 if method == "pick-folder" else 60)
        except asyncio.TimeoutError as exc:
            raise AppError("客户端操作超时，请重试。", 504) from exc
        finally:
            self.pending.pop(request_id, None)

    async def listen(self, server):
        while not server.should_exit:
            line = await asyncio.to_thread(sys.stdin.readline)
            if not line:
                server.should_exit = True
                break
            try:
                reply = json.loads(line)
                if reply.get("type") == "shutdown":
                    server.should_exit = True
                    break
                future = self.pending.get(reply.get("id"))
                if future is not None and not future.done():
                    if reply.get("error"):
                        future.set_exception(AppError(reply["error"], reply.get("status", 500)))
                    else:
                        future.set_result(reply.get("result"))
            except (ValueError, TypeError):
                continue
        for future in self.pending.values():
            if not future.done():
                future.set_exception(AppError("客户端连接已关闭。", 503))


async def serve(args):
    token = secrets.token_hex(32) if args.desktop else ""
    bridge = DesktopBridge() if args.desktop else None
    workspace = Workspace(args.data_dir / "developer", native=bridge.call if bridge else None)
    app = create_app(args.assets, args.data_dir, token, workspace, NativeBrowser(bridge.call) if bridge else None)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("127.0.0.1", args.port))
    sock.listen(128)
    app.state.port = sock.getsockname()[1]
    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=app.state.port, log_level="warning", access_log=False, lifespan="on"))
    listener = asyncio.create_task(bridge.listen(server)) if bridge else None
    running = asyncio.create_task(server.serve(sockets=[sock]))
    try:
        while not server.started and not running.done():
            await asyncio.sleep(0.01)
        if server.started:
            print(dumps({"type": "ready", "origin": f"http://127.0.0.1:{app.state.port}", "token": token, "backend": "python", "version": "2.1.19"}), flush=True)
        await running
    finally:
        sock.close()
        if listener:
            listener.cancel()
            await asyncio.gather(listener, return_exceptions=True)


async def runtime_self_test():
    skill = SkillCatalog().snapshot()
    assert skill["metadata"]["id"] == "software-development" and skill["content"].startswith("---")
    assert len(skill["resources"]) == 3
    with tempfile.TemporaryDirectory(prefix="shujin-runtime-") as folder:
        Path(folder, "real.test.mjs").write_text("import {test} from 'node:test';import assert from 'node:assert/strict';test('behavior',()=>assert.equal(2+3,5));", encoding="utf-8")
        Path(folder, "empty.test.mjs").write_text("// empty", encoding="utf-8")
        passed = await run_process("node", ["--test", "real.test.mjs"], folder)
        empty = await run_process("node", ["--test", "empty.test.mjs"], folder)
        if passed["status"] != "passed" or passed["passedTests"] != 1 or empty["passedTests"] != 0:
            raise RuntimeError(dumps({"passed": passed, "empty": empty}))
        print(dumps({"type": "runtime_self_test", "passed": True, "passedTests": 1, "emptyTests": 0, "skill": skill["metadata"]}), flush=True)


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stdin.reconfigure(encoding="utf-8")
    root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description="筱竹书瑾 Python 后端")
    parser.add_argument("--assets", type=Path, default=root)
    parser.add_argument("--data-dir", type=Path, default=Path(os.environ.get("SHUJIN_DATA_DIR", str(root / ".local"))))
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", "3000")))
    parser.add_argument("--desktop", action="store_true")
    parser.add_argument("--self-test", action="store_true", help="Verify bundled Node supervision and test reporter")
    args = parser.parse_args()
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(runtime_self_test() if args.self_test else serve(args))


if __name__ == "__main__":
    main()
