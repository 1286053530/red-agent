import asyncio
import copy
import json
from pathlib import Path

import httpx

from .common import AppError, dumps

TOOLS = json.loads(Path(__file__).with_name("tools.json").read_text(encoding="utf-8"))
# Character pagination bounds each result even for minified, single-line files.
read_properties = TOOLS[1]["function"]["parameters"]["properties"]
read_properties.update(offset={"type": "integer", "minimum": 0}, max_chars={"type": "integer", "minimum": 1, "maximum": 12000})
TOOLS[1]["function"]["description"] = "Read UTF-8 source of any size in bounded pages (12000 characters). Follow next_offset using offset to continue. Optional start_line/end_line select at most 400 lines. For inspection read relevant ranges and report coverage; only full-file replacement requires reading all pages. Never treat a partial page as the full file."
TOOLS.append({"type": "function", "function": {"name": "read_skill_resource", "description": "Read an allowlisted reference from the active bundled Skill. Paths come from SKILL.md. Instructions are pinned to this task; this does not read project files or grant new commands.",
    "parameters": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"], "additionalProperties": False}}})


async def call_model(provider, messages, stop=None, client=None):
    anthropic = provider["protocol"] == "anthropic"
    headers = {"Content-Type": "application/json"}
    if anthropic:
        headers.update({"x-api-key": provider.get("apiKey", ""), "anthropic-version": "2023-06-01"})
        converted = []
        for message in messages:
            if message["role"] == "system":
                continue
            role = message["role"]
            if role == "tool":
                role = "user"
                content = [{"type": "tool_result", "tool_use_id": message["tool_call_id"], "content": message["content"]}]
            elif message.get("tool_calls"):
                content = ([{"type": "text", "text": message["content"]}] if message.get("content") else [])
                content += [{"type": "tool_use", "id": c["id"], "name": c["function"]["name"], "input": json.loads(c["function"]["arguments"])} for c in message["tool_calls"]]
            else:
                content = [{"type": "text", "text": message.get("content") or "（无文本）"}]
            if converted and converted[-1]["role"] == role:
                converted[-1]["content"].extend(content)
            else:
                converted.append({"role": role, "content": content})
        body = {"model": provider["model"], "max_tokens": 8192, "system": "\n".join(m["content"] for m in messages if m["role"] == "system"),
                "messages": converted, "tools": [{"name": t["function"]["name"], "description": t["function"]["description"], "input_schema": t["function"]["parameters"]} for t in TOOLS]}
    else:
        if provider.get("apiKey"):
            headers["Authorization"] = "Bearer " + provider["apiKey"]
        body = {"model": provider["model"], "messages": messages, "stream": False, "tools": TOOLS}
    endpoint = provider["baseUrl"].rstrip("/") + ("/messages" if anthropic else "/chat/completions")
    own_client = client is None
    client = client or httpx.AsyncClient(timeout=120, follow_redirects=False)
    request = asyncio.create_task(client.post(endpoint, headers=headers, json=body))
    stopped = asyncio.create_task((stop or asyncio.Event()).wait())
    try:
        done, _ = await asyncio.wait([request, stopped], return_when=asyncio.FIRST_COMPLETED)
        if stopped in done:
            raise AppError("任务已停止。")
        response = await request
        if not response.is_success:
            description = {401: "API Key 无效或已过期", 403: "模型或接口无访问权限", 404: "接口路径或模型不存在", 429: "请求限流或账户额度不足"}.get(response.status_code, "模型服务请求失败")
            raise AppError(f"{description}（HTTP {response.status_code}）。", 502)
        try:
            data = response.json()
            if anthropic:
                content = data["content"]
                answer = {"role": "assistant", "content": "\n".join(c["text"] for c in content if c["type"] == "text"),
                          "tool_calls": [{"id": c["id"], "type": "function", "function": {"name": c["name"], "arguments": dumps(c["input"])}} for c in content if c["type"] == "tool_use"]}
            else:
                message = data["choices"][0]["message"]
                if not isinstance(message.get("content"), str) and not message.get("tool_calls"):
                    raise ValueError("empty response")
                answer = {"role": "assistant", "content": message.get("content") or ""}
                if message.get("tool_calls"):
                    answer["tool_calls"] = copy.deepcopy(message["tool_calls"])
            return {**answer, "usage": data.get("usage", {})}
        except (ValueError, KeyError, TypeError, IndexError) as exc:
            raise AppError("模型返回了无效响应，请检查模型是否支持工具调用。", 502) from exc
    except httpx.TimeoutException as exc:
        raise AppError("模型请求超时，请稍后重试。", 502) from exc
    except httpx.HTTPError as exc:
        raise AppError("无法连接模型服务，请检查接口地址、网络和服务状态。", 502) from exc
    finally:
        for task in [request, stopped]:
            if not task.done():
                task.cancel()
        await asyncio.gather(request, stopped, return_exceptions=True)
        if own_client:
            await client.aclose()
