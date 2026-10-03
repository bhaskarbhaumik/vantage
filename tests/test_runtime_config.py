"""Config upgrades and provider protocol checks without paid API calls."""

import asyncio
import copy
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock

import jsonschema
import pytest
from pydantic import ValidationError

from vantage.agents.executor import run_agent
from vantage.blueprint.loader import Blueprint
from vantage.blueprint.stages import AGENTS
from vantage.models.config import Config, ProviderCfg
from vantage.providers.anthropic_provider import AnthropicProvider
from vantage.providers.base import AssistantTurn, ToolCall, ToolSpec
from vantage.providers.gemini_provider import GeminiProvider, _to_contents
from vantage.providers.openai_provider import OpenAIProvider
from vantage.providers.rate_limiter import RateLimiter
from vantage.providers.router import ProviderRouter
from vantage.settings import REPO_DEFAULT, harness_dir, migrate_user_config, run_dir
from vantage.tools.registry import ToolRegistry


def template():
    return json.loads(REPO_DEFAULT.read_text())


@pytest.mark.parametrize("path", ["~/vantage/runs", "~/.cache/vantage/runs"])
def test_migration_updates_known_defaults_and_preserves_customizations(path):
    user = template()
    user["version"] = "1.0"
    user["engine"]["output_dir"] = path
    user["models"]["synthesis"]["model"] = "claude-opus-4-8"
    user["models"]["research"]["model"] = "claude-sonnet-5"
    user["providers"]["openai"]["default_model"] = "gpt-5"
    user["role_model_map"]["contradiction"] = "research"
    original = copy.deepcopy(user)
    defaults = template()
    saved_defaults = copy.deepcopy(defaults)
    out, changes = migrate_user_config(user, defaults)
    assert user == original and defaults == saved_defaults
    assert out["version"] == "2.1"
    assert out["engine"]["output_dir"] == "~/.cache/vantage/run"
    assert out["models"]["synthesis"]["model"] == "claude-opus-5-5"
    assert out["providers"]["openai"]["default_model"] == "gpt-6.1-sol"
    assert out["role_model_map"]["contradiction"] == "research"
    assert changes
    assert migrate_user_config(out, defaults) == (out, [])


def test_custom_output_and_current_concurrency_survive():
    user = {"version": "2.0", "engine": {"output_dir": "/custom/dossiers", "max_concurrency": 2}}
    out, _ = migrate_user_config(user, template())
    assert out["engine"]["output_dir"] == "/custom/dossiers"
    assert out["engine"]["max_concurrency"] == 2


def test_cache_run_path(monkeypatch, tmp_path):
    monkeypatch.setenv("HOME", str(tmp_path))
    assert run_dir(Config(), "example") == tmp_path / ".cache/vantage/run/example"


def test_schema_matches_models_and_validates_template():
    spec = importlib.util.spec_from_file_location("schema_generator", "scripts/generate-config-schema.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    schema = json.loads(Path("config/default.schema.json").read_text())
    assert schema == module.config_schema()
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(template(), schema)
    Config.model_validate(template())


@pytest.mark.parametrize("section,key,value", [
    ("engine", "max_iterations", 0), ("engine", "tool_timeout_seconds", -1),
    ("engine", "max_concurrency", 0), ("models", "max_tokens", 10),
    ("auth", "mode", "typo"), ("engine", "max_iteratons", 12),
    ("output", "formats", ["pdf"]),
])
def test_runtime_and_schema_reject_invalid_settings(section, key, value):
    data = template()
    data[section][key] = value
    with pytest.raises(ValidationError):
        Config.model_validate(data)
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(data, json.loads(Path("config/default.schema.json").read_text()))


def test_profile_provider_uses_its_own_default_model(monkeypatch):
    cfg = Config.model_validate(template())
    cfg.auth.research.provider = "openai"
    router = ProviderRouter(cfg)
    monkeypatch.setattr(router, "get", lambda *args: "mock")
    assert router.for_role("market") == ("mock", "gpt-6.1-sol")
    cfg.auth.research.model = "custom-pin"
    assert router.for_role("market") == ("mock", "custom-pin")


class Block(SimpleNamespace):
    def model_dump(self, **kwargs):
        return vars(self)


def provider(cls, response):
    obj = object.__new__(cls)
    call = AsyncMock(return_value=response)
    obj._client = SimpleNamespace(messages=SimpleNamespace(create=call),
                                  responses=SimpleNamespace(create=call))
    obj._rl = RateLimiter(max_attempts=1)
    return obj, call


COMMON = dict(system="system", messages=[{"role": "user", "content": "test"}],
              tools=[ToolSpec("lookup", "Find evidence", {"type": "object"})],
              temperature=0.2, max_tokens=16000,
              thinking={"enabled": True, "mode": "auto", "effort": "high"})


async def test_anthropic_adaptive_thinking_and_signatures_round_trip():
    blocks = [Block(type="thinking", thinking="reasoning", signature="opaque-signature"),
              Block(type="tool_use", id="call1", name="lookup", input={})]
    p, call = provider(AnthropicProvider, SimpleNamespace(
        content=blocks, usage=SimpleNamespace(input_tokens=3, output_tokens=4), stop_reason="tool_use"))
    first = await p.complete(model="claude-opus-5-5", **COMMON)
    kw = call.call_args.kwargs
    assert "temperature" not in kw
    assert kw["thinking"] == {"type": "adaptive"}
    assert kw["output_config"] == {"effort": "high"}
    history = COMMON["messages"] + [{"role": "assistant", "content": first.content},
                                    {"role": "user", "content": [{"type": "tool_result",
                                     "tool_use_id": "call1", "content": "found"}]}]
    await p.complete(model="claude-opus-5-5", **{**COMMON, "messages": history})
    assert call.call_args.kwargs["messages"][1]["content"][0]["signature"] == "opaque-signature"


async def test_openai_responses_preserves_reasoning_and_call_ids():
    p, call = provider(OpenAIProvider, SimpleNamespace(
        output=[Block(type="reasoning", id="rs1", encrypted_content="encrypted"),
                Block(type="function_call", id="fc1", call_id="call1", name="lookup", arguments="{}")],
        output_text="", usage=SimpleNamespace(input_tokens=1, output_tokens=2)))
    first = await p.complete(model="gpt-6.1-sol", **COMMON)
    assert first.tool_calls[0].id == "call1"
    history = COMMON["messages"] + [{"role": "assistant", "content": [],
                                     "provider_content": first.provider_content},
                                    {"role": "user", "content": [{"type": "tool_result",
                                     "tool_use_id": "call1", "content": "found"}]}]
    await p.complete(model="gpt-6.1-sol", **{**COMMON, "messages": history})
    kw = call.call_args.kwargs
    assert not kw["store"] and "temperature" not in kw
    assert kw["input"][1]["encrypted_content"] == "encrypted"
    assert kw["input"][-1] == {"type": "function_call_output", "call_id": "call1", "output": "found"}
    assert kw["tools"][0]["type"] == "function" and not kw["tools"][0]["strict"]


async def test_gemini_preserves_signed_function_call():
    from google.genai import types

    part = types.Part(function_call=types.FunctionCall(name="lookup", args={}), thought_signature=b"signed")
    response = SimpleNamespace(candidates=[SimpleNamespace(content=types.Content(role="model", parts=[part]))],
                               usage_metadata=None)
    p = object.__new__(GeminiProvider)
    p._rl = RateLimiter(max_attempts=1)
    p._client = SimpleNamespace(aio=SimpleNamespace(models=SimpleNamespace(
        generate_content=AsyncMock(return_value=response))))
    turn = await p.complete(model="gemini-3.5-flash", **COMMON)
    messages = [{"role": "assistant", "content": [{"type": "tool_use", "name": "lookup",
                 "id": turn.tool_calls[0].id, "input": {}}], "provider_content": turn.provider_content}]
    assert _to_contents(messages, types)[0].parts[0].thought_signature == b"signed"


async def test_executor_obeys_iteration_limit_and_tier_settings(tmp_path):
    cfg = Config.model_validate(template())
    cfg.engine.max_iterations = 2
    cfg.models.research.max_tokens = 4000
    cfg.models.research.temperature = 0.4
    p = SimpleNamespace(complete=AsyncMock(return_value=AssistantTurn(
        tool_calls=[ToolCall(id="call1", name="list_dir", input={})])))
    router = SimpleNamespace(for_role=lambda role: (p, "fake"))
    hd = harness_dir(cfg)
    result = await run_agent(AGENTS["market"], cfg=cfg, router=router, blueprint=Blueprint(hd),
                             run_dir=tmp_path, harness_dir=hd, params_text="test")
    assert result.error == "agent did not submit within iteration budget"
    assert p.complete.await_count == 2
    assert p.complete.call_args.kwargs["max_tokens"] == 4000
    assert p.complete.call_args.kwargs["temperature"] == 0.4


async def test_tool_timeout_is_a_reported_gap(tmp_path):
    cfg = Config()
    cfg.engine.tool_timeout_seconds = 0.01
    registry = ToolRegistry(cfg, tmp_path, tmp_path)

    async def slow(args):
        await asyncio.sleep(1)

    registry._tools["slow"] = SimpleNamespace(run=slow)
    assert "timed out" in await registry.run("slow", {})


async def test_retry_attempts_are_bounded():
    call = AsyncMock(side_effect=ConnectionError("temporary"))
    limiter = RateLimiter(max_attempts=2, retry_min_seconds=0, retry_max_seconds=0)
    with pytest.raises(ConnectionError):
        await limiter.run(call)
    assert call.await_count == 2
    with pytest.raises(ValidationError):
        ProviderCfg(retry_min_seconds=5, retry_max_seconds=1)


def test_cli_uses_run_defaults_and_explicit_flags_win(monkeypatch, tmp_path):
    from typer.testing import CliRunner

    from vantage import cli
    from vantage.pipeline.orchestrator import RunResult

    cfg = Config.model_validate(template())
    cfg.engine.output_dir = str(tmp_path)
    cfg.run_defaults.primary_geography = "Europe"
    cfg.run_defaults.target_vertical = "Banking"
    captured = []

    async def run(job):
        captured.append(job)
        return RunResult(slug=job.slug, run_dir=str(tmp_path), dossier="example.md")

    monkeypatch.setattr(cli, "load_config", lambda *a, **k: cfg)
    monkeypatch.setattr(cli, "get_backend", lambda *a, **k: SimpleNamespace(check=lambda: [], run=run))
    args = ["run", "--client", "Example", "--slug", "example", "--json"]
    first = CliRunner().invoke(cli.app, args)
    assert first.exit_code == 0, first.output
    assert captured[-1].primary_geography == "Europe"
    assert captured[-1].target_vertical == "Banking"
    second = CliRunner().invoke(cli.app, args + ["--geography", "AUTO-DETECT",
                                                 "--account-context", "Known account",
                                                 "--capability-pack", "ATTACHED"])
    assert second.exit_code == 0, second.output
    assert captured[-1].primary_geography == "AUTO-DETECT"
    assert captured[-1].account_context == "Known account"
    assert captured[-1].capability_pack == "ATTACHED"


def test_migration_cli_dry_run_then_backup_and_schema(monkeypatch, tmp_path):
    from typer.testing import CliRunner

    from vantage import cli, settings

    path = tmp_path / "default.json"
    monkeypatch.setattr(cli, "USER_CONFIG", path)
    monkeypatch.setattr(settings, "USER_CONFIG_DIR", tmp_path)
    original = '{"version":"1.0","engine":{"output_dir":"~/vantage/runs"}}\n'
    path.write_text(original)
    result = CliRunner().invoke(cli.app, ["config", "migrate", "--dry-run"])
    assert result.exit_code == 0, result.output
    assert path.read_text() == original
    assert list(tmp_path.iterdir()) == [path]
    result = CliRunner().invoke(cli.app, ["config", "migrate"])
    assert result.exit_code == 0, result.output
    assert next(tmp_path.glob("*.bak")).read_text() == original
    data = json.loads(path.read_text())
    assert data["engine"]["output_dir"] == "~/.cache/vantage/run"
    jsonschema.validate(data, json.loads((tmp_path / "default.schema.json").read_text()))


def test_disabled_provider_fails_before_reading_credentials():
    from vantage.providers.base import ProviderError

    cfg = Config.model_validate(template())
    with pytest.raises(ProviderError, match="disabled"):
        ProviderRouter(cfg).get("openai")


def test_organization_prefixed_run_defaults_migrate_without_losing_input():
    user = {"version": "2.0", "run_defaults": {
        "vendor_capability_pack": "ATTACHED",
        "vendor_account_context": "Existing account context",
    }}
    out, changes = migrate_user_config(user, template())
    assert out["run_defaults"]["capability_pack"] == "ATTACHED"
    assert out["run_defaults"]["account_context"] == "Existing account context"
    assert "vendor_capability_pack" not in out["run_defaults"]
    assert any("neutral input names" in change for change in changes)
    Config.model_validate(out)
    user["run_defaults"]["account_context"] = "Explicit neutral setting"
    out, _ = migrate_user_config(user, template())
    assert out["run_defaults"]["account_context"] == "Explicit neutral setting"
