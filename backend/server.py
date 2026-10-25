from contextlib import asynccontextmanager
import hmac
import json
import logging
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse, Response

from .browser import BrowserSession, DISABLED_MESSAGE, RETIRED_ACTIONS
from .common import AppError
from .workspace import Workspace

PUBLIC_FILES = {"index.html", "styles.css", "desktop.css", "account.css", "app.js", "account.js", "developer.js", "developer.css", "agent-theme.css"}


def create_app(assets, data_dir, desktop_token="", workspace=None, browser=None):
    assets, data_dir = Path(assets), Path(data_dir)
    dev = workspace or Workspace(data_dir / "developer")
    xhs = browser or BrowserSession(data_dir / "xiaohongshu-profile")

    @asynccontextmanager
    async def lifespan(app):
        yield
        await dev.shutdown()
        await xhs.close()

    app = FastAPI(lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None)
    app.state.workspace, app.state.browser = dev, xhs

    @app.middleware("http")
    async def local_only(request, call_next):
        port = request.scope.get("server", (None, 3000))[1]
        allowed_port = getattr(app.state, "port", port)
        origins = {f"http://localhost:{allowed_port}", f"http://127.0.0.1:{allowed_port}", f"http://[::1]:{allowed_port}"}
        if "http://" + request.headers.get("host", "") not in origins:
            return JSONResponse({"error": "仅支持本机访问。"}, status_code=403)
        if desktop_token and not hmac.compare_digest(request.cookies.get("shujin_session", ""), desktop_token):
            return JSONResponse({"error": "此服务仅允许桌面客户端访问。"}, status_code=403)
        if request.url.path.startswith("/api/"):
            origin = request.headers.get("origin")
            if origin and origin not in origins or request.headers.get("sec-fetch-site") == "cross-site":
                return JSONResponse({"error": "不允许其他站点访问本机数据。"}, status_code=403)
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Cache-Control"] = "no-store" if request.url.path.startswith("/api/") else "no-cache"
        return response

    @app.api_route("/{path:path}", methods=["GET", "HEAD", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
    async def route(path, request: Request):
        try:
            if path.startswith("api/dev/"):
                data = {}
                if request.method == "POST":
                    if not request.headers.get("content-type", "").startswith("application/json"):
                        raise AppError("请使用 JSON 请求。", 415)
                    raw = bytearray()
                    async for chunk in request.stream():
                        raw.extend(chunk)
                        if len(raw) > 1000000:
                            raise AppError("请求过大。", 413)
                    try:
                        data = json.loads(raw or b"{}")
                    except ValueError as exc:
                        raise AppError("无效的 JSON。") from exc
                    if not isinstance(data, dict):
                        raise AppError("无效的请求参数。")
                return await dev.handle(request.method, path[len("api/dev/"):].split("/"), data, request.query_params)
            if path == "api/xhs/status" and request.method == "GET":
                return await xhs.status()
            if path.startswith("api/xhs/"):
                if request.method != "POST":
                    raise AppError("请使用 POST 请求。", 405)
                # Reject old pages/clients here, before any native bridge or adapter.
                if path in RETIRED_ACTIONS:
                    raise AppError(DISABLED_MESSAGE, 410)
                actions = {"api/xhs/disconnect": lambda: xhs.disconnect()}
                if path not in actions:
                    raise AppError("接口不存在。", 404)
                return await actions[path]()
            if request.method not in {"GET", "HEAD"}:
                return Response(status_code=405)
            file = path or "index.html"
            if file not in PUBLIC_FILES:
                return Response("Not found", status_code=404)
            if request.method == "HEAD":
                return Response(status_code=200)
            return FileResponse(assets / file, media_type="text/javascript" if file.endswith(".js") else None)
        except AppError as exc:
            return JSONResponse({"error": str(exc)}, status_code=exc.status)
        except FileNotFoundError:
            return JSONResponse({"error": "文件不存在。"}, status_code=404)
        except Exception:
            logging.exception("Workbench request failed")
            return JSONResponse({"error": "服务暂时不可用，请重试。"}, status_code=500)

    return app
