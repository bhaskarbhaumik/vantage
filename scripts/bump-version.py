#!/usr/bin/env python3
"""Bump or check the Vantage package version across every manifest that carries it.

The single source is ``src/vantage/__init__.py`` (``__version__``); ``pyproject.toml`` reads it
dynamically. This script keeps the copies in step:

* ``package.json`` ``version``
* ``package-lock.json`` root ``version`` and ``packages[""].version`` (and the root ``name``,
  which npm derives from ``package.json``)
* ``.claude-plugin/plugin.json`` ``version`` and the ``vantage`` entry in
  ``.claude-plugin/marketplace.json``
* ``CHANGELOG.md``: the ``[Unreleased]`` section becomes a dated release section, a fresh empty
  ``[Unreleased]`` goes above it, and the compare links at the bottom are updated.

Usage::

    python scripts/bump-version.py patch|minor|major|X.Y.Z [--date YYYY-MM-DD] [--dry-run]
    python scripts/bump-version.py --check

Passing the current version re-syncs the manifests without touching the changelog.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
REPO_URL = "https://github.com/bhaskarbhaumik/vantage"

SEMVER = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
)
INIT_RE = re.compile(r'^__version__\s*=\s*["\']([^"\']+)["\']', re.MULTILINE)
RELEASE_RE = re.compile(r"^## \[(\d+\.\d+\.\d+[^\]]*)\] - (\d{4}-\d{2}-\d{2})\s*$", re.MULTILINE)
UNRELEASED_RE = re.compile(r"^## \[Unreleased\]\s*$", re.MULTILINE)


@dataclass(frozen=True)
class Paths:
    root: Path

    @property
    def init(self) -> Path:
        return self.root / "src" / "vantage" / "__init__.py"

    @property
    def package_json(self) -> Path:
        return self.root / "package.json"

    @property
    def package_lock(self) -> Path:
        return self.root / "package-lock.json"

    @property
    def plugin_json(self) -> Path:
        return self.root / ".claude-plugin" / "plugin.json"

    @property
    def marketplace_json(self) -> Path:
        return self.root / ".claude-plugin" / "marketplace.json"

    @property
    def changelog(self) -> Path:
        return self.root / "CHANGELOG.md"


# ── reading ────────────────────────────────────────────────────────────────────


def read_init_version(paths: Paths) -> str:
    match = INIT_RE.search(paths.init.read_text(encoding="utf-8"))
    if not match:
        raise SystemExit(f"no __version__ in {paths.init}")
    return match.group(1)


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _dump_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def top_released_version(changelog_text: str) -> str | None:
    match = RELEASE_RE.search(changelog_text)
    return match.group(1) if match else None


def collect_versions(paths: Paths) -> dict[str, str | None]:
    """Every place the package version appears, keyed by a human-readable label."""
    found: dict[str, str | None] = {"src/vantage/__init__.py": read_init_version(paths)}
    if paths.package_json.exists():
        found["package.json"] = _load_json(paths.package_json).get("version")
    if paths.package_lock.exists():
        lock = _load_json(paths.package_lock)
        found["package-lock.json"] = lock.get("version")
        found['package-lock.json packages[""]'] = lock.get("packages", {}).get("", {}).get("version")
    if paths.plugin_json.exists():
        found[".claude-plugin/plugin.json"] = _load_json(paths.plugin_json).get("version")
    if paths.marketplace_json.exists():
        for plugin in _load_json(paths.marketplace_json).get("plugins", []):
            if plugin.get("name") == "vantage" and "version" in plugin:
                found[".claude-plugin/marketplace.json"] = plugin["version"]
    if paths.changelog.exists():
        found["CHANGELOG.md (top release)"] = top_released_version(
            paths.changelog.read_text(encoding="utf-8")
        )
    return found


# ── computing ──────────────────────────────────────────────────────────────────


def next_version(current: str, part: str) -> str:
    if SEMVER.match(part):
        return part
    core = re.match(r"^(\d+)\.(\d+)\.(\d+)", current)
    if not core:
        raise SystemExit(f"current version {current!r} is not SemVer")
    major, minor, patch = (int(x) for x in core.groups())
    if part == "major":
        return f"{major + 1}.0.0"
    if part == "minor":
        return f"{major}.{minor + 1}.0"
    if part == "patch":
        return f"{major}.{minor}.{patch + 1}"
    raise SystemExit(f"expected major, minor, patch or X.Y.Z, got {part!r}")


# ── writing ────────────────────────────────────────────────────────────────────


def write_init(paths: Paths, version: str) -> None:
    text = paths.init.read_text(encoding="utf-8")
    paths.init.write_text(INIT_RE.sub(f'__version__ = "{version}"', text, count=1), "utf-8")


def write_package_files(paths: Paths, version: str) -> None:
    if not paths.package_json.exists():
        return
    pkg = _load_json(paths.package_json)
    pkg["version"] = version
    _dump_json(paths.package_json, pkg)
    if paths.package_lock.exists():
        lock = _load_json(paths.package_lock)
        lock["name"] = pkg.get("name", lock.get("name"))
        lock["version"] = version
        root = lock.setdefault("packages", {}).setdefault("", {})
        root["name"] = lock["name"]
        root["version"] = version
        _dump_json(paths.package_lock, lock)


def write_plugin_files(paths: Paths, version: str) -> None:
    if paths.plugin_json.exists():
        plugin = _load_json(paths.plugin_json)
        plugin["version"] = version
        _dump_json(paths.plugin_json, plugin)
    if paths.marketplace_json.exists():
        market = _load_json(paths.marketplace_json)
        for entry in market.get("plugins", []):
            if entry.get("name") == "vantage" and "version" in entry:
                entry["version"] = version
        _dump_json(paths.marketplace_json, market)


def bump_changelog(text: str, version: str, date: str) -> str:
    """Turn ``[Unreleased]`` into ``[version] - date`` and refresh the compare links."""
    if re.search(rf"^## \[{re.escape(version)}\]", text, re.MULTILINE):
        return text
    previous = top_released_version(text)
    unreleased = UNRELEASED_RE.search(text)
    if not unreleased:
        raise SystemExit("CHANGELOG.md has no '## [Unreleased]' heading")

    body_start = unreleased.end()
    next_heading = re.compile(r"^## \[", re.MULTILINE).search(text, body_start)
    link_block = re.compile(r"^\[[^\]]+\]: ", re.MULTILINE).search(text, body_start)
    candidates = [m.start() for m in (next_heading, link_block) if m]
    body_end = min(candidates) if candidates else len(text)
    body = text[body_start:body_end].strip()
    if not body:
        body = "### Changed\n\n- Describe the changes in this release."

    section = f"## [Unreleased]\n\n## [{version}] - {date}\n\n{body}\n\n"
    text = text[: unreleased.start()] + section + text[body_end:]

    link_re = re.compile(r"^\[Unreleased\]: .*$", re.MULTILINE)
    new_links = f"[Unreleased]: {REPO_URL}/compare/v{version}...HEAD\n"
    if previous:
        new_links += f"[{version}]: {REPO_URL}/compare/v{previous}...v{version}"
    else:
        new_links += f"[{version}]: {REPO_URL}/releases/tag/v{version}"
    if link_re.search(text):
        text = link_re.sub(new_links, text, count=1)
    else:
        text = text.rstrip("\n") + "\n\n" + new_links + "\n"
    return text


# ── commands ───────────────────────────────────────────────────────────────────


def check(paths: Paths) -> int:
    versions = collect_versions(paths)
    expected = versions["src/vantage/__init__.py"]
    width = max(len(k) for k in versions)
    bad = 0
    for label, value in versions.items():
        ok = value == expected
        bad += not ok
        print(f"{'ok ' if ok else 'BAD'}  {label:<{width}}  {value}")
    if bad:
        print(f"\n{bad} location(s) disagree with {expected}. "
              f"Run: python scripts/bump-version.py {expected}", file=sys.stderr)
        return 1
    print(f"\nall versions agree: {expected}")
    return 0


def bump(paths: Paths, part: str, date: str, dry_run: bool) -> int:
    current = read_init_version(paths)
    target = next_version(current, part)
    print(f"{current} -> {target}")
    if dry_run:
        return 0
    write_init(paths, target)
    write_package_files(paths, target)
    write_plugin_files(paths, target)
    if paths.changelog.exists():
        text = paths.changelog.read_text(encoding="utf-8")
        paths.changelog.write_text(bump_changelog(text, target, date), encoding="utf-8")
    print("updated manifests and CHANGELOG.md; edit the new changelog section, then run --check")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("part", nargs="?", help="major | minor | patch | X.Y.Z")
    parser.add_argument("--check", action="store_true", help="verify every copy agrees")
    parser.add_argument("--date", default=dt.date.today().isoformat(), help="release date")
    parser.add_argument("--dry-run", action="store_true", help="print the new version only")
    parser.add_argument("--root", type=Path, default=REPO, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    paths = Paths(args.root)
    if args.check:
        return check(paths)
    if not args.part:
        parser.error("give major, minor, patch or X.Y.Z (or --check)")
    return bump(paths, args.part, args.date, args.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
