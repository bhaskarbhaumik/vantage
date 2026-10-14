"""Export: helper CLIs (mocked), brand theming, graceful degradation, options, doctor."""

from __future__ import annotations

import json
import subprocess
import zipfile
from pathlib import Path

import pytest

from vantage.export import api
from vantage.export.api import ExportOptions, export, options_from_config
from vantage.export.helpers import Toolbox
from vantage.export.theme import DEFAULT_THEME, contrast
from vantage.models.config import Config, ExportHelpersCfg

FIXTURE = Path(__file__).parent / "fixtures" / "export" / "northwind-2026-10"

BRAND_JSON = {
    "brand": {
        "name": "Contoso",
        "colors": [{"hex": "#ffffff", "type": "light"}, {"hex": "#7A1FA2", "type": "brand"},
                   {"hex": "#0E8A6B", "type": "accent"}],
        "fonts": [{"name": "Font Black", "type": "title"}, {"name": "Lato", "type": "body"}],
        "logos": [],
    }
}
ICON_SVG = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" '
            'stroke="currentColor"><path id="p" d="M4 4h16v16H4z"/></svg>')


def _done(stdout: str = "", code: int = 0) -> subprocess.CompletedProcess:
    return subprocess.CompletedProcess(args=[], returncode=code, stdout=stdout, stderr="")


@pytest.fixture
def no_helpers(monkeypatch):
    """Every helper binary absent: nothing may be executed or fetched."""
    monkeypatch.setattr(Toolbox, "which", lambda self, name: None)

    def boom(*_a, **_k):
        raise AssertionError("no helper may run when none is installed")

    monkeypatch.setattr(Toolbox, "run", boom)
    monkeypatch.setattr(Toolbox, "fetch", boom)


@pytest.fixture
def fake_helpers(monkeypatch):
    """get-brand, get-icon and get-stock present and answering from fixtures; no network."""
    calls: list[list[str]] = []
    binaries = {"get-brand", "get-icon", "get-stock"}
    monkeypatch.setattr(Toolbox, "which",
                        lambda self, name: f"/fake/{name}" if name in binaries else None)

    def run(self, args, timeout=None, cwd=None):
        calls.append(list(args))
        tool = Path(args[0]).name
        if tool == "get-brand":
            return _done(json.dumps(BRAND_JSON))
        if tool == "get-icon" and args[1:3] == ["iconify", "download"]:
            name = args[3].split(":", 1)[1]
            out = Path(args[args.index("-o") + 1])
            out.mkdir(parents=True, exist_ok=True)
            (out / f"iconify-lucide-{name}.svg").write_text(ICON_SVG)
            return _done(f"Saved icon {args[3]}")
        if tool == "get-stock":
            return _done(json.dumps({"rank": 1, "cdn_url": "https://img.invalid/photo.jpg"}))
        return _done("", 1)

    def fetch(self, url, dest):
        from PIL import Image

        dest.parent.mkdir(parents=True, exist_ok=True)
        Image.new("RGB", (64, 36), (40, 80, 120)).save(dest, "JPEG")
        return True

    monkeypatch.setattr(Toolbox, "run", run)
    monkeypatch.setattr(Toolbox, "fetch", fetch)
    return calls


# ── degradation ──────────────────────────────────────────────────────────────


def test_missing_helpers_degrade_with_warnings(tmp_path, no_helpers):
    events = []
    result = export(ExportOptions(dossier=FIXTURE, formats=["pptx", "html"], out_dir=tmp_path,
                                  brand="contoso.example"), emit=events.append)
    assert {a["format"] for a in result.artifacts} == {"pptx", "html"}
    warnings = " ".join(result.warnings)
    for binary in ("get-icon", "get-stock", "get-brand"):
        assert binary in warnings
    assert "neutral theme" in warnings
    assert sum(1 for e in events if e.type == "run_warning") == len(result.warnings)
    # Figures still drew, with the built-in renderer.
    page = Path(result.artifacts[1]["path"]).read_text(encoding="utf8")
    assert page.count("<figure>") >= 2 and "Simplified legal structure" in page


def test_diagrams_none_prints_the_figure_as_a_table(tmp_path, no_helpers):
    helpers = ExportHelpersCfg(icons=False, brand=False, stock_images=False, diagrams="none")
    result = export(ExportOptions(dossier=FIXTURE, formats=["html"], out_dir=tmp_path,
                                  helpers=helpers, client_logo=False))
    page = Path(result.artifacts[0]["path"]).read_text(encoding="utf8")
    assert "Northwind GmbH" in page and ">From<" in page


# ── helpers present (mocked) ─────────────────────────────────────────────────


def test_brand_theming_applies_to_every_output(tmp_path, fake_helpers):
    result = export(ExportOptions(dossier=FIXTURE, formats=["pptx", "docx", "html"],
                                  out_dir=tmp_path, brand="contoso.example",
                                  helpers=ExportHelpersCfg(diagrams="none")))
    accent = "7A1FA2"
    assert contrast(accent, "FFFFFF") >= 4.5
    pptx = Path(next(a["path"] for a in result.artifacts if a["format"] == "pptx"))
    with zipfile.ZipFile(pptx) as zf:
        slides = "".join(zf.read(n).decode() for n in zf.namelist()
                         if n.startswith("ppt/slides/slide"))
    assert accent in slides.upper()
    docx = Path(next(a["path"] for a in result.artifacts if a["format"] == "docx"))
    with zipfile.ZipFile(docx) as zf:
        assert accent in zf.read("word/document.xml").decode().upper()
    html = Path(next(a["path"] for a in result.artifacts if a["format"] == "html"))
    page = html.read_text(encoding="utf8")
    assert f"--accent: #{accent.lower()}" in page
    assert "'Lato'" in page and "Font Black" not in page
    manifest = json.loads(result.manifest.read_text())
    assert manifest["theme"] == "Contoso" and manifest["brand"] == "contoso.example"
    # get-brand ran for the brand and for the client's own domain; results cached on disk.
    domains = [c[1] for c in fake_helpers if Path(c[0]).name == "get-brand"]
    assert domains == ["contoso.example", "northwind-ceramics.example"]
    assert (tmp_path / ".assets" / "brand" / "contoso.example" / "brand.json").exists()


def test_icons_and_stock_images_are_inlined(tmp_path, fake_helpers):
    result = export(ExportOptions(dossier=FIXTURE, formats=["html"], out_dir=tmp_path,
                                  site_mode="deck", depth="exec", client_logo=False,
                                  helpers=ExportHelpersCfg(brand=False, diagrams="none")))
    page = Path(result.artifacts[0]["path"]).read_text(encoding="utf8")
    assert 'class="icon"' in page and "currentColor" in page
    assert "data:image/jpeg;base64," in page
    assert "https://img.invalid" not in page
    icons = list((tmp_path / ".assets" / "icons").glob("*.svg"))
    assert icons and all("lucide" not in p.name for p in icons)


def test_icon_misses_are_remembered(tmp_path, monkeypatch):
    calls = []
    monkeypatch.setattr(Toolbox, "which", lambda self, name: f"/fake/{name}")
    monkeypatch.setattr(Toolbox, "run", lambda self, args, **k: calls.append(args) or _done("", 1))
    tools = Toolbox(ExportHelpersCfg(), tmp_path)
    assert tools.icon_svg("no-such-icon") is None
    assert tools.icon_svg("no-such-icon") is None
    assert len(calls) == 2       # iconify + nerd once; the miss is cached


def test_helper_timeout_is_respected(tmp_path, monkeypatch):
    seen = {}

    def fake_run(args, **kwargs):
        seen["timeout"] = kwargs["timeout"]
        raise subprocess.TimeoutExpired(args, kwargs["timeout"])

    monkeypatch.setattr(subprocess, "run", fake_run)
    tools = Toolbox(ExportHelpersCfg(timeout_seconds=7), tmp_path)
    assert tools.run(["get-icon", "x"]) is None
    assert seen["timeout"] == 7


def test_with_brand_keeps_contrast_for_pale_colours():
    theme = DEFAULT_THEME.with_brand([{"hex": "#9FD3FF", "type": "brand"}], name="Pale")
    assert contrast(theme.palette.accent, "FFFFFF") >= 4.5
    assert theme.brand_name == "Pale"
    assert DEFAULT_THEME.with_brand([]).palette == DEFAULT_THEME.palette


# ── options, doctor, agents ──────────────────────────────────────────────────


def test_options_from_config_precedence():
    cfg = Config.model_validate({"export": {
        "formats": ["pptx"], "depth": "exec", "classification": "Internal",
        "brand": "acme.example", "helpers": {"icons": False, "timeout_seconds": 30}}})
    base = options_from_config(cfg, FIXTURE)
    assert base.formats == ["pptx"] and base.depth == "exec"
    assert base.classification == "Internal" and base.brand == "acme.example"
    assert base.helpers.icons is False and base.helpers.timeout_seconds == 30
    assert base.out_dir is None and base.harness_dir.name == "export"
    over = options_from_config(cfg, FIXTURE, formats=["html", "pdf"], depth=None,
                               classification="Secret", helpers={"timeout_seconds": 5},
                               out_dir="~/x")
    assert over.formats == ["html", "pdf"]
    assert over.depth == "exec"                        # None never clobbers config
    assert over.classification == "Secret"
    assert over.helpers.icons is False and over.helpers.timeout_seconds == 5
    assert over.out_dir == Path("~/x").expanduser()
    assert cfg.export.helpers.timeout_seconds == 30    # config object not mutated
    with pytest.raises(TypeError):
        options_from_config(cfg, FIXTURE, colour="red")


def test_doctor_reports_every_helper(monkeypatch):
    monkeypatch.setattr("shutil.which", lambda name: None)
    checks = api.doctor(Config())
    names = {c.name for c in checks}
    assert {"icons", "brand", "stock images", "diagrams", "LibreOffice (PDF)",
            "whitepaper template", "python: python-pptx"} <= names
    assert all(c.status in {"ok", "warn", "fail"} for c in checks)
    by_name = {c.name: c for c in checks}
    assert by_name["icons"].status == "warn" and by_name["whitepaper template"].status == "ok"
    assert all(set(c.to_dict()) == {"group", "name", "status", "detail"} for c in checks)


def test_missing_dependency_says_how_to_install(monkeypatch):
    real = api.importlib.import_module

    def fake(name, *a, **k):
        if name == "pptx":
            raise ImportError(name)
        return real(name, *a, **k)

    monkeypatch.setattr(api.importlib, "import_module", fake)
    with pytest.raises(api.ExportDependencyError, match="uv sync --extra export"):
        api.check_dependencies(["pptx"])


def test_agent_authoring_falls_back_when_claude_is_missing(tmp_path, monkeypatch):
    import vantage.export.agents as agents

    monkeypatch.setattr(agents.shutil, "which", lambda name: None)
    result = export(ExportOptions(dossier=FIXTURE, formats=["html"], out_dir=tmp_path,
                                  authoring="agents", client_logo=False,
                                  helpers=ExportHelpersCfg(icons=False, brand=False,
                                                           stock_images=False, diagrams="none")))
    assert any("agent authoring unavailable" in w for w in result.warnings)
    assert result.plans == {"deck": "scaffold", "doc": "scaffold", "site": "scaffold"}
    assert (tmp_path / "plan" / ".scaffold.json").exists()


def test_agent_authoring_runs_the_workflow(tmp_path, monkeypatch):
    import vantage.export.agents as agents

    seen = {}

    class FakeProc:
        stdout = iter(["phase P1 Narrative\n", "done\n"])

        def wait(self):
            plan = tmp_path / "plan" / "site.json"
            data = json.loads(plan.read_text())
            data["pages"][0]["summary"] = "Written by the site-plan agent."
            plan.write_text(json.dumps(data))
            return 0

    def popen(argv, **kwargs):
        seen["argv"] = argv
        seen["cwd"] = kwargs["cwd"]
        return FakeProc()

    monkeypatch.setattr(agents.shutil, "which", lambda name: "/fake/claude")
    monkeypatch.setattr(agents.subprocess, "Popen", popen)
    events = []
    result = export(ExportOptions(dossier=FIXTURE, formats=["html"], out_dir=tmp_path,
                                  authoring="agents", client_logo=False,
                                  helpers=ExportHelpersCfg(icons=False, brand=False,
                                                           stock_images=False, diagrams="none")),
                    emit=events.append)
    prompt = seen["argv"][2]
    assert seen["argv"][1] == "-p"
    assert "vantage-export.workflow.mjs" in prompt and '"render": false' in prompt
    assert result.plans["site"] == "authored" and result.plans["deck"] == "scaffold"
    assert any(e.type == "log" and e.agent == "export-workflow" for e in events)
    page = Path(result.artifacts[0]["path"]).read_text(encoding="utf8")
    assert "Written by the site-plan agent." in page
