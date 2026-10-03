"""Anthropic provider — native tool use. The primary path for every programmatic backend."""

from __future__ import annotations

import os

from ..models.config import ProviderCfg
from .base import AssistantTurn, ProviderError, ToolCall, ToolSpec
from .rate_limiter import RateLimiter, register_transient


class AnthropicProvider:
    name = "anthropic"

    def __init__(self, api_key_env: str = "ANTHROPIC_API_KEY", max_concurrency: int = 8,
                 *, options: ProviderCfg | None = None) -> None:
        try:
            from anthropic import AsyncAnthropic
        except ImportError as e:  # pragma: no cover
            raise ProviderError("anthropic SDK not installed") from e
        key = os.environ.get(api_key_env)
        if not key:
            raise ProviderError(f"{api_key_env} is not set")
        options = options or ProviderCfg()
        self._client = AsyncAnthropic(api_key=key, timeout=options.timeout_seconds, max_retries=0)
        self._rl = RateLimiter(options.max_concurrency or max_concurrency, options.max_attempts,
                               options.retry_min_seconds, options.retry_max_seconds)
        try:  # widen retryable set with the SDK's own transient errors
            from anthropic import APIConnectionError, APITimeoutError, RateLimitError

            register_transient(APIConnectionError, APITimeoutError, RateLimitError)
        except Exception:  # pragma: no cover
            pass

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
        kwargs: dict = {
            "model": model,
            "system": system,
            "messages": [{"role": m["role"], "content": m["content"]} for m in messages],
            "max_tokens": max_tokens,
        }
        if tools:
            kwargs["tools"] = [t.to_anthropic() for t in tools]
        modern = model.startswith(("claude-opus-4-7", "claude-opus-4-8",
                                   "claude-opus-5", "claude-sonnet-5", "claude-fable-"))
        adaptive = modern or (thinking or {}).get("mode") == "adaptive"
        enabled = (thinking or {}).get("enabled", True)
        always_on = model.startswith(("claude-opus-5-5", "claude-fable-"))
        if adaptive and (enabled or always_on):
            # Opus 5.5 always thinks. Manual budgets and sampling parameters are rejected.
            kwargs["thinking"] = {"type": "adaptive"}
            kwargs["output_config"] = {"effort": (thinking or {}).get("effort", "medium")}
        elif modern:
            kwargs["thinking"] = {"type": "disabled"}
        else:
            kwargs["temperature"] = temperature
            if thinking and thinking.get("enabled"):
                budget = min(int(thinking.get("budget_tokens", 8000)), max_tokens - 1)
                if budget < 1024:
                    raise ProviderError("extended thinking requires max_tokens greater than 1024")
                kwargs["thinking"] = {"type": "enabled", "budget_tokens": budget}
                kwargs["temperature"] = 1.0

        async def _call():
            return await self._client.messages.create(**kwargs)

        resp = await self._rl.run(_call)

        text_parts: list[str] = []
        calls: list[ToolCall] = []
        for block in resp.content:
            btype = getattr(block, "type", None)
            if btype == "text":
                text_parts.append(block.text)
            elif btype == "tool_use":
                calls.append(ToolCall(id=block.id, name=block.name, input=dict(block.input)))
        usage = {
            "input_tokens": getattr(resp.usage, "input_tokens", 0),
            "output_tokens": getattr(resp.usage, "output_tokens", 0),
        }
        return AssistantTurn(
            text="".join(text_parts),
            tool_calls=calls,
            stop_reason=resp.stop_reason or "end_turn",
            usage=usage,
            content=[b.model_dump(exclude_none=True) for b in resp.content],
        )
