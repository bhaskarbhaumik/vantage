"""The credential layer: subscription by default, API billing strictly opt-in."""

import pytest

from vantage import auth
from vantage.blueprint.stages import AGENTS, ORCHESTRATOR_AGENTS, SECTION_RESEARCH_AGENTS
from vantage.models.config import Config
from vantage.providers.router import ProviderRouter
from vantage.settings import load_config


def _cfg(**overrides) -> Config:
    return load_config(overrides=overrides or None)


def test_default_is_subscription():
    assert _cfg().auth.mode == "subscription"


def test_subscription_ignores_a_stray_key(monkeypatch):
    """An ANTHROPIC_API_KEY exported for some other tool must not meter a subscription run."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-should-be-ignored")
    cfg = _cfg()
    assert auth.readiness(cfg, "workflow") == []
    # ...and the api backend still refuses, because the key is not what makes it allowed.
    assert any("--auth api-key" in i for i in auth.readiness(cfg, "api"))


def test_agent_classes_partition_the_roster():
    assert set(SECTION_RESEARCH_AGENTS) | set(ORCHESTRATOR_AGENTS) == set(AGENTS)
    assert not set(SECTION_RESEARCH_AGENTS) & set(ORCHESTRATOR_AGENTS)
    assert "financials" in SECTION_RESEARCH_AGENTS
    assert "assembly" in ORCHESTRATOR_AGENTS
    assert "preflight" in ORCHESTRATOR_AGENTS


def test_profile_routes_by_agent_class():
    cfg = _cfg(auth={"mode": "api-key",
                     "research": {"provider": "gemini", "api_key_env": "RESEARCH_KEY"}})
    assert cfg.auth.profile_for("financials").provider == "gemini"
    assert cfg.auth.profile_for("assembly").provider is None
    assert auth.key_env(cfg, "gemini", cfg.auth.profile_for("financials")) == "RESEARCH_KEY"


def test_routed_providers_includes_research_override():
    cfg = _cfg(auth={"mode": "api-key",
                     "research": {"provider": "openai", "api_key_env": "RESEARCH_KEY"}})
    routed = auth.routed_providers(cfg)
    assert routed["openai"] == "RESEARCH_KEY"
    assert routed["anthropic"] == "ANTHROPIC_API_KEY"


def test_readiness_names_every_missing_key(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("RESEARCH_KEY", raising=False)
    cfg = _cfg(auth={"mode": "api-key",
                     "research": {"provider": "openai", "api_key_env": "RESEARCH_KEY"}})
    issues = " ".join(auth.readiness(cfg, "api"))
    assert "ANTHROPIC_API_KEY" in issues and "RESEARCH_KEY" in issues


def test_model_env_overrides_the_tier(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_MODEL", "claude-opus-5")
    cfg = _cfg(auth={"mode": "api-key"})
    profile = cfg.auth.profile_for("financials")
    assert auth.resolve_model(cfg, "anthropic", profile, "claude-sonnet-5") == "claude-opus-5"
    # ANTHROPIC_MODEL must not leak onto a non-anthropic provider — the name would be rejected.
    assert auth.resolve_model(cfg, "openai", profile, "gpt-5") == "gpt-5"


def test_profile_model_env_applies_to_any_provider(monkeypatch):
    monkeypatch.setenv("RESEARCH_MODEL", "gemini-3-pro")
    cfg = _cfg(auth={"mode": "api-key", "research": {"provider": "gemini",
                                                     "model_env": "RESEARCH_MODEL"}})
    profile = cfg.auth.profile_for("market")
    assert auth.resolve_model(cfg, "gemini", profile, "gemini-2.5-pro") == "gemini-3-pro"


def test_model_pin_warning_only_when_metered(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_MODEL", "claude-opus-5")
    assert auth.model_pin_warning(_cfg()) is None            # subscription: no tiers to collapse
    assert "role_model_map" in auth.model_pin_warning(_cfg(auth={"mode": "api-key"}))


def test_resolve_key_never_prompts_by_default(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    cfg = _cfg(auth={"mode": "api-key", "prompt_for_key": True})
    # allow_prompt defaults to False: an agent mid-fan-out must fail, never block on stdin.
    with pytest.raises(auth.AuthError, match="--ask-key"):
        auth.resolve_key(cfg, "anthropic")


def test_prompt_missing_is_a_noop_on_subscription(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    assert auth.prompt_missing(_cfg(auth={"prompt_for_key": True})) == []


def test_router_caches_per_key_not_per_provider(monkeypatch):
    """Two profiles on one vendor with different keys must not share a client, or they share
    one account's rate limit."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-orchestrator")
    monkeypatch.setenv("RESEARCH_KEY", "sk-research")
    cfg = _cfg(auth={"mode": "api-key", "research": {"api_key_env": "RESEARCH_KEY"}})
    router = ProviderRouter(cfg)
    orchestrator, _ = router.for_role("assembly")
    research, _ = router.for_role("financials")
    assert orchestrator is not research
    assert router.for_role("market")[0] is research
