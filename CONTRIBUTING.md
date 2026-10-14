# Contributing to Vantage

Thanks for helping improve Vantage. This guide covers the development setup, the checks a pull
request must pass, and the rules for changing the harness without breaking resumed runs.

By participating you agree to follow the [Code of Conduct](CODE_OF_CONDUCT.md). Security issues go
through [SECURITY.md](SECURITY.md), never a public issue.

## Development setup

Requirements: [uv](https://docs.astral.sh/uv/) (it installs the pinned Python 3.14) and
Node.js 20 or newer.

```bash
git clone https://github.com/bhaskarbhaumik/vantage.git
cd vantage
uv sync --extra dev          # engine + test/lint tools (includes the export extra)
npm ci                       # locked TUI dependencies; runs the build via `prepare`
cp .env.example .env         # only if you need API-key backends; never commit .env
uv run vantage doctor        # check configuration and backend readiness
```

`uv sync --extra X` makes the environment match exactly that set of extras, so list every extra you
need in one call, for example `uv sync --extra dev --extra langgraph`.

Useful commands:

| Task | Command |
|---|---|
| Run the TUI from source | `npm run dev` |
| Python tests | `uv run python -m pytest -q` |
| One test file | `uv run python -m pytest tests/test_pipeline.py -q` |
| Python lint + import order | `uv run ruff check src tests` |
| TypeScript type check | `npm run typecheck` |
| TypeScript build | `npm run build` |
| TUI tests | `npm test` |
| Version consistency | `uv run python scripts/bump-version.py --check` |

Run all of them before you open a pull request. CI runs the same set on every push and pull request.

## Code style

- Python: four-space indentation, type annotations, `snake_case` functions and modules,
  `PascalCase` classes, 100-character lines. Ruff is the source of truth.
- TypeScript: two-space indentation, single quotes, semicolons, `camelCase` functions,
  `PascalCase` React components, strict mode.
- `.editorconfig` encodes these defaults for your editor.

## Tests

- Use pytest and pytest-asyncio (async mode is automatic). Name files `tests/test_*.py`.
- Add regression coverage for every behaviour change.
- Keep tests deterministic: temporary directories, mocked providers, mocked subprocess and HTTP.
  Tests must never call the network or a paid API.

## Commits, branches and pull requests

- Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/):
  `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `build:`, `ci:`, `chore:`, with an optional
  scope such as `feat(export):` or `fix(harness):`. Mark breaking changes with `!` and a
  `BREAKING CHANGE:` footer.
- Branch from `main` with a short descriptive name (`feat/export-depth`, `fix/runs-list-json`).
- Keep pull requests focused. Fill in the template: what changed, why, linked issues, and the
  validation commands you ran with their results. Include terminal screenshots for TUI changes.
- Document any configuration, harness or `--json` contract impact in the pull request.
- No Developer Certificate of Origin sign-off is required. By submitting a contribution you agree
  to license it under the project's [MIT License](LICENSE).

## Changing the harness safely

`harness/` is loaded at runtime and is the product. Read
[harness/ARCHITECTURE.md](harness/ARCHITECTURE.md) before you touch it.

- **Keep prompts byte-stable.** `prompts/system-vantage-analyst.md` is shared by every agent and is
  cached across them; any change, including whitespace, invalidates that cache for every agent.
  Change it only when the change is the point.
- **Respect resume caching.** A resumed workflow run replays an agent from cache only when its
  prompt and options are byte-identical. If you change how a prompt is composed in
  `harness/workflows/vantage-v3.workflow.mjs`, make sure first-pass prompts stay identical unless
  you intend to invalidate earlier runs, and say so in the pull request.
- **Keep the five registries in step** when you add an agent: the brief, `prompts/id-allocation.md`,
  `blueprint/section-contracts.md`, `src/vantage/blueprint/stages.py`, and `role_model_map` in
  `config/default.json`. `tests/test_blueprint.py` fails until they agree.
- **Do not let verification rewrite analysis.** Fixes go back to the owning agent (P7R); see
  design decision 7 in `ARCHITECTURE.md`.
- Never commit generated dossiers or run directories, even as test fixtures. Write small synthetic
  fixtures instead.
- Version the change: see the harness rules in [VERSION.md](VERSION.md).

## Changelog and versions

- Add a line under `## [Unreleased]` in [CHANGELOG.md](CHANGELOG.md) for every user-visible
  change, in the right group (Added, Changed, Deprecated, Removed, Fixed, Security). The format is
  [Keep a Changelog 1.1](https://keepachangelog.com/en/1.1.0/).
- Do not edit version numbers by hand. Maintainers run `scripts/bump-version.py` at release time;
  [VERSION.md](VERSION.md) describes the version lines and the release process.

## Configuration and secrets

- Credentials live in environment variables only. Never commit `.env`, keys, service-account files
  or generated dossiers.
- Preserve subscription-first authentication: API billing must stay an explicit opt-in
  (`--auth api-key`). A change that could make a run metered without the user asking is a bug.
- New config keys go in `src/vantage/models/config.py` and `config/default.json`, with the schema
  regenerated by `scripts/generate-config-schema.py`.

## Questions

See [SUPPORT.md](SUPPORT.md).
