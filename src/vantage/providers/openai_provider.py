"""OpenAI Responses API adapter, preserving reasoning items between tool turns."""

from __future__ import annotations

import json
import os

from ..models.config import ProviderCfg
from .base import AssistantTurn, ProviderError, ToolCall, ToolSpec
from .rate_limiter import RateLimiter, register_transient


def _to_openai_input(messages: list[dict]) -> list[dict]:
    out: list[dict] = []
    for message in messages:
        if message.get("provider_content") is not None:
            out.extend(message["provider_content"])
            continue
        blocks = message["content"]
        if isinstance(blocks, str):
            blocks = [{"type": "text", "text": blocks}]
        for block in blocks:
            if block["type"] == "text":
                out.append({"role": message["role"], "content": block["text"]})
            elif block["type"] == "tool_use":
                out.append({"type": "function_call", "call_id": block["id"],
                            "name": block["name"], "arguments": json.dumps(block["input"])})
            elif block["type"] == "tool_result":
                content = block["content"]
                if isinstance(content, list):
                    content = "".join(c.get("text", "") for c in content)
                out.append({"type": "function_call_output", "call_id": block["tool_use_id"],
                            "output": str(content)})
    return out


class OpenAIProvider:
    name = "openai"

    def __init__(self, api_key_env: str = "OPENAI_API_KEY", max_concurrency: int = 8,
                 *, options: ProviderCfg | None = None) -> None:
        try:
            from openai import APIConnectionError, APITimeoutError, AsyncOpenAI, RateLimitError
        except ImportError as e:  # pragma: no cover
            raise ProviderError("openai SDK not installed") from e
        key = os.environ.get(api_key_env)
        if not key:
            raise ProviderError(f"{api_key_env} is not set")
        options = options or ProviderCfg()
        self._client = AsyncOpenAI(api_key=key, timeout=options.timeout_seconds, max_retries=0)
        self._rl = RateLimiter(options.max_concurrency or max_concurrency, options.max_attempts,
                               options.retry_min_seconds, options.retry_max_seconds)
        register_transient(APIConnectionError, APITimeoutError, RateLimitError)

    async def complete(
        self, *, system: str, messages: list[dict], tools: list[ToolSpec], model: str,
        temperature: float, max_tokens: int, thinking: dict | None = None,
    ) -> AssistantTurn:
        kwargs: dict = {
            "model": model, "instructions": system, "input": _to_openai_input(messages),
            "max_output_tokens": max_tokens, "store": False,
        }
        if model.startswith(("gpt-5", "gpt-6", "o1", "o3", "o4")):
            kwargs["reasoning"] = {"effort": (thinking or {}).get("effort", "medium")}
            kwargs["include"] = ["reasoning.encrypted_content"]
        else:
            kwargs["temperature"] = temperature
        if tools:
            kwargs["tools"] = [{"type": "function", "name": t.name, "description": t.description,
                                "parameters": t.input_schema, "strict": False} for t in tools]

        async def _call():
            return await self._client.responses.create(**kwargs)

        resp = await self._rl.run(_call)
        calls = []
        for item in resp.output:
            if item.type == "function_call":
                calls.append(ToolCall(id=item.call_id, name=item.name,
                                      input=json.loads(item.arguments or "{}")))
        return AssistantTurn(
            text=resp.output_text or "", tool_calls=calls,
            stop_reason="tool_use" if calls else "end_turn",
            usage={"input_tokens": getattr(resp.usage, "input_tokens", 0),
                   "output_tokens": getattr(resp.usage, "output_tokens", 0)},
            provider_content=[item.model_dump(exclude_none=True) for item in resp.output],
        )
