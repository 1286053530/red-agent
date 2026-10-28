import asyncio
import copy
import json
import re
from pathlib import Path

import httpx

from .common import AppError, dumps

MODEL_REQUEST_ATTEMPTS = 5
MODEL_RETRY_DELAYS = (1, 2, 3, 4)
RETRYABLE_HTTP_STATUSES = {502, 503, 504}
ANTHROPIC_THINKING_BUDGETS = {"low": 1024, "medium": 4096, "high": 8192}


def adaptive_anthropic(model):
    return bool(re.search(r"claude-(?:opus|sonnet)-4[-.]6(?:\b|[-.])", model, re.I))


def reasoning_efforts(protocol, model=""):
    if protocol == "anthropic":
        levels = ["default", "none", "low", "medium", "high"]
        if adaptive_anthropic(model) and "opus" in model.lower():
            levels.append("max")
        return levels
    return ["default", "none", "minimal", "low", "medium", "high", "xhigh"]


def validate_reasoning_effort(protocol, effort="default", model=""):
    if not isinstance(effort, str) or effort not in reasoning_efforts(protocol, model):
        raise AppError("推理强度无效，请重新选择。")
    return effort


def model_error_detail(response, api_key=""):
    """Expose bounded API diagnostics without leaking credentials or HTML pages."""
    try:
        data = response.json()
    except (ValueError, UnicodeError):
        # Gateway errors may be plain text. Never expose HTML proxy pages.
        if response.headers.get("content-type", "").split(";")[0].strip().lower() != "text/plain":
            return ""
        data = response.text[:4096]
        if "<" in data or ">" in data:
            return ""
    error = data.get("error", data) if isinstance(data, dict) else data
    if isinstance(error, str):
        detail = error
    elif isinstance(error, dict):
        detail = "; ".join(str(error[key]) for key in ("message", "code", "param")
                           if isinstance(error.get(key), (str, int)) and error[key])
    else:
        return ""
    if api_key:
        detail = detail.replace(api_key, "[REDACTED]")
    detail = re.sub(r"(?i)\b(?:sk|sess)-[a-z0-9_-]+", "[REDACTED]", detail)
    detail = re.sub(r"(?i)(bearer\s+)[^\s\"'<>;,]+", r"\1[REDACTED]", detail)
    detail = re.sub(r"(?i)((?:api[_-]?key|access[_-]?token|authorization)\s*[=:]\s*[\"']?)[^\s\"'<>;,]+", r"\1[REDACTED]", detail)
    return " ".join(detail.split())[:600]

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


async def post_with_retries(client, endpoint, headers, body, stop, attempts=MODEL_REQUEST_ATTEMPTS):
    stopped = asyncio.create_task(stop.wait())
    active = None
    try:
        for attempt in range(attempts):
            if stop.is_set():
                raise AppError("任务已停止。")
            active = asyncio.create_task(client.post(endpoint, headers=headers, json=body))
            done, _ = await asyncio.wait([active, stopped], return_when=asyncio.FIRST_COMPLETED)
            if stopped in done:
                raise AppError("任务已停止。")
            try:
                response = await active
            except httpx.TransportError:
                if attempt + 1 == attempts:
                    raise
            else:
                if response.status_code not in RETRYABLE_HTTP_STATUSES or attempt + 1 == attempts:
                    return response
            finally:
                if active and active.done():
                    active = None
            active = asyncio.create_task(asyncio.sleep(MODEL_RETRY_DELAYS[min(attempt, len(MODEL_RETRY_DELAYS) - 1)]))
            done, _ = await asyncio.wait([active, stopped], return_when=asyncio.FIRST_COMPLETED)
            if stopped in done:
                raise AppError("任务已停止。")
            await active
            active = None
    finally:
        for task in (active, stopped):
            if task and not task.done():
                task.cancel()
        await asyncio.gather(*(task for task in (active, stopped) if task), return_exceptions=True)


async def call_model(provider, messages, stop=None, client=None, *, include_tools=True, allowed_tools=None, request_timeout=None, attempts=MODEL_REQUEST_ATTEMPTS, max_output_tokens=8192):
    effort = validate_reasoning_effort(provider["protocol"], provider.get("reasoningEffort", "default"), provider["model"])
    available_tools = [tool for tool in TOOLS if allowed_tools is None or tool["function"]["name"] in allowed_tools]
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
            elif role == "assistant" and message.get("_anthropic_content"):
                content = copy.deepcopy(message["_anthropic_content"])
            elif message.get("tool_calls"):
                content = ([{"type": "text", "text": message["content"]}] if message.get("content") else [])
                content += [{"type": "tool_use", "id": c["id"], "name": c["function"]["name"], "input": json.loads(c["function"]["arguments"])} for c in message["tool_calls"]]
            else:
                content = anthropic_content(message.get("content"))
            if converted and converted[-1]["role"] == role:
                converted[-1]["content"].extend(content)
            else:
                converted.append({"role": role, "content": content})
        body = {"model": provider["model"], "max_tokens": max_output_tokens, "system": "\n".join(m["content"] for m in messages if m["role"] == "system"),
                "messages": converted}
        if effort == "none":
            body["thinking"] = {"type": "disabled"}
        elif effort != "default":
            if adaptive_anthropic(provider["model"]):
                body["thinking"] = {"type": "adaptive"}
                body["output_config"] = {"effort": effort}
            else:
                budget = ANTHROPIC_THINKING_BUDGETS[effort]
                body["thinking"] = {"type": "enabled", "budget_tokens": budget}
                body["max_tokens"] += budget
        if include_tools:
            body["tools"] = [{"name": t["function"]["name"], "description": t["function"]["description"], "input_schema": t["function"]["parameters"]} for t in available_tools]
    else:
        if provider.get("apiKey"):
            headers["Authorization"] = "Bearer " + provider["apiKey"]
        if responses:
            body = {"model": provider["model"], "input": responses_input(messages), "stream": False, "store": False,
                    "max_output_tokens": max_output_tokens,
                    "include": ["reasoning.encrypted_content"]}
            if include_tools:
                body["tools"] = [{"type": "function", **tool["function"], "strict": False} for tool in available_tools]
        else:
            body = {"model": provider["model"], "messages": [{k: v for k, v in m.items() if not k.startswith("_")} for m in messages], "stream": False}
            if include_tools:
                body["tools"] = available_tools
        if effort != "default":
            if responses:
                body["reasoning"] = {"effort": effort}
            else:
                body["reasoning_effort"] = effort
    endpoint = provider["baseUrl"].rstrip("/") + ("/messages" if anthropic else "/responses" if responses else "/chat/completions")
    own_client = client is None
    client = client or httpx.AsyncClient(timeout=120, follow_redirects=False)
    try:
        request = post_with_retries(client, endpoint, headers, body, stop or asyncio.Event(), attempts)
        response = await asyncio.wait_for(request, request_timeout) if request_timeout else await request
        if not response.is_success:
            description = {400: "模型拒绝请求，请检查接口协议及模型的图片与工具调用能力", 401: "API Key 无效或已过期", 403: "模型或接口无访问权限", 404: "接口路径或模型不存在", 422: "模型请求格式不受支持，请检查接口协议", 429: "请求限流或账户额度不足"}.get(response.status_code, "模型服务请求失败")
            detail = model_error_detail(response, provider.get("apiKey", ""))
            if detail:
                description += "；服务端详情：" + detail
            if effort != "default" and response.status_code in {400, 422} and re.search(r"reasoning|thinking|effort", detail, re.I):
                description += "；请确认模型支持所选推理强度，或改为默认后重试"
            if response.status_code in RETRYABLE_HTTP_STATUSES and attempts > 1:
                description += f"；已连续尝试 {attempts} 次"
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
                answer = {"role": "assistant", "content": "\n".join(c["text"] for c in content if c["type"] == "text"), "_anthropic_content": copy.deepcopy(content),
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
    except (httpx.TimeoutException, asyncio.TimeoutError) as exc:
        raise AppError(f"模型请求超时，连续 {attempts} 次连接尝试均失败，请检查网络和服务状态。", 502) from exc
    except httpx.TransportError as exc:
        raise AppError(f"连续 {attempts} 次无法连接模型服务，请检查接口地址、网络和服务状态。", 502) from exc
    except httpx.HTTPError as exc:
        raise AppError("无法连接模型服务，请检查接口地址、网络和服务状态。", 502) from exc
    finally:
        if own_client:
            await client.aclose()
