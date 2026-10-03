# Repository Guidelines

## Project Structure & Module Organization

Vantage combines a Python research engine with a TypeScript/React Ink terminal UI.
- `src/vantage/`: engine code; `pipeline/` orchestrates stages, `agents/` executes briefs, `engine/` implements backends, and `render/` assembles dossiers.
- `cli/src/`: terminal UI; compiled output goes to `cli/dist/`.
- `harness/`: versioned blueprint, agent briefs, contracts, schemas, and workflows loaded at runtime. Start with `harness/ARCHITECTURE.md` for dossier design.
- `tests/`: Python tests. `config/` holds shipped defaults; `docs/`, `scripts/`, and `deploy/` contain documentation, utilities, and deployment resources.

## Build, Test, and Development Commands

Use `uv` with the pinned Python 3.14 and Node.js 18 or newer.

- `uv sync --extra dev`: install the engine and development tools. Include additional extras in the same invocation to retain them.
- `npm ci`: install locked UI dependencies and run the prepare build.
- `npm run dev`: launch the terminal UI from source.
- `npm run build`: compile TypeScript; `npm start` launches the compiled UI.
- `uv build`: build Python distribution artifacts with Hatchling.
- `uv run vantage-engine doctor`: check local configuration and backend readiness.
- `uv run python -m pytest -q`: run the Python suite.
- `uv run ruff check src tests`: lint Python and check imports.
- `npm run typecheck`: validate TypeScript without emitting files.

## Coding Style & Naming Conventions

Use four-space Python indentation, type annotations, `snake_case` functions/modules, and `PascalCase` classes. Ruff targets Python 3.12 syntax with a 100-character line-length setting. Match existing TypeScript style: two-space indentation, single quotes, semicolons, `camelCase` functions, and `PascalCase` React components. TypeScript strict mode is enabled.

## Testing Guidelines

Use pytest and pytest-asyncio; async mode is automatic. Name files `tests/test_*.py` and functions `test_*`. Add regression coverage for changed behavior, using temporary directories and mocked providers to keep tests deterministic. Run a focused file with `uv run pytest tests/test_pipeline.py -q`. No numeric coverage threshold is configured.

## Commit & Pull Request Guidelines

History currently contains only the initial commit, so no recurring commit convention is established. Use concise, imperative subjects. PRs should explain the change, link relevant issues, and list validation commands/results. Include terminal screenshots for UI changes and document configuration or harness compatibility impacts.

## Security & Configuration

Copy `.env.example` to `.env` for local configuration; keep credentials in environment variables. Preserve subscription-first authentication and explicit opt-in API billing. Never commit secrets or generated dossiers. Keep `uv.lock` and `package-lock.json` tracked.
