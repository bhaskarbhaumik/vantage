import pytest

from vantage.blueprint import Blueprint
from vantage.engine import BACKENDS, get_backend
from vantage.pipeline.orchestrator import RunJob
from vantage.settings import harness_dir, load_config


def _cfg_bp(tmp_path, **overrides):
    cfg = load_config(overrides={"engine": {"output_dir": str(tmp_path)}, **overrides})
    return cfg, Blueprint(harness_dir(cfg))


def test_registry_has_six():
    assert list(BACKENDS) == ["workflow", "api", "agent-sdk", "langgraph", "adk", "crewai"]


def test_get_backend_instances(tmp_path):
    cfg, bp = _cfg_bp(tmp_path)
    for name in BACKENDS:
        be = get_backend(name, cfg, bp, harness_dir(cfg))
        assert be.name == name
        assert isinstance(be.check(), list)


def test_unknown_backend_raises(tmp_path):
    cfg, bp = _cfg_bp(tmp_path)
    with pytest.raises(ValueError):
        get_backend("nope", cfg, bp, harness_dir(cfg))


def test_api_backend_needs_api_key_mode(tmp_path):
    """Subscription mode is the default, and the api backend cannot run on it."""
    cfg, bp = _cfg_bp(tmp_path)
    assert cfg.auth.subscription
    issues = get_backend("api", cfg, bp, harness_dir(cfg)).check()
    assert any("--auth api-key" in i for i in issues)


def test_api_backend_reports_missing_key(tmp_path, monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    cfg, bp = _cfg_bp(tmp_path, auth={"mode": "api-key"})
    issues = get_backend("api", cfg, bp, harness_dir(cfg)).check()
    assert any("ANTHROPIC_API_KEY" in i for i in issues)


def test_workflow_backend_ready_on_subscription(tmp_path):
    cfg, bp = _cfg_bp(tmp_path)
    issues = get_backend("workflow", cfg, bp, harness_dir(cfg)).check()
    assert not any("api-key" in i or "API_KEY" in i for i in issues)


def test_workflow_backend_flags_pointless_api_key_mode(tmp_path):
    """--auth api-key with the workflow backend spends nothing: the CLI carries the credentials."""
    cfg, bp = _cfg_bp(tmp_path, auth={"mode": "api-key"})
    issues = get_backend("workflow", cfg, bp, harness_dir(cfg)).check()
    assert any("always runs on the Claude Code" in i for i in issues)


async def test_api_backend_aborts_without_key(tmp_path, monkeypatch):
    """No network: the provider refuses at construction, so scoping aborts cleanly."""
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    cfg, bp = _cfg_bp(tmp_path, auth={"mode": "api-key"})
    be = get_backend("api", cfg, bp, harness_dir(cfg))
    result = await be.run(RunJob(client_legal_name="Acme", slug="acme", research_as_of="2026-08-11"))
    assert result.dossier is None
    assert result.agents_ok == 0
    assert any("ANTHROPIC_API_KEY" in e for e in result.errors)
