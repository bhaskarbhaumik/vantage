"""Route a model reference to a concrete provider, instantiated lazily and cached.

Routing is auth-aware: an agent's provider, key, and model all come from the credential profile
its class maps to (``auth.orchestrator`` or ``auth.research``), falling back to the role's model
tier. That is what lets the section-wise deep-research fan-out run on a different vendor — or a
different key with its own rate limit — than the orchestrator agents.
"""

from __future__ import annotations

from .. import auth as _auth
from ..models.config import Config, ModelRef, ProviderCfg
from .base import LLMProvider, ProviderError


class ProviderRouter:
    def __init__(self, cfg: Config) -> None:
        self._cfg = cfg
        # Keyed by provider *and* key env: two profiles on the same vendor but different keys are
        # different clients, and collapsing them would silently share one account's rate limit.
        self._cache: dict[str, LLMProvider] = {}
        self._conc = cfg.engine.max_concurrency

    def _key_env(self, provider: str) -> str:
        return _auth.key_env(self._cfg, provider)

    def get(self, provider: str, key_env: str | None = None) -> LLMProvider:
        configured = self._cfg.providers.get(provider)
        if configured is not None and not configured.enabled:
            raise ProviderError(f"provider {provider} is disabled; set providers.{provider}.enabled=true")
        env = key_env or self._key_env(provider)
        cache_key = f"{provider}:{env}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        options = self._cfg.providers.get(provider, ProviderCfg())
        if provider == "anthropic":
            from .anthropic_provider import AnthropicProvider

            inst: LLMProvider = AnthropicProvider(env, self._conc, options=options)
        elif provider == "openai":
            from .openai_provider import OpenAIProvider

            inst = OpenAIProvider(env, self._conc, options=options)
        elif provider == "gemini":
            from .gemini_provider import GeminiProvider

            inst = GeminiProvider(env, self._conc, options=options)
        else:
            raise ProviderError(f"unknown provider: {provider}")
        self._cache[cache_key] = inst
        return inst

    def for_model(self, ref: ModelRef) -> tuple[LLMProvider, str]:
        return self.get(ref.provider), ref.model

    def for_role(self, role: str) -> tuple[LLMProvider, str]:
        profile = self._cfg.auth.profile_for(role)
        ref = self._cfg.model_for_role(role)
        provider = profile.provider or ref.provider
        fallback = ref.model
        if provider != ref.provider:
            pc = self._cfg.providers.get(provider)
            fallback = pc.default_model if pc and pc.default_model else ""
        model = _auth.resolve_model(self._cfg, provider, profile, fallback)
        if not model:
            raise ProviderError(f"set providers.{provider}.default_model or the auth profile model")
        env = profile.api_key_env or self._key_env(provider)
        # In subscription mode no key exists to resolve — the backend carries the credentials.
        # Otherwise fail here, with the env var named, rather than inside the SDK's own error.
        if not self._cfg.auth.subscription:
            _auth.resolve_key(self._cfg, provider, profile)
        return self.get(provider, env), model
