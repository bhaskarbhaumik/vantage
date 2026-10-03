import json
import re
from pathlib import Path

import jsonschema

from vantage.blueprint.stages import AGENTS, WAVE_A
from vantage.models.config import Config
from vantage.settings import REPO_DEFAULT, load_config, migrate_user_config


def test_defaults_load():
    cfg = load_config()
    assert cfg.engine.backend in cfg.engine.available_backends
    assert cfg.engine.tier in ("EXECUTIVE", "STANDARD", "FULL_ANNEX")
    assert cfg.models.synthesis.model
    assert len(cfg.engine.available_backends) == 6


def test_template_concurrency_fits_wave_a():
    """Wave A launches ten agents; a lower cap silently serialises the research phase.

    Checked against the shipped template rather than the resolved config, because a user copy at
    ~/.config/vantage/default.json wins and is outside the repo's control. A v2-era user
    config carries max_concurrency 8 — `vantage doctor` reports that drift.
    """
    from vantage.blueprint.stages import WAVE_A
    tmpl = json.loads(Path("config/default.json").read_text())
    assert tmpl["engine"]["max_concurrency"] >= len(WAVE_A)


def test_role_model_map_covers_every_agent():
    rm = json.loads(Path("config/default.json").read_text())["role_model_map"]
    assert set(rm) == set(AGENTS), "role_model_map and the agent roster have drifted apart"


def test_role_model_map():
    cfg = load_config()
    # preflight routes to synthesis (entity resolution is the run's highest-leverage decision)
    assert cfg.model_for_role("preflight").model == cfg.models.synthesis.model
    assert cfg.model_for_role("market").model == cfg.models.research.model
    # the adversarial audit is the hardest judgement in the run
    assert cfg.model_for_role("evidence-audit").model == cfg.models.synthesis.model
    # unknown role falls back to research
    assert cfg.model_for_role("nope").model == cfg.models.research.model


def test_env_override(monkeypatch):
    monkeypatch.setenv("VANTAGE_BACKEND", "api")
    monkeypatch.setenv("VANTAGE_TIER", "executive")
    cfg = load_config()
    assert cfg.engine.backend == "api"
    assert cfg.engine.tier == "EXECUTIVE"


def test_cli_overrides_win():
    cfg = load_config(overrides={"engine": {"backend": "langgraph"}})
    assert cfg.engine.backend == "langgraph"


# ---- user-config migration ---------------------------------------------------------------

def _template() -> dict:
    return json.loads(REPO_DEFAULT.read_text())


def test_migrate_rebrands_every_legacy_token():
    legacy = {
        "_note": "Template config for the Company AID MAS harness.",
        "engine": {"output_dir": "~/company-aid/runs", "max_concurrency": 8, "depth": "STANDARD"},
        "cloud": {"image": "company-aid", "azure": {"env": "company-aid-env"}},
    }
    out, changes = migrate_user_config(legacy, _template())
    blob = json.dumps(out)
    for token in ("company-aid", "company_aid", "Company AID", "Account Intelligence Dossier"):
        assert token not in blob, token
    assert not re.search(r"\bAID\b", blob)
    assert out["engine"]["output_dir"] == "~/.cache/vantage/run"
    assert out["cloud"]["azure"]["env"] == "vantage-env"
    assert any("brand tokens" in c for c in changes)


def test_migrate_drops_v2_leftovers_and_restores_the_roster():
    legacy = {
        "engine": {"depth": "STANDARD", "max_concurrency": 8},
        "role_model_map": {"scoping": "synthesis", "qa-gate": "synthesis", "corporate": "research"},
    }
    out, changes = migrate_user_config(legacy, _template())
    assert "depth" not in out["engine"]
    assert out["engine"]["max_concurrency"] == len(WAVE_A)
    assert set(out["role_model_map"]) == set(AGENTS)
    assert any("scoping" in c for c in changes)


def test_migrate_keeps_a_genuine_customisation():
    """A deliberate override must survive; only stale and missing keys are touched."""
    tmpl = _template()
    legacy = {"engine": {"backend": "api", "max_concurrency": 24},
              "models": {"research": {"provider": "gemini", "model": "gemini-2.5-pro"}}}
    out, _ = migrate_user_config(legacy, tmpl)
    assert out["engine"]["backend"] == "api"
    assert out["engine"]["max_concurrency"] == 24        # above Wave A — left alone
    assert out["models"]["research"]["model"] == "gemini-2.5-pro"
    assert out["models"]["synthesis"] == tmpl["models"]["synthesis"]


def test_migrate_is_idempotent():
    tmpl = _template()
    once, _ = migrate_user_config({}, tmpl)
    twice, changes = migrate_user_config(once, tmpl)
    assert once == twice
    assert changes == []


def test_migrated_config_still_validates_and_loads():
    legacy = {"_note": "Company AID", "engine": {"depth": "STANDARD", "output_dir": "~/company-aid/runs"},
              "role_model_map": {"scoping": "synthesis"}}
    out, _ = migrate_user_config(legacy, _template())
    jsonschema.validate(out, json.loads(Path("config/default.schema.json").read_text()))
    cfg = Config.model_validate(out)
    assert cfg.engine.tier in ("EXECUTIVE", "STANDARD", "FULL_ANNEX")
    assert cfg.auth.mode == "subscription"
