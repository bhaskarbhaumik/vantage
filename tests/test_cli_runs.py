"""``vantage runs`` and vantage.runs discovery on a fake output dir."""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest
from typer.testing import CliRunner

from vantage import cli, runs
from vantage.cli import common

runner = CliRunner()


def _write(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(data if isinstance(data, str) else json.dumps(data))


@pytest.fixture
def tree(tmp_path, monkeypatch):
    for var in ("VANTAGE_CONFIG", "VANTAGE_OUTPUT_DIR"):
        monkeypatch.delenv(var, raising=False)
    out = tmp_path / "out"
    full = out / "acme-2026-10"
    _write(full / "acme-2026-10-vantage.md", "# Acme\n")
    _write(full / "state" / "state.json", {
        "run_contract": {"entity": {"legal_name": "Acme Corporation", "common_name": "Acme"},
                         "tier": "STANDARD", "as_of": "2026-10-01"},
        "verification": {"result": "FAIL", "overall_confidence": "Insufficient", "eqi": 10,
                         "blockers": 9, "majors": 9, "minors": 9},
    })
    _write(full / "qa" / "verification-report.json", {
        "result": "PASS WITH DISCLOSURES", "overall_confidence": "Thin", "eqi": 58.9,
        "blockers": 4, "majors": 8, "minors": 3, "checks": [1, 2, 3]})
    _write(full / "sections" / "01-exec-brief.md", "x")
    _write(full / "sections" / "00-run-contract.md", "x")
    _write(full / "exports" / "manifest.json",
           {"artifacts": [{"format": "pptx", "path": "acme.pptx"},
                          {"format": "pdf", "path": str(tmp_path / "abs.pdf")}]})
    partial = out / "beta-2026-09"
    _write(partial / "run.jsonl", json.dumps({"type": "run_start", "message": "Beta Ltd",
                                              "data": {"tier": "EXECUTIVE"}}) + "\n")
    _write(out / "not-a-run" / "notes.txt", "x")
    os.utime(partial, (1_000_000, 1_000_000))
    os.utime(partial / "run.jsonl", (1_000_000, 1_000_000))
    cfg = tmp_path / "config.json"
    cfg.write_text(json.dumps({"engine": {"output_dir": str(out)}}))
    return out, cfg


def test_discover_reads_state_verification_and_exports(tree):
    out, _ = tree
    found = runs.discover(out)
    assert [r["slug"] for r in found] == ["acme-2026-10", "beta-2026-09"]
    acme, beta = found
    assert acme["client"] == "Acme Corporation"
    assert (acme["as_of"], acme["tier"]) == ("2026-10-01", "STANDARD")
    assert acme["dossier"].endswith("acme-2026-10-vantage.md")
    # the final QA report wins over the in-state copy
    assert acme["verification"] == {"result": "PASS WITH DISCLOSURES",
                                    "overall_confidence": "Thin", "eqi": 58.9,
                                    "blockers": 4, "majors": 8, "minors": 3}
    assert acme["exports"] == [str(out / "acme-2026-10" / "exports" / "acme.pptx"),
                               str(out.parent / "abs.pdf")]
    assert beta == {"slug": "beta-2026-09", "run_dir": str(out / "beta-2026-09"),
                    "dossier": None, "client": "Beta Ltd", "as_of": None, "tier": "EXECUTIVE",
                    "mtime": beta["mtime"], "verification": None, "exports": []}
    assert runs.discover(out / "missing") == []
    assert runs.find_run(out, "../out") is None
    assert runs.find_run(out, "not-a-run") is None


def test_runs_list_and_show_json_contract(tree):
    out, cfg = tree
    res = runner.invoke(cli.app, ["--config", str(cfg), "runs", "list", "--json"])
    assert res.exit_code == 0, res.output
    listed = json.loads(res.stdout)["runs"]
    keys = {"slug", "run_dir", "dossier", "client", "as_of", "tier", "mtime", "verification",
            "exports"}
    assert all(set(r) == keys for r in listed)
    assert isinstance(listed[0]["mtime"], float)

    res = runner.invoke(cli.app, ["runs", "show", "acme-2026-10", "--json", "--config", str(cfg)])
    shown = json.loads(res.stdout)
    assert set(shown) == keys | {"sections"}
    assert shown["sections"] == ["00-run-contract.md", "01-exec-brief.md"]
    assert runner.invoke(cli.app, ["--config", str(cfg), "runs", "show", "nope"]).exit_code == 1

    res = runner.invoke(cli.app, ["--config", str(cfg), "--ascii", "runs", "list"])
    assert res.exit_code == 0 and "acme" in res.stderr and res.stdout == ""
    res = runner.invoke(cli.app, ["--config", str(cfg), "runs", "list", "-n", "1", "--json"])
    assert len(json.loads(res.stdout)["runs"]) == 1


def test_runs_path_open_and_output_dir_override(tree, tmp_path, monkeypatch):
    out, cfg = tree
    res = runner.invoke(cli.app, ["--config", str(cfg), "runs", "path", "acme-2026-10"])
    assert res.stdout.strip() == str(out / "acme-2026-10")
    res = runner.invoke(cli.app, ["--config", str(cfg), "runs", "path", "acme-2026-10",
                                  "--dossier"])
    assert res.stdout.strip().endswith("acme-2026-10-vantage.md")
    assert runner.invoke(cli.app, ["--config", str(cfg), "runs", "path", "beta-2026-09",
                                   "--dossier"]).exit_code == 1
    opened: list = []
    monkeypatch.setattr("vantage.cli.runs_cmd.open_path", opened.append)
    assert runner.invoke(cli.app, ["--config", str(cfg), "runs", "open", "acme-2026-10"]
                         ).exit_code == 0
    assert opened[-1].name == "acme-2026-10-vantage.md"
    empty = tmp_path / "empty"
    empty.mkdir()
    res = runner.invoke(cli.app, ["--config", str(cfg), "--output-dir", str(empty), "runs",
                                  "list", "--json"])
    assert json.loads(res.stdout) == {"runs": []}


def test_runs_rm_confirms_unless_yes(tree):
    out, cfg = tree
    base = ["--config", str(cfg), "runs", "rm"]
    res = runner.invoke(cli.app, base + ["beta-2026-09"], input="n\n")
    assert res.exit_code == 1 and (out / "beta-2026-09").exists()
    res = runner.invoke(cli.app, base + ["beta-2026-09"], input="y\n")
    assert res.exit_code == 0 and not (out / "beta-2026-09").exists()
    res = runner.invoke(cli.app, base + ["acme-2026-10", "--yes"])
    assert res.exit_code == 0 and not (out / "acme-2026-10").exists()
    assert runner.invoke(cli.app, base + ["not-a-run", "--yes"]).exit_code == 1
    assert (out / "not-a-run").exists()


def test_slug_completion_uses_output_dir(tree, monkeypatch):
    out, cfg = tree
    from vantage.models.config import Config

    monkeypatch.setattr(cli, "load_config",
                        lambda *a, **k: Config.model_validate({"engine": {"output_dir": str(out)}}))
    assert common.complete_slugs("a") == ["acme-2026-10"]
    assert common.complete_slugs("") == ["acme-2026-10", "beta-2026-09"]
