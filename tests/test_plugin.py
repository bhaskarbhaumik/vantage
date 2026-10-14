"""The repository installs as the `vantage` Claude Code plugin.

Checks the plugin and marketplace manifests, and that every plugin skill under `skills/` has valid
frontmatter, so the skills surface as `/vantage:generate` and `/vantage:export`.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

import vantage

ROOT = Path(__file__).resolve().parent.parent
PLUGIN_DIR = ROOT / ".claude-plugin"
SKILLS_DIR = ROOT / "skills"
EXPECTED_SKILLS = {"generate", "export"}
KEBAB = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
REPO_URL = "https://github.com/bhaskarbhaumik/vantage"


def parse_frontmatter(text: str) -> dict[str, str]:
    """Parse the YAML frontmatter subset skills use: scalars and folded/literal blocks."""
    lines = text.splitlines()
    assert lines and lines[0] == "---", "SKILL.md must start with '---'"
    try:
        end = lines.index("---", 1)
    except ValueError:
        pytest.fail("SKILL.md frontmatter is not closed with '---'")
    fields: dict[str, str] = {}
    key: str | None = None
    block: list[str] = []
    for line in lines[1:end]:
        if line.startswith((" ", "\t")) and key is not None:
            block.append(line.strip())
            continue
        if key is not None and block:
            fields[key] = " ".join(block)
        key, block = None, []
        match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        assert match, f"unparseable frontmatter line: {line!r}"
        name, value = match.groups()
        if value in {">", ">-", "|", "|-"}:
            key = name
        else:
            fields[name] = value.strip().strip("'\"")
    if key is not None:
        fields[key] = " ".join(block)
    return fields


def _load(name: str) -> dict:
    return json.loads((PLUGIN_DIR / name).read_text(encoding="utf-8"))


def _skill_dirs() -> list[Path]:
    return sorted(p.parent for p in SKILLS_DIR.glob("*/SKILL.md"))


# ── manifests ──────────────────────────────────────────────────────────────────


def test_plugin_manifest():
    plugin = _load("plugin.json")
    assert plugin["name"] == "vantage"
    assert KEBAB.match(plugin["name"])
    assert plugin["version"] == vantage.__version__
    assert plugin["description"]
    assert plugin["author"]["name"]
    assert plugin["homepage"] == REPO_URL
    assert plugin["repository"] == REPO_URL
    assert plugin["license"] == "MIT"
    assert plugin["keywords"] and all(isinstance(k, str) for k in plugin["keywords"])


def test_plugin_manifest_uses_default_component_dirs():
    """Skills are auto-discovered from ./skills; custom paths would only add locations."""
    plugin = _load("plugin.json")
    for key in ("skills", "commands", "agents", "hooks", "mcpServers"):
        assert key not in plugin, f"unexpected component path override: {key}"


def test_marketplace_manifest():
    market = _load("marketplace.json")
    assert market["name"] == "vantage", "install id must be vantage@vantage"
    assert market["owner"]["name"]
    entries = {p["name"]: p for p in market["plugins"]}
    assert set(entries) == {"vantage"}
    entry = entries["vantage"]
    assert entry["source"] == "./"
    assert entry.get("version", vantage.__version__) == vantage.__version__
    assert entry["description"]


# ── skills ─────────────────────────────────────────────────────────────────────


def test_generate_skill_exists():
    assert (SKILLS_DIR / "generate" / "SKILL.md").is_file()


def test_only_expected_skills():
    names = {p.name for p in _skill_dirs()}
    assert names <= EXPECTED_SKILLS, f"unexpected plugin skills: {names - EXPECTED_SKILLS}"


@pytest.mark.parametrize("name", sorted(EXPECTED_SKILLS))
def test_skill_frontmatter(name: str):
    path = SKILLS_DIR / name / "SKILL.md"
    if not path.exists():
        pytest.skip(f"skills/{name} not present yet")
    fields = parse_frontmatter(path.read_text(encoding="utf-8"))
    assert fields.get("name") == name, "frontmatter name must match the directory"
    assert KEBAB.match(fields["name"])
    description = fields.get("description", "")
    assert 20 <= len(description) <= 1024, "description must say when to use the skill"


def test_project_alias_skill():
    """`/vantage` (project skill + command) stays available and points at the plugin skill."""
    skill = ROOT / ".claude" / "skills" / "vantage" / "SKILL.md"
    text = skill.read_text(encoding="utf-8")
    assert parse_frontmatter(text)["name"] == "vantage"
    assert "skills/generate/SKILL.md" in text
    assert (ROOT / ".claude" / "commands" / "vantage.md").is_file()


def test_generate_skill_resolves_repo_from_plugin_root():
    text = (SKILLS_DIR / "generate" / "SKILL.md").read_text(encoding="utf-8")
    assert "${CLAUDE_PLUGIN_ROOT}" in text
    assert "VANTAGE_REPO" in text
    assert "/vantage:export" in text


def test_plugin_files_use_only_vantage_naming():
    paths = [PLUGIN_DIR / "plugin.json", PLUGIN_DIR / "marketplace.json"]
    paths += [d / "SKILL.md" for d in _skill_dirs()]
    paths += [ROOT / ".claude" / "skills" / "vantage" / "SKILL.md"]
    paths += [ROOT / ".claude" / "commands" / "vantage.md"]
    # The legacy token is assembled at runtime so this guard does not trip repo-wide greps.
    token = "a" + "id"
    legacy = re.compile(rf"\b{token}\b|{token}[-_]", re.IGNORECASE)
    for path in paths:
        assert not legacy.search(path.read_text(encoding="utf-8")), f"legacy name in {path}"
