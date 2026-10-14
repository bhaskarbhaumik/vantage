# Repository Guidelines

## Project Structure & Module Organization

Vantage combines a Python research engine with a TypeScript/React Ink terminal UI.
- `src/vantage/`: engine code. `cli/` is the `vantage` command (Typer; `flags.py` turns every config key into a flag), `pipeline/` orchestrates stages, `agents/` executes briefs, `engine/` implements the six backends, `render/` assembles dossiers, and `export/` renders dossiers to PPTX, DOCX, PDF and HTML.
- `tui/src/`: the Ink terminal UI (`vantage-tui`); compiled output goes to `tui/dist/`, tests live in `tui/test/`.
- `harness/`: versioned blueprint, agent briefs, contracts, schemas, and workflows loaded at runtime. Start with `harness/ARCHITECTURE.md` for dossier design. `harness/export/` is the export harness (plan briefs, blueprints, plan schemas, workflow).
- `skills/` (`generate`, `export`) and `.claude-plugin/` make the repo a Claude Code plugin; `.claude/` holds the project `/vantage` skill and command.
- `completions/`: generated bash, zsh and fish scripts for `vantage` and `vantage-engine`.
- `tests/`: Python tests. `config/` holds shipped defaults and the generated JSON schema; `docs/` (user docs; `docs/reference/cli.md` is generated), `scripts/`, and `deploy/` contain documentation, utilities, and deployment resources.

## Build, Test, and Development Commands

Use `uv` with the pinned Python 3.14 (3.12+ supported) and Node.js 18.19 or newer.

- `uv sync --extra dev`: install the engine, the export extra, and development tools. Include additional extras in the same invocation to retain them.
- `npm ci`: install locked UI dependencies and run the prepare build.
- `npm run dev`: launch the terminal UI from source.
- `npm run build`: compile TypeScript to `tui/dist/`; `npm start` launches the compiled UI.
- `npm run typecheck`: validate TypeScript without emitting files. `npm test`: TUI tests.
- `uv run vantage doctor`: check local configuration, backend, export and TUI readiness. `vantage-engine` is an alias of `vantage`.
- `uv run vantage --help`, `uv run vantage options`: commands and every flag.
- `uv run python -m pytest -q`: run the Python suite.
- `uv run ruff check src tests scripts`: lint Python and check imports.
- `uv run python scripts/generate-cli-reference.py`: regenerate `docs/reference/cli.md` after changing commands, options or config keys (`tests/test_docs.py` fails when it is stale). `scripts/generate-config-schema.py` regenerates `config/default.schema.json`.
- `uv build`: build Python distribution artifacts with Hatchling.

## Coding Style & Naming Conventions

Use four-space Python indentation, type annotations, `snake_case` functions/modules, and `PascalCase` classes. Ruff targets Python 3.12 syntax with a 100-character line-length setting. Match existing TypeScript style: two-space indentation, single quotes, semicolons, `camelCase` functions, and `PascalCase` React components. TypeScript strict mode is enabled.

## Testing Guidelines

Use pytest and pytest-asyncio; async mode is automatic. Name files `tests/test_*.py` and functions `test_*`. Add regression coverage for changed behavior, using temporary directories and mocked providers to keep tests deterministic; never call the network or a paid API. Run a focused file with `uv run pytest tests/test_pipeline.py -q`. No numeric coverage threshold is configured.

## Versioning & Changelog

The package version is single-sourced in `src/vantage/__init__.py`; `package.json` must match. Do not edit versions by hand: maintainers run `uv run python scripts/bump-version.py minor|major|patch` (and `--check`). Add user-visible changes under `## [Unreleased]` in `CHANGELOG.md`. The harness (v3.0.0), config schema (2.2) and state schema (3.0) carry their own versions; see `VERSION.md`.

## Commit & Pull Request Guidelines

Use Conventional Commits (`feat:`, `fix:`, `docs:` …) with concise, imperative subjects. PRs should explain the change, link relevant issues, and list validation commands/results. Include terminal screenshots for UI changes and document configuration, harness or `--json` contract impacts. See `CONTRIBUTING.md`.

## Security & Configuration

Copy `.env.example` to `.env` for local configuration; keep credentials in environment variables. Preserve subscription-first authentication and explicit opt-in API billing (`--auth api-key`); a change that could make a run metered without the user asking is a bug. Never commit secrets or generated dossiers. Keep `uv.lock` and `package-lock.json` tracked.
