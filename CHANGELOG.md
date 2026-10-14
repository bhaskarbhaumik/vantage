# Changelog

All notable changes to Vantage are documented in this file.

The format is based on [Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/), and this
project adheres to [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html). The version
recorded here is the engine package version; the harness, config schema and state schema carry
their own version lines (see [VERSION.md](VERSION.md)).

## [Unreleased]

## [0.2.0] - 2026-10-14

### Added

- **P7R owner remediation (harness).** After verification, `remediation-router` (brief 26a) turns
  BLOCKER findings (with confined MAJORs riding along) into work orders for the agents that own
  the defective text; owners
  revise only their own section under brief 26b, in dependency order, and a fresh verifier re-runs
  every check. §21.8 records each round as fixed, partly fixed, not fixed, regressed or declined.
  `vantage run --remediation-rounds 0|1|2` sets the number of rounds (default 1; workflow backend).
- **Synthesis re-sync cascade.** When a register or body owner rewrites, every synthesis owner
  downstream of it (§18–§20, §1) is re-dispatched to re-sync, even when no finding names its text.
- **`vantage export`** turns a finished dossier into collateral: PowerPoint (`.pptx`), Word
  (`.docx`), PDF, and a self-contained HTML microsite or HTML deck. Supports `exec`, `standard`
  and `full` depth, deterministic or agent-authored plans, and an export manifest.
  - Brand theming from `--brand <domain>` via the `get-brand` helper.
  - Icons via `get-icon` and stock imagery via `get-stock`.
  - Diagrams via `dgm`, draw.io or Mermaid; Napkin illustrations (opt-in).
  - Charts rendered with matplotlib (static formats) and Plotly (HTML) from
    `vantage-chart/v1` blocks.
  - `artifact` run events so the CLI and TUI can show export progress.
- **CLI overhaul.** `vantage` is now the primary command (`vantage-engine` remains as an alias).
  Every configuration option is available as a flag, plus a generic `--set <dotted.key>=<value>`.
  New `runs`, `config` and `completion` command groups, with bash, zsh and fish completion.
  `--json` output contracts for `run`, `export`, `runs`, `doctor`, `backends`, `config` and
  `version`.
- **Ink TUI** as `vantage-tui` (or `vantage --tui`), with Nerd Font icons by default and
  `--ascii`, `--icons`, `--theme`, `--no-color` and `--no-animations` presentation flags.
- **Config schema 2.2** with new `export` and `ui` sections.
- **Claude Code plugin.** The repository installs as the `vantage` plugin, providing
  `/vantage:generate` and `/vantage:export`; the project-level `/vantage` command remains.
- Community and governance files: `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`,
  `SUPPORT.md`, `GOVERNANCE.md`, `AUTHORS.md`, `VERSION.md`, issue forms, a pull request
  template, CI and release workflows, Dependabot, `.editorconfig` and `.gitattributes`.
- `scripts/bump-version.py` to bump and check the package version across all manifests.

### Changed

- The package version is single-sourced from `src/vantage/__init__.py`; `pyproject.toml` reads it
  dynamically and `package.json` must match.
- The terminal UI source moved from `cli/` to `tui/`.
- `scripts/install-skill.sh` now prints the plugin install instructions and only symlinks the
  `/vantage` skill and command with `--link`.
- Documentation revamp across the README and `docs/`.

### Removed

- All legacy pre-Vantage naming, identifiers and paths.
- Superseded harness versions; `harness/` now carries only the v3.0.0 blueprint.
- The backout script.

### Fixed

- Refuted and weakened claims are no longer left asserted in §3–§17 with only an annotation;
  qualifiers lost in the body no longer survive unchanged into §18–§20 and §1.
- A resumed workflow run can no longer replay a stale merge or verdict from cache after the set of
  remediation owners changes.

## [0.1.0] - 2026-10-03

### Added

- Initial public baseline of Vantage: the v3.0.0 harness (22 sections, 29 agents, 12 steps), the
  Python engine with six execution backends (`workflow`, `api`, `agent-sdk`, `langgraph`, `adk`,
  `crewai`), subscription-first authentication, the Ink terminal UI, the `/vantage` Claude Code
  skill and command, and cloud deployment targets for GCP, Azure and AWS.

[Unreleased]: https://github.com/bhaskarbhaumik/vantage/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/bhaskarbhaumik/vantage/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/bhaskarbhaumik/vantage/releases/tag/v0.1.0
