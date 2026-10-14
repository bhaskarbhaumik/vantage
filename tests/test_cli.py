"""CLI: generated config flags, overrides, commands and JSON contracts. No network, no backends."""

from __future__ import annotations

import datetime as dt
import json
import sys
import types
from dataclasses import dataclass, field
from pathlib import Path
from types import SimpleNamespace

import pytest
import typer
from typer.testing import CliRunner

from vantage import __version__, cli
from vantage.cli import completion as C
from vantage.cli import flags as F
from vantage.cli import tui as T
from vantage.engine import BACKENDS
from vantage.models.config import Config, ExportHelpersCfg
from vantage.pipeline.orchestrator import RunResult
from vantage.settings import REPO_DEFAULT, REPO_ROOT, _deep_merge

runner = CliRunner()


def shipped() -> dict:
    return json.loads(REPO_DEFAULT.read_text())


def _flatten(data: dict, prefix: tuple[str, ...] = ()) -> set[str]:
    out: set[str] = set()
    for k, v in data.items():
        if isinstance(v, dict):
            out |= _flatten(v, prefix + (k,))
        else:
            out.add(".".join(prefix + (k,)))
    return out


@pytest.fixture
def cfg_file(tmp_path, monkeypatch):
    """An isolated config file + output dir; keeps the real ~/.config untouched."""
    for var in ("VANTAGE_CONFIG", "VANTAGE_OUTPUT_DIR", "VANTAGE_BACKEND", "VANTAGE_TIER",
                "VANTAGE_AUTH_MODE", "NO_COLOR"):
        monkeypatch.delenv(var, raising=False)
    out = tmp_path / "runs"
    out.mkdir()
    path = tmp_path / "config.json"
    path.write_text(json.dumps({"engine": {"output_dir": str(out)}}))
    return path


def invoke(args, **kw):
    return runner.invoke(cli.app, args, **kw)


def _capture_load(monkeypatch) -> list:
    seen: list = []

    def fake(path=None, overrides=None):
        seen.append((path, overrides or {}))
        return Config.model_validate(_deep_merge(shipped(), overrides or {}))

    monkeypatch.setattr(cli, "load_config", fake)
    return seen


# ── flag generation ───────────────────────────────────────────────────────────────────────────
def test_flag_generation_covers_every_config_leaf():
    data = Config.model_validate(shipped()).model_dump(mode="json")
    data.pop("version")
    data.pop("role_model_map")
    assert F.config_leaf_paths() == _flatten(data)
    specs = F.config_flag_specs()
    assert len({s.flag for s in specs}) == len(specs)
    by = {s.dotted: s for s in specs}
    assert by["engine.max_concurrency"].flag == "--engine-max-concurrency"
    assert by["models.synthesis.model"].flag == "--models-synthesis-model"
    assert by["providers.openai.enabled"].negative == "--no-providers-openai-enabled"
    assert by["export.helpers.diagrams"].choices == ("auto", "dgm", "drawio", "mermaid", "none")
    assert by["export.formats"].multiple and by["export.formats"].kind == "choice"
    assert by["export.brand"].nullable
    assert by["auth.research.provider"].choices == ("anthropic", "openai", "gemini")
    assert by["engine.backend"].env_vars == ["VANTAGE_ENGINE_BACKEND", "VANTAGE_BACKEND"]
    assert all(s.help for s in specs)


def test_every_command_accepts_every_config_flag():
    root = typer.main.get_command(cli.app)
    wanted = {s.flag for s in F.config_flag_specs()} | {"--backend", "--set", "--role-model"}

    def opts(cmd) -> set[str]:
        return {o for p in cmd.params for o in (*getattr(p, "opts", []),
                                                *getattr(p, "secondary_opts", []))}

    assert wanted <= opts(root)
    commands = dict(F.iter_commands(root))
    for path in [("run",), ("generate",), ("export",), ("doctor",), ("config", "get"),
                 ("runs", "list"), ("auth", "status"), ("completion", "zsh"), ("tui",)]:
        assert wanted <= opts(commands[path]), path
    # deploy keeps its own -t/--target; the --tier alias stays available long-form
    deploy_opts = opts(commands[("deploy",)])
    assert {"--target", "-t", "--tier"} <= deploy_opts


# ── overrides ─────────────────────────────────────────────────────────────────────────────────
def test_overrides_reach_load_config(monkeypatch, tmp_path):
    seen = _capture_load(monkeypatch)
    cfgp = tmp_path / "c.json"
    res = invoke([
        "--config", str(cfgp), "--engine-max-concurrency", "12", "--tier", "standard",
        "config", "show", "--json",
        "--providers-openai-enabled", "--export-helpers-diagrams", "mermaid",
        "--set", "tools.web_search.max_results=9", "--set", 'cloud.gcp.region="eu"',
        "--role-model", "backbone=cheap", "--export-formats", "pptx", "--export-formats", "html",
        "--no-ui-animations", "--export-brand", "null", "--models-synthesis-max-tokens", "20000",
    ])
    assert res.exit_code == 0, res.output
    path, over = seen[-1]
    assert path == str(cfgp)
    assert over["engine"] == {"max_concurrency": 12, "tier": "STANDARD"}
    assert over["providers"]["openai"]["enabled"] is True
    assert over["export"]["helpers"]["diagrams"] == "mermaid"
    assert over["export"]["formats"] == ["pptx", "html"]
    assert over["export"]["brand"] is None
    assert over["tools"]["web_search"]["max_results"] == 9
    assert over["cloud"]["gcp"]["region"] == "eu"
    assert over["role_model_map"] == {"backbone": "cheap"}
    assert over["ui"]["animations"] is False
    assert over["models"]["synthesis"]["max_tokens"] == 20000
    shown = json.loads(res.stdout)
    assert shown["engine"]["max_concurrency"] == 12
    assert shown["role_model_map"]["backbone"] == "cheap"


def test_later_flag_wins_and_env_is_lower_than_flags(monkeypatch):
    seen = _capture_load(monkeypatch)
    res = invoke(["--tier", "EXECUTIVE", "config", "get", "engine.tier", "--tier", "STANDARD"])
    assert res.exit_code == 0, res.output
    assert res.stdout.strip() == "STANDARD"
    monkeypatch.setenv("VANTAGE_ENGINE_MAX_CONCURRENCY", "7")
    res = invoke(["config", "get", "engine.max_concurrency"])
    assert res.stdout.strip() == "7"
    res = invoke(["config", "get", "engine.max_concurrency", "--max-concurrency", "9"])
    assert res.stdout.strip() == "9"
    assert seen[-1][1]["engine"]["max_concurrency"] == 9


@pytest.mark.parametrize("args", [
    ["--set", "nope.key=1", "version"],
    ["--set", "engine.max_concurency=3", "version"],
    ["--set", "missing-equals", "version"],
    ["--role-model", "backbone=huge", "version"],
    ["--engine-backend", "nope", "version"],
    ["--engine-max-concurrency", "many", "version"],
])
def test_bad_override_flags_are_usage_errors(args):
    assert invoke(args).exit_code == 2


def test_invalid_config_value_exits_2(monkeypatch):
    _capture_load(monkeypatch)
    res = invoke(["--engine-max-concurrency", "99", "config", "show"])
    assert res.exit_code == 2
    assert "max_concurrency" in res.stderr


# ── run / generate ────────────────────────────────────────────────────────────────────────────
def _fake_backend(monkeypatch, tmp_path, captured: list):
    async def run(job):
        captured.append(job)
        return RunResult(slug=job.slug, run_dir=str(tmp_path), dossier="x-vantage.md",
                         verification={"result": "PASS", "overall_confidence": "Insufficient",
                                       "eqi": 40, "blockers": 1, "majors": 0, "minors": 0})

    monkeypatch.setattr(cli, "get_backend",
                        lambda *a, **k: SimpleNamespace(check=lambda: [], run=run))


def test_generate_alias_auto_slug_and_json_result(monkeypatch, tmp_path):
    seen = _capture_load(monkeypatch)
    captured: list = []
    _fake_backend(monkeypatch, tmp_path, captured)
    res = invoke(["generate", "--client", "Example Holdings Inc.", "--json", "--as-of",
                  "2026-03-04", "--output-dir", str(tmp_path), "-t", "executive",
                  "--remediation-rounds", "0"])
    assert res.exit_code == 0, res.output
    job = captured[-1]
    assert job.slug == "example-2026-03"
    assert job.tier == "EXECUTIVE"
    assert job.remediation_rounds == 0
    assert seen[-1][1]["engine"]["output_dir"] == str(tmp_path)
    last = json.loads(res.stdout.strip().splitlines()[-1])
    assert last["result"]["slug"] == "example-2026-03"
    assert last["result"]["verification"]["overall_confidence"] == "Insufficient"


def test_run_human_summary_is_loud_on_insufficient(monkeypatch, tmp_path):
    _capture_load(monkeypatch)
    _fake_backend(monkeypatch, tmp_path, [])
    res = invoke(["--ascii", "--no-color", "run", "--client", "Example", "--slug", "ex",
                  "--output-dir", str(tmp_path)])
    assert res.exit_code == 0, res.output
    assert "DO NOT PRESENT" in res.stderr
    assert res.stdout == ""


def test_run_dry_run_prints_job_and_config_without_backend(monkeypatch, tmp_path):
    _capture_load(monkeypatch)
    monkeypatch.setattr(cli, "get_backend", lambda *a, **k: pytest.fail("backend built"))
    res = invoke(["run", "--client", "Acme", "--dry-run", "--geography", "EU",
                  "--capability-pack", "attached", "--output-dir", str(tmp_path / "o")])
    assert res.exit_code == 0, res.output
    out = json.loads(res.stdout)
    assert out["job"]["slug"] == f"acme-{dt.date.today().isoformat()[:7]}"
    assert out["job"]["primary_geography"] == "EU"
    assert out["job"]["capability_pack"] == "ATTACHED"
    assert out["config"]["engine"]["output_dir"] == str(tmp_path / "o")
    assert not (tmp_path / "o").exists()


@pytest.mark.parametrize("extra", [["--slug", "../escape"], ["--as-of", "yesterday"],
                                   ["--input-sheet", "MAYBE"], ["--remediation-rounds", "3"]])
def test_run_rejects_bad_inputs(monkeypatch, tmp_path, extra):
    _capture_load(monkeypatch)
    res = invoke(["run", "--client", "Acme", "--dry-run", *extra])
    assert res.exit_code == 2


def test_ask_key_and_auth_alias_become_overrides(monkeypatch, tmp_path):
    seen = _capture_load(monkeypatch)
    res = invoke(["run", "--client", "Acme", "--dry-run", "-a", "api-key", "--ask-key"])
    assert res.exit_code == 0, res.output
    assert seen[-1][1]["auth"] == {"mode": "api-key", "prompt_for_key": True}
    res = invoke(["--auth", "metered", "version"])
    assert res.exit_code == 2


def test_auto_slug():
    assert cli.auto_slug("Acme Industries, Inc.", "2026-10-14") == "acme-industries-2026-10"
    assert cli.auto_slug("Northwind Ceramics plc", "2026-10-01") == "northwind-ceramics-2026-10"
    assert cli.auto_slug("Inc", "2026-01-01") == "inc-2026-01"


# ── JSON contracts ────────────────────────────────────────────────────────────────────────────
def test_version_json_contract():
    res = invoke(["version", "--json"])
    assert res.exit_code == 0
    out = json.loads(res.stdout)
    assert set(out) == {"version", "harness", "config", "python"}
    assert out["version"] == __version__ and out["harness"] == "3.0.0" and out["config"] == "2.2"
    assert invoke(["--version"]).stdout.strip() == __version__


def test_backends_and_doctor_json_contracts(monkeypatch, cfg_file):
    monkeypatch.setattr(cli, "get_backend",
                        lambda name, *a, **k: SimpleNamespace(
                            check=lambda: [] if name == "workflow" else ["not installed"]))
    res = invoke(["--config", str(cfg_file), "backends", "--json"])
    assert res.exit_code == 0, res.output
    out = json.loads(res.stdout)
    assert out["default"] == "workflow"
    assert [b["name"] for b in out["backends"]] == list(BACKENDS)
    assert all(set(b) == {"name", "ready", "issues"} for b in out["backends"])
    assert out["backends"][0]["ready"] is True and out["backends"][1]["issues"] == ["not installed"]

    res = invoke(["--config", str(cfg_file), "doctor", "--json"])
    assert res.exit_code == 0, res.output
    out = json.loads(res.stdout)
    assert out["version"] == __version__
    groups = {c["group"] for c in out["checks"]}
    assert {"engine", "auth", "backends", "tui"} <= groups
    for c in out["checks"]:
        assert set(c) == {"group", "name", "status", "detail"}
        assert c["status"] in ("ok", "warn", "fail")


def test_doctor_includes_export_checks(monkeypatch, cfg_file):
    monkeypatch.setattr(cli, "get_backend", lambda *a, **k: SimpleNamespace(check=lambda: []))
    fake = types.ModuleType("vantage.export.api")
    fake.doctor = lambda cfg: [SimpleNamespace(group="export", name="soffice", status="warn",
                                               detail="LibreOffice not found")]
    monkeypatch.setitem(sys.modules, "vantage.export.api", fake)
    out = json.loads(invoke(["--config", str(cfg_file), "doctor", "--json"]).stdout)
    assert {"group": "export", "name": "soffice", "status": "warn",
            "detail": "LibreOffice not found"} in out["checks"]


def test_ascii_doctor_has_no_nerd_glyphs(monkeypatch, cfg_file):
    monkeypatch.setattr(cli, "get_backend", lambda *a, **k: SimpleNamespace(check=lambda: []))
    res = invoke(["--ascii", "--no-color", "--config", str(cfg_file), "doctor"])
    assert res.exit_code == 0, res.output
    assert not any(0xE000 <= ord(ch) <= 0xF8FF for ch in res.stderr)
    assert "+ ok" in res.stderr


def test_config_show_get_and_options_json(cfg_file):
    res = invoke(["--config", str(cfg_file), "config", "show", "--json"])
    cfg = json.loads(res.stdout)
    assert Config.model_validate(cfg).engine.output_dir == json.loads(
        cfg_file.read_text())["engine"]["output_dir"]
    res = invoke(["--config", str(cfg_file), "config", "get", "export.formats"])
    assert json.loads(res.stdout) == ["pptx", "docx", "pdf", "html"]
    assert invoke(["--config", str(cfg_file), "config", "get", "no.such"]).exit_code == 1

    for args in (["options", "--json"], ["config", "options", "--json"]):
        rows = json.loads(invoke(args).stdout)["options"]
        flags = {r["flag"] for r in rows if r["group"] == "config"}
        assert flags == {s.flag for s in F.config_flag_specs()}
        assert all({"type", "default", "env", "description"} <= set(r) for r in rows)
    assert invoke(["options"]).exit_code == 0


def test_config_set_unset_validate_and_secret_guard(cfg_file):
    base = ["--config", str(cfg_file), "config"]
    assert invoke(base + ["set", "export.depth", "exec"]).exit_code == 0
    assert json.loads(cfg_file.read_text())["export"]["depth"] == "exec"
    assert invoke(base + ["set", "export.depth", "huge"]).exit_code == 2
    assert invoke(base + ["set", "providers.openai.api_key", "abc"]).exit_code == 2
    assert invoke(base + ["set", "cloud.gcp.token", "sk-abcdefghijklmnopqrstuv"]).exit_code == 2
    res = invoke(base + ["set", "auth.mode", "api-key"])
    assert res.exit_code == 0 and "billed per token" in res.stderr
    assert invoke(base + ["unset", "export.depth"]).exit_code == 0
    assert "depth" not in json.loads(cfg_file.read_text())["export"]
    assert invoke(base + ["unset", "export.depth"]).exit_code == 1
    assert invoke(base + ["validate"]).exit_code == 0
    bad = cfg_file.with_name("bad.json")
    bad.write_text('{"engine": {"tier": "HUGE"}}')
    assert invoke(base + ["validate", str(bad)]).exit_code == 1
    assert json.loads(invoke(["config", "schema"]).stdout)


def test_auth_status_json_reports_no_key_values(cfg_file, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-secret-value")
    res = invoke(["--config", str(cfg_file), "auth", "status", "--json"])
    assert res.exit_code == 0
    assert "sk-ant-secret-value" not in res.output
    out = json.loads(res.stdout)
    assert out["mode"] == "subscription" and out["profiles"][0]["key_set"] is None
    out = json.loads(invoke(["--config", str(cfg_file), "-a", "api-key", "auth", "status",
                             "--json"]).stdout)
    assert out["profiles"][0]["key_set"] is True


# ── export ────────────────────────────────────────────────────────────────────────────────────
def _export_api(monkeypatch):
    """The real vantage.export.api when present, else a stub coded to the shared contract."""
    try:
        import importlib

        api = importlib.import_module("vantage.export.api")
    except ImportError:
        api = types.ModuleType("vantage.export.api")

        @dataclass
        class ExportOptions:
            dossier: Path
            formats: list[str]
            depth: str = "standard"
            site_mode: str = "microsite"
            authoring: str = "deterministic"
            out_dir: Path | None = None
            classification: str = "Confidential"
            brand: str | None = None
            client_logo: bool = True
            helpers: ExportHelpersCfg = field(default_factory=ExportHelpersCfg)
            harness_dir: Path | None = None

        def options_from_config(cfg, dossier, **overrides):
            e = cfg.export
            base = dict(formats=list(e.formats), depth=e.depth, site_mode=e.site_mode,
                        authoring=e.authoring, out_dir=Path(e.out_dir) if e.out_dir else None,
                        classification=e.classification, brand=e.brand,
                        client_logo=e.client_logo, helpers=e.helpers)
            base.update(overrides)
            return ExportOptions(dossier=Path(dossier), **base)

        api.ExportOptions = ExportOptions
        api.options_from_config = options_from_config
        monkeypatch.setitem(sys.modules, "vantage.export.api", api)
    captured: list = []

    def fake_export(opts, emit=None):
        captured.append(opts)
        out = Path(opts.out_dir or opts.dossier.parent / "exports")
        art = {"format": "pptx", "path": str(out / "x.pptx"), "bytes": 10, "pages": None,
               "slides": 3}
        if emit:
            from vantage.models.events import RunEvent

            emit(RunEvent(type="artifact", data=art))
        return SimpleNamespace(out_dir=out, artifacts=[art], warnings=[], plans={},
                               verification=None,
                               to_dict=lambda: {"out_dir": str(out), "artifacts": [art]})

    monkeypatch.setattr(api, "export", fake_export, raising=False)
    return captured


def test_export_maps_flags_to_export_options(monkeypatch, cfg_file, tmp_path):
    captured = _export_api(monkeypatch)
    out_root = Path(json.loads(cfg_file.read_text())["engine"]["output_dir"])
    run = out_root / "acme-2026-10"
    run.mkdir()
    (run / "acme-2026-10-vantage.md").write_text("# Acme\n")
    res = invoke([
        "--config", str(cfg_file), "export", "acme-2026-10", "-f", "pptx", "-f", "PDF",
        "--depth", "exec", "--site-mode", "deck", "--authoring", "agents",
        "--out", str(tmp_path / "x"), "--classification", "Internal", "--brand", "example.com",
        "--no-client-logo", "--diagrams", "mermaid", "--no-stock-images", "--helper-timeout",
        "5", "--json",
    ])
    assert res.exit_code == 0, res.output
    opts = captured[-1]
    # a run dir (or the *-vantage.md inside it, once the real API resolves it) — never elsewhere
    assert run.resolve() in (Path(opts.dossier).resolve(), Path(opts.dossier).resolve().parent)
    assert list(opts.formats) == ["pptx", "pdf"]
    assert (opts.depth, opts.site_mode, opts.authoring) == ("exec", "deck", "agents")
    assert Path(opts.out_dir) == tmp_path / "x"
    assert opts.classification == "Internal" and opts.brand == "example.com"
    assert opts.client_logo is False
    assert opts.helpers.diagrams == "mermaid" and opts.helpers.stock_images is False
    assert opts.helpers.timeout_seconds == 5
    lines = [json.loads(line) for line in res.stdout.strip().splitlines()]
    assert lines[0]["type"] == "artifact"
    assert lines[-1]["result"]["artifacts"][0]["format"] == "pptx"


def test_export_defaults_come_from_config_flags(monkeypatch, cfg_file, tmp_path):
    captured = _export_api(monkeypatch)
    dossier = tmp_path / "z-vantage.md"
    dossier.write_text("# Z\n")
    res = invoke(["--config", str(cfg_file), "--export-depth", "full", "--export-formats", "html",
                  "export", str(dossier)])
    assert res.exit_code == 0, res.output
    assert captured[-1].depth == "full" and list(captured[-1].formats) == ["html"]
    assert invoke(["--config", str(cfg_file), "export", "no-such-run"]).exit_code == 2


# ── tui ───────────────────────────────────────────────────────────────────────────────────────
def test_tui_flag_execs_node_with_forwarded_args(monkeypatch, cfg_file, tmp_path):
    entry = tmp_path / "tui" / "dist" / "index.js"
    entry.parent.mkdir(parents=True)
    entry.write_text("")
    monkeypatch.setattr(cli, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(T.shutil, "which", lambda name: "/usr/bin/node" if name == "node" else None)
    monkeypatch.setenv("VANTAGE_ENGINE_BACKEND", "")  # restored after the test
    calls: list = []
    monkeypatch.setattr(T.os, "execvp", lambda file, argv: calls.append((file, argv)))
    res = invoke(["--tui", "--ascii", "--theme", "light", "--backend", "api", "--no-animations",
                  "runs", "list"])
    assert res.exit_code == 0, res.output
    assert calls == [("/usr/bin/node", ["/usr/bin/node", str(entry), "--ascii", "--theme",
                                        "light", "--no-animations", "runs", "list"])]
    import os

    assert os.environ["VANTAGE_ENGINE_BACKEND"] == "api"

    calls.clear()
    res = invoke(["tui", "--icons", "unicode", "--some-tui-flag", "x"])
    assert res.exit_code == 0, res.output
    assert calls[0][1][2:] == ["--icons", "unicode", "--some-tui-flag", "x"]


def test_tui_missing_prints_build_hint(monkeypatch, tmp_path):
    monkeypatch.setattr(cli, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(T.shutil, "which", lambda name: None)
    monkeypatch.setattr(T.os, "execvp", lambda *a: pytest.fail("exec without a TUI"))
    res = invoke(["--tui"])
    assert res.exit_code == 1
    assert "npm ci && npm run build" in res.stderr


def test_tui_prefers_built_entry_then_path(monkeypatch, tmp_path):
    monkeypatch.setattr(T.shutil, "which", lambda n: {"vantage-tui": "/bin/vantage-tui"}.get(n))
    assert T.resolve_tui(tmp_path) == (["/bin/vantage-tui"], None)
    assert T.ui_flags({"ui.icons": "nerd", "ui.color": "never"}) == ["--icons", "nerd",
                                                                    "--no-color"]


# ── completion ────────────────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("prog", C.PROGS)
@pytest.mark.parametrize("shell", C.SHELLS)
def test_completion_scripts_match_committed_files(shell, prog):
    committed = REPO_ROOT / "completions" / C.committed_name(shell, prog)
    assert committed.read_text() == C.script(shell, prog)
    if prog == "vantage":
        res = invoke(["completion", shell])
        assert res.exit_code == 0 and res.stdout == C.script(shell, prog)


def test_completion_install_writes_user_file(monkeypatch, tmp_path):
    monkeypatch.setattr(C.Path, "home", classmethod(lambda cls: tmp_path))
    monkeypatch.setenv("ZDOTDIR", str(tmp_path))
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    res = invoke(["completion", "zsh", "--install"])
    assert res.exit_code == 0, res.output
    target = tmp_path / ".zfunc" / "_vantage"
    assert target.read_text() == C.script("zsh", "vantage")
    assert str(target) in res.stderr and "fpath+=~/.zfunc" in res.stderr.replace("\n", "")
    res = invoke(["completion", "fish", "--install", "--prog-name", "vantage-engine"])
    assert (tmp_path / ".config" / "fish" / "completions" / "vantage-engine.fish").exists()


def test_completion_readme_lists_every_committed_script():
    readme = (REPO_ROOT / "completions" / "README.md").read_text()
    for prog in C.PROGS:
        for shell in C.SHELLS:
            assert C.committed_name(shell, prog) in readme


def test_ascii_mode_output_is_strictly_seven_bit():
    from vantage.cli.ui import Ui

    ui = Ui().configure(icons="ascii", color="never")
    buf = []
    ui.err.file._stream = type("S", (), {"write": lambda self, t: buf.append(t),
                                         "flush": lambda self: None,
                                         "isatty": lambda self: False})()
    from rich.table import Table

    t = Table("group", "detail")
    t.add_row("engine", "Vantage 0.2.0 · harness 3.0.0 — ok ✓ §21.8")
    ui.print(t)
    ui.ok("done → next")
    out = "".join(buf)
    assert out and out.isascii(), out
