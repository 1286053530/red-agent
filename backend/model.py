import asyncio
import copy
import json
from pathlib import Path

import httpx

from .common import AppError, dumps

MODEL_REQUEST_ATTEMPTS = 5
MODEL_RETRY_DELAYS = (1, 2, 3, 4)

TOOLS = json.loads(Path(__file__).with_name("tools.json").read_text(encoding="utf-8"))
# Character pagination bounds each result even for minified, single-line files.
read_properties = TOOLS[1]["function"]["parameters"]["properties"]
read_properties.update(offset={"type": "integer", "minimum": 0}, max_chars={"type": "integer", "minimum": 1, "maximum": 12000})
TOOLS[1]["function"]["description"] = "Read UTF-8 source of any size in bounded pages (12000 characters). Follow next_offset using offset to continue. Optional start_line/end_line select at most 400 lines. For inspection read relevant ranges and report coverage; only full-file replacement requires reading all pages. Never treat a partial page as the full file."
TOOLS.append({"type": "function", "function": {"name": "read_skill_resource", "description": "Read an allowlisted reference from the active bundled Skill. Paths come from SKILL.md. Instructions are pinned to this task; this does not read project files or grant new commands.",
    "parameters": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"], "additionalProperties": False}}})


def responses_input(messages):
    converted = []
    for message in messages:
        role = message["role"]
        if role == "tool":
            converted.append({"type": "function_call_output", "call_id": message["tool_call_id"], "output": message["content"]})
        elif message.get("_responses_output"):
            # Reasoning items (including encrypted content) must accompany tool calls
            # on stateless follow-up requests and after a persisted task resumes.
            converted.extend(copy.deepcopy(message["_responses_output"]))
        else:
            content = message.get("content")
            if content:
                if isinstance(content, list):
                    content = [({"type": "input_image", "image_url": part["image_url"]["url"]} if part["type"] == "image_url"
                                else {"type": "input_text", "text": part["text"]}) for part in content]
                converted.append({"role": role, "content": content})
            for call in message.get("tool_calls", []):
                converted.append({"type": "function_call", "call_id": call["id"], **call["function"]})
    return converted


def anthropic_content(content):
    if not isinstance(content, list):
        return [{"type": "text", "text": content or "（无文本）"}]
    converted = []
    for part in content:
        if part["type"] == "image_url":
            header, value = part["image_url"]["url"].split(",", 1)
            converted.append({"type": "image", "source": {"type": "base64", "media_type": header[5:].split(";")[0], "data": value}})
        else:
            converted.append({"type": "text", "text": part["text"]})
    return converted


async def post_with_retries(client, endpoint, headers, body, stop):
    stopped = asyncio.create_task(stop.wait())
    active = None
    try:
        for attempt in range(MODEL_REQUEST_ATTEMPTS):
            if stop.is_set():
                raise AppError("任务已停止。")
            active = asyncio.create_task(client.post(endpoint, headers=headers, json=body))
            done, _ = await asyncio.wait([active, stopped], return_when=asyncio.FIRST_COMPLETED)
            if stopped in done:
                raise AppError("任务已停止。")
            try:
                response = await active
            except httpx.TransportError:
                if attempt + 1 == MODEL_REQUEST_ATTEMPTS:
                    raise
                active = asyncio.create_task(asyncio.sleep(MODEL_RETRY_DELAYS[attempt]))
                done, _ = await asyncio.wait([active, stopped], return_when=asyncio.FIRST_COMPLETED)
                if stopped in done:
                    raise AppError("任务已停止。")
                await active
            else:
                return response
            finally:
                if active and active.done():
                    active = None
    finally:
        for task in (active, stopped):
            if task and not task.done():
                task.cancel()
        await asyncio.gather(*(task for task in (active, stopped) if task), return_exceptions=True)


async def call_model(provider, messages, stop=None, client=None):
    anthropic = provider["protocol"] == "anthropic"
    responses = provider["protocol"] == "responses"
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
                content = anthropic_content(message.get("content"))
            if converted and converted[-1]["role"] == role:
                converted[-1]["content"].extend(content)
            else:
                converted.append({"role": role, "content": content})
        body = {"model": provider["model"], "max_tokens": 8192, "system": "\n".join(m["content"] for m in messages if m["role"] == "system"),
                "messages": converted, "tools": [{"name": t["function"]["name"], "description": t["function"]["description"], "input_schema": t["function"]["parameters"]} for t in TOOLS]}
    else:
        if provider.get("apiKey"):
            headers["Authorization"] = "Bearer " + provider["apiKey"]
        if responses:
            body = {"model": provider["model"], "input": responses_input(messages), "stream": False, "store": False,
                    "include": ["reasoning.encrypted_content"],
                    "tools": [{"type": "function", **tool["function"], "strict": False} for tool in TOOLS]}
        else:
            body = {"model": provider["model"], "messages": [{k: v for k, v in m.items() if not k.startswith("_")} for m in messages], "stream": False, "tools": TOOLS}
    endpoint = provider["baseUrl"].rstrip("/") + ("/messages" if anthropic else "/responses" if responses else "/chat/completions")
    own_client = client is None
    client = client or httpx.AsyncClient(timeout=120, follow_redirects=False)
    try:
        response = await post_with_retries(client, endpoint, headers, body, stop or asyncio.Event())
        if not response.is_success:
            description = {400: "模型拒绝请求，请检查接口协议及模型的图片与工具调用能力", 401: "API Key 无效或已过期", 403: "模型或接口无访问权限", 404: "接口路径或模型不存在", 422: "模型请求格式不受支持，请检查接口协议", 429: "请求限流或账户额度不足"}.get(response.status_code, "模型服务请求失败")
            raise AppError(f"{description}（HTTP {response.status_code}）。", 502)
        try:
            data = response.json()
            if not isinstance(data, dict):
                raise ValueError("invalid response object")
            if responses:
                if data.get("error") or data.get("status") in {"failed", "cancelled", "incomplete", "queued", "in_progress"}:
                    raise ValueError("response did not complete")
                output = data["output"]
                if not isinstance(output, list) or any(not isinstance(item, dict) for item in output):
                    raise ValueError("invalid output")
                text = []
                calls = []
                for item in output:
                    if item["type"] == "message":
                        text.extend(part["text"] if part["type"] == "output_text" else part.get("refusal", "") for part in item["content"])
                    elif item["type"] == "function_call":
                        if not all(isinstance(item.get(key), str) and item[key] for key in ("call_id", "name", "arguments")):
                            raise ValueError("invalid function call")
                        calls.append({"id": item["call_id"], "type": "function", "function": {"name": item["name"], "arguments": item["arguments"]}})
                if not any(text) and not calls:
                    raise ValueError("empty response")
                answer = {"role": "assistant", "content": "\n".join(text), "_responses_output": copy.deepcopy(output)}
                if calls:
                    answer["tool_calls"] = calls
            elif anthropic:
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
        raise AppError(f"模型请求超时，连续 {MODEL_REQUEST_ATTEMPTS} 次连接尝试均失败，请检查网络和服务状态。", 502) from exc
    except httpx.TransportError as exc:
        raise AppError(f"连续 {MODEL_REQUEST_ATTEMPTS} 次无法连接模型服务，请检查接口地址、网络和服务状态。", 502) from exc
    except httpx.HTTPError as exc:
        raise AppError("无法连接模型服务，请检查接口地址、网络和服务状态。", 502) from exc
    finally:
        if own_client:
            await client.aclose()
