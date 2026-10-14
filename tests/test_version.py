"""The package version is single-sourced and every copy of it agrees.

`src/vantage/__init__.py` is the source; `package.json`, the root of `package-lock.json`, the
installed distribution metadata, and the top released `CHANGELOG.md` entry must all match it. The
changelog must follow Keep a Changelog 1.1. `scripts/bump-version.py` is exercised against a
temporary copy of the manifests.
"""

from __future__ import annotations

import datetime as dt
import importlib.metadata
import importlib.util
import json
import re
import shutil
import sys
from pathlib import Path
from types import ModuleType

import pytest

import vantage

ROOT = Path(__file__).resolve().parent.parent
CHANGELOG = ROOT / "CHANGELOG.md"
SEMVER = re.compile(r"^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$")
RELEASE_HEADING = re.compile(r"^## \[(?P<version>[^\]]+)\] - (?P<date>\d{4}-\d{2}-\d{2})$")
CHANGE_TYPES = {"Added", "Changed", "Deprecated", "Removed", "Fixed", "Security"}
REPO_URL = "https://github.com/bhaskarbhaumik/vantage"


def _bump_module() -> ModuleType:
    if "bump_version" in sys.modules:
        return sys.modules["bump_version"]
    spec = importlib.util.spec_from_file_location("bump_version", ROOT / "scripts" / "bump-version.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["bump_version"] = module  # dataclasses resolves annotations via sys.modules
    spec.loader.exec_module(module)
    return module


def _version_tuple(version: str) -> tuple[int, ...]:
    return tuple(int(part) for part in re.match(r"^(\d+)\.(\d+)\.(\d+)", version).groups())


def _changelog_lines() -> list[str]:
    return CHANGELOG.read_text(encoding="utf-8").splitlines()


# ── single source ──────────────────────────────────────────────────────────────


def test_version_is_semver():
    assert SEMVER.match(vantage.__version__)


def test_package_json_matches():
    pkg = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
    assert pkg["version"] == vantage.__version__


def test_package_lock_root_matches():
    pkg = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
    lock = json.loads((ROOT / "package-lock.json").read_text(encoding="utf-8"))
    assert lock["name"] == pkg["name"]
    assert lock["version"] == vantage.__version__
    assert lock["packages"][""]["version"] == vantage.__version__


def test_installed_metadata_matches():
    assert importlib.metadata.version("vantage") == vantage.__version__


def test_pyproject_reads_version_dynamically():
    text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert 'dynamic = ["version"]' in text
    assert 'path = "src/vantage/__init__.py"' in text
    assert not re.search(r'^version\s*=', text, re.MULTILINE)


def test_top_changelog_release_matches():
    for line in _changelog_lines():
        match = RELEASE_HEADING.match(line)
        if match:
            assert match["version"] == vantage.__version__
            return
    pytest.fail("CHANGELOG.md has no released version")


def test_bump_script_check_agrees():
    assert _bump_module().main(["--check"]) == 0


# ── Keep a Changelog 1.1 ───────────────────────────────────────────────────────


def test_changelog_structure():
    lines = _changelog_lines()
    assert lines[0] == "# Changelog"
    level2 = [line for line in lines if line.startswith("## ")]
    assert level2[0] == "## [Unreleased]", "the first section must be [Unreleased]"

    releases = [RELEASE_HEADING.match(line) for line in level2[1:]]
    assert all(releases), f"malformed release heading in {level2[1:]}"
    versions = [m["version"] for m in releases]
    dates = [dt.date.fromisoformat(m["date"]) for m in releases]
    assert all(SEMVER.match(v) for v in versions)
    assert len(set(versions)) == len(versions), "duplicate release"
    assert [_version_tuple(v) for v in versions] == sorted(
        (_version_tuple(v) for v in versions), reverse=True
    ), "releases must be newest first"
    assert dates == sorted(dates, reverse=True), "release dates must be newest first"


def test_changelog_change_types():
    for line in _changelog_lines():
        if line.startswith("### "):
            assert line[4:] in CHANGE_TYPES, f"unknown change type: {line}"


def test_changelog_link_references():
    text = CHANGELOG.read_text(encoding="utf-8")
    refs = dict(re.findall(r"^\[([^\]]+)\]: (\S+)$", text, re.MULTILINE))
    assert refs["Unreleased"] == f"{REPO_URL}/compare/v{vantage.__version__}...HEAD"
    versions = [m["version"] for m in map(RELEASE_HEADING.match, _changelog_lines()) if m]
    for newer, older in zip(versions, versions[1:], strict=False):
        assert refs[newer] == f"{REPO_URL}/compare/v{older}...v{newer}"
    assert refs[versions[-1]] == f"{REPO_URL}/releases/tag/v{versions[-1]}"


# ── bump-version.py ────────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    ("current", "part", "expected"),
    [
        ("0.2.0", "patch", "0.2.1"),
        ("0.2.3", "minor", "0.3.0"),
        ("0.2.3", "major", "1.0.0"),
        ("0.2.3", "1.4.0-rc.1", "1.4.0-rc.1"),
    ],
)
def test_next_version(current: str, part: str, expected: str):
    assert _bump_module().next_version(current, part) == expected


def test_next_version_rejects_garbage():
    with pytest.raises(SystemExit):
        _bump_module().next_version("0.2.0", "huge")


@pytest.fixture
def repo_copy(tmp_path: Path) -> Path:
    for rel in (
        "src/vantage/__init__.py",
        "package.json",
        "package-lock.json",
        "CHANGELOG.md",
        ".claude-plugin/plugin.json",
        ".claude-plugin/marketplace.json",
    ):
        source = ROOT / rel
        if source.exists():
            (tmp_path / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, tmp_path / rel)
    # Start from a consistent tree so the test does not depend on the live lockfile state.
    _bump_module().main([vantage.__version__, "--root", str(tmp_path)])
    return tmp_path


def test_bump_updates_every_manifest(repo_copy: Path):
    bump = _bump_module()
    target = bump.next_version(vantage.__version__, "minor")
    (repo_copy / "CHANGELOG.md").write_text(
        (repo_copy / "CHANGELOG.md")
        .read_text(encoding="utf-8")
        .replace("## [Unreleased]\n", "## [Unreleased]\n\n### Fixed\n\n- A thing.\n", 1),
        encoding="utf-8",
    )
    assert bump.main(["minor", "--date", "2030-01-02", "--root", str(repo_copy)]) == 0

    init = (repo_copy / "src/vantage/__init__.py").read_text(encoding="utf-8")
    assert f'__version__ = "{target}"' in init
    assert json.loads((repo_copy / "package.json").read_text())["version"] == target
    lock = json.loads((repo_copy / "package-lock.json").read_text())
    assert lock["version"] == lock["packages"][""]["version"] == target
    plugin = repo_copy / ".claude-plugin/plugin.json"
    if plugin.exists():
        assert json.loads(plugin.read_text())["version"] == target

    changelog = (repo_copy / "CHANGELOG.md").read_text(encoding="utf-8")
    assert f"## [Unreleased]\n\n## [{target}] - 2030-01-02\n\n### Fixed\n\n- A thing.\n" in changelog
    assert f"[Unreleased]: {REPO_URL}/compare/v{target}...HEAD" in changelog
    assert f"[{target}]: {REPO_URL}/compare/v{vantage.__version__}...v{target}" in changelog
    assert bump.main(["--check", "--root", str(repo_copy)]) == 0


def test_bump_to_current_version_leaves_changelog_alone(repo_copy: Path):
    before = (repo_copy / "CHANGELOG.md").read_text(encoding="utf-8")
    assert _bump_module().main([vantage.__version__, "--root", str(repo_copy)]) == 0
    assert (repo_copy / "CHANGELOG.md").read_text(encoding="utf-8") == before


def test_check_reports_drift(repo_copy: Path):
    pkg_path = repo_copy / "package.json"
    pkg = json.loads(pkg_path.read_text())
    pkg["version"] = "9.9.9"
    pkg_path.write_text(json.dumps(pkg))
    assert _bump_module().main(["--check", "--root", str(repo_copy)]) == 1
