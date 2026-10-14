# Versioning and releases

Vantage carries four independent version lines. Only the first one is "the version" of a release;
the others describe contracts that change on their own schedule.

| Line | Current | Single source | Bumps when |
|---|---|---|---|
| Engine package | **0.2.0** | `src/vantage/__init__.py` (`__version__`) | Every release |
| Harness / blueprint | **v3.0.0** | `harness/` (blueprint, briefs, workflow) | The dossier structure or agent contracts change |
| Config schema | **2.2** | `config/default.json` (`"version"`) | Keys are added, renamed or removed in the config |
| State schema | **3.0** | `harness/state/state.schema.json`, `src/vantage/models/state.py` | The run-state handoff contract changes |

## Engine package — Semantic Versioning 2.0

The package follows [SemVer 2.0.0](https://semver.org/spec/v2.0.0.html). `pyproject.toml` reads
the version dynamically from `src/vantage/__init__.py`, and `package.json` (plus the root entries in
`package-lock.json`) must carry the same value. `tests/test_version.py` fails if they disagree, if
the installed metadata disagrees, or if the top released entry in `CHANGELOG.md` is a different
version.

### Pre-1.0 rules

While the major version is `0`, the public surface is still settling:

- **Minor** (`0.x.0`): new features, and any breaking change to the CLI, the `--json` output
  contracts, the config schema, the Python API, or the plugin skills. Breaking changes are called
  out under **Changed** or **Removed** in the changelog with a migration note.
- **Patch** (`0.x.y`): backwards-compatible bug fixes, documentation and dependency updates.

From `1.0.0` the usual rules apply: breaking changes require a major bump.

### What counts as the public surface

- The `vantage` / `vantage-engine` commands, their flags and `--json` output shapes.
- `vantage-tui` and its flags.
- `~/.config/vantage/default.json` keys and their meaning.
- `vantage.export.api` and other documented Python entry points.
- The Claude Code plugin skills (`/vantage:generate`, `/vantage:export`) and the `/vantage` command.
- The dossier file name (`<slug>-vantage.md`) and the `vantage-chart/v1` / `vantage-figure/v1`
  block schemas.

## The other version lines

- **Harness / blueprint (v3.0.0).** Bump the major version when the section structure, the agent
  roster, or a section contract changes in a way that makes old dossiers incomparable. Bump the
  minor version for new checks, briefs or vertical/jurisdiction modules that keep the structure.
  Prompt wording fixes that keep the contract are a patch. A harness bump always ships in an
  engine release and is noted in the changelog.
- **Config schema (2.2).** Bump the minor version when keys are added; bump the major version when
  keys are renamed or removed, and ship a migration in `vantage config` so existing user configs
  keep loading. Regenerate the JSON schema with `scripts/generate-config-schema.py`.
- **State schema (3.0).** Tracks the harness major version. Bump the minor version for additive
  fields; resumed runs written with an older minor version must still load.

## Release process

1. Make sure `main` is green and the `[Unreleased]` section of `CHANGELOG.md` is complete.
2. Bump the version:

   ```bash
   uv run python scripts/bump-version.py minor     # or major | patch | X.Y.Z
   uv run python scripts/bump-version.py --check   # all manifests agree
   ```

   The script updates `src/vantage/__init__.py`, `package.json` and the root version fields of
   `package-lock.json`, and turns `[Unreleased]` into a dated section with a fresh, empty
   `[Unreleased]` above it.
3. Edit the new changelog section, then run the full checks:
   `uv run python -m pytest -q`, `uv run ruff check src tests`, `npm run typecheck`, `npm test`.
4. Open a pull request titled `chore(release): vX.Y.Z` and merge it.
5. Tag the merge commit and push the tag:

   ```bash
   git tag -a v0.2.0 -m "Vantage 0.2.0"
   git push origin v0.2.0
   ```

6. The `release` workflow builds the sdist and wheel with `uv build` and creates the GitHub
   release, using the matching `CHANGELOG.md` section as the release notes.
