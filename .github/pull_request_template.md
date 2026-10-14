## What and why

<!-- What does this change, and why? Link issues with "Fixes #123". -->

## Validation

<!-- Commands you ran and their results. -->

- [ ] `uv run python -m pytest -q`
- [ ] `uv run ruff check src tests`
- [ ] `npm run typecheck` and `npm test` (if TypeScript changed)

## Checklist

- [ ] Tests added or updated for changed behaviour (deterministic: no network, no paid APIs)
- [ ] `CHANGELOG.md` updated under `## [Unreleased]`
- [ ] Docs updated (README, `docs/`, `--help` text) where behaviour or flags changed
- [ ] Harness changes keep prompts byte-stable unless invalidating resume caches is intended (explain below)
- [ ] Config, `--json` contract or harness compatibility impact described below (or none)
- [ ] Subscription-first authentication preserved; API billing stays opt-in
- [ ] No secrets, `.env` files, generated dossiers, run directories or exports committed
- [ ] Terminal screenshots attached for TUI changes

## Compatibility notes

<!-- Config keys, JSON output shapes, harness/blueprint, plugin skills. Write "None" if none. -->
