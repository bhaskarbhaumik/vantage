"""Google Gemini provider (google-genai) with function calling.

Secondary path — disabled by default in config. Translates the Anthropic-style conversation to
Gemini ``Content``/``Part`` objects, tracking tool-call names so ``function_response`` parts can
be reconstructed from ``tool_result`` blocks (which only carry the tool-use id).
"""

from __future__ import annotations

import os
import uuid

from ..models.config import ProviderCfg
from .base import AssistantTurn, ProviderError, ToolCall, ToolSpec
from .rate_limiter import RateLimiter


def _to_contents(messages: list[dict], types) -> list:
    id_to_name: dict[str, str] = {}
    contents = []
    for m in messages:
        blocks = m["content"] if isinstance(m["content"], list) else [{"type": "text", "text": m["content"]}]
        if m["role"] == "assistant":
            for b in blocks:
                if b.get("type") == "tool_use":
                    id_to_name[b["id"]] = b["name"]
            if m.get("provider_content") is not None:
                contents.append(types.Content(role="model", parts=[
                    types.Part.model_validate(p) for p in m["provider_content"]
                ]))
                continue
            parts = []
            for b in blocks:
                if b.get("type") == "text" and b.get("text"):
                    parts.append(types.Part(text=b["text"]))
                elif b.get("type") == "tool_use":
                    id_to_name[b["id"]] = b["name"]
                    parts.append(types.Part(function_call=types.FunctionCall(name=b["name"], args=b.get("input", {}))))
            if parts:
                contents.append(types.Content(role="model", parts=parts))
        else:
            parts = []
            for b in blocks:
                if b.get("type") == "text":
                    parts.append(types.Part(text=b["text"]))
                elif b.get("type") == "tool_result":
                    name = id_to_name.get(b["tool_use_id"], "tool")
                    content = b["content"]
                    if isinstance(content, list):
                        content = "".join(c.get("text", "") for c in content)
                    parts.append(
                        types.Part(function_response=types.FunctionResponse(name=name, response={"result": str(content)}))
                    )
            if parts:
                contents.append(types.Content(role="user", parts=parts))
    return contents


class GeminiProvider:
    name = "gemini"

    def __init__(self, api_key_env: str = "GOOGLE_API_KEY", max_concurrency: int = 8,
                 *, options: ProviderCfg | None = None) -> None:
        try:
            from google import genai
        except ImportError as e:  # pragma: no cover
            raise ProviderError("google-genai SDK not installed") from e
        key = os.environ.get(api_key_env)
        if not key:
            raise ProviderError(f"{api_key_env} is not set")
        use_vertex = os.environ.get("GOOGLE_GENAI_USE_VERTEXAI", "").lower() == "true"
        from google.genai import types

        options = options or ProviderCfg()
        http = types.HttpOptions(timeout=int(options.timeout_seconds * 1000),
                                 retry_options=types.HttpRetryOptions(
                                     attempts=options.max_attempts,
                                     initial_delay=options.retry_min_seconds,
                                     max_delay=options.retry_max_seconds))
        self._client = (genai.Client(vertexai=True, http_options=http) if use_vertex
                        else genai.Client(api_key=key, http_options=http))
        self._rl = RateLimiter(options.max_concurrency or max_concurrency, 1)

    async def complete(
        self,
        *,
        system: str,
        messages: list[dict],
        tools: list[ToolSpec],
        model: str,
        temperature: float,
        max_tokens: int,
        thinking: dict | None = None,
    ) -> AssistantTurn:
        from google.genai import types

        gtools = None
        if tools:
            gtools = [
                types.Tool(
                    function_declarations=[
                        types.FunctionDeclaration(name=t.name, description=t.description, parameters=t.input_schema)
                        for t in tools
                    ]
                )
            ]
        reasoning = None
        if thinking and thinking.get("enabled"):
            if model.startswith("gemini-3"):
                effort = thinking.get("effort", "medium")
                level = effort if effort in {"low", "medium"} else "high"
                reasoning = types.ThinkingConfig(thinking_level=level.upper())
            else:
                reasoning = types.ThinkingConfig(thinking_budget=thinking.get("budget_tokens", 8000))
        config = types.GenerateContentConfig(
            system_instruction=system,
            temperature=temperature,
            max_output_tokens=max_tokens,
            tools=gtools,
            thinking_config=reasoning,
        )

        async def _call():
            return await self._client.aio.models.generate_content(
                model=model, contents=_to_contents(messages, types), config=config
            )

        resp = await self._rl.run(_call)
        text_parts: list[str] = []
        calls: list[ToolCall] = []
        cand = resp.candidates[0] if resp.candidates else None
        parts = getattr(getattr(cand, "content", None), "parts", None) or []
        for part in parts:
            if getattr(part, "text", None) and not getattr(part, "thought", False):
                text_parts.append(part.text)
            fc = getattr(part, "function_call", None)
            if fc is not None:
                args = dict(fc.args) if fc.args else {}
                calls.append(ToolCall(id=fc.id or f"call_{uuid.uuid4().hex}", name=fc.name, input=args))
        um = getattr(resp, "usage_metadata", None)
        usage = {
            "input_tokens": getattr(um, "prompt_token_count", 0) if um else 0,
            "output_tokens": getattr(um, "candidates_token_count", 0) if um else 0,
        }
        return AssistantTurn(
            text="".join(text_parts),
            tool_calls=calls,
            stop_reason="tool_use" if calls else "end_turn",
            usage=usage,
            provider_content=[p.model_dump(exclude_none=True) for p in parts],
        )
