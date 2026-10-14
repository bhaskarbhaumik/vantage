# Vantage documentation

Vantage™ — Verified Account Navigator: Targeting, Analysis & GTM Engine. Start with
[Getting started](getting-started.md); everything else is reference you can dip into.

## Use it

| Page | Covers |
|---|---|
| [Getting started](getting-started.md) | Prerequisites, install, first dossier, first export, quick fixes |
| [CLI guide](cli.md) | Global vs command options, precedence, `--set`, `--role-model`, JSON mode, exit codes, recipes |
| [CLI reference](reference/cli.md) | Every command and option, generated from the code |
| [Terminal UI](tui.md) | Screens, keybindings, deep links, icon modes, colour, themes, Nerd Fonts |
| [Export](export.md) | Decks, whitepapers, PDFs and HTML from a finished dossier |
| [Claude Code](claude-code.md) | The plugin, `/vantage:generate`, `/vantage:export`, the Workflow tool |
| [Shell completion](completions.md) | bash, zsh and fish |

## Configure and run

| Page | Covers |
|---|---|
| [Configuration](configuration.md) | Every config section, environment variables, precedence, migration |
| [Backends](backends.md) | The six execution backends and when to use each |
| [Authentication and billing](auth.md) | Subscription vs API key, credential classes, what costs money |
| [Deployment](deployment.md) | The container image and the GCP, Azure and AWS targets |

## Understand it

| Page | Covers |
|---|---|
| [Architecture](architecture.md) | Pipeline P0–P8, P7R owner remediation, the engine's layers |
| [Harness architecture](../harness/ARCHITECTURE.md) | The design decisions behind the dossier, in depth |
| [Harness README](../harness/HARNESS_README.md) | Layout, workflow args, tiers, run layout |
| [Export harness](../harness/export/ARCHITECTURE.md) | Agents write plans, code writes files |
| [Reference prompt package](prompts/vantage-v1/vantage-20260829.md) | The v3.0.0 prompt package the harness implements ([tooling catalog](prompts/vantage-v1/vantage-tools-20260829.md)) |

## When something is off

[Troubleshooting](troubleshooting.md) · [FAQ](faq.md) · [Support](../SUPPORT.md) ·
[Security](../SECURITY.md)

## Project

[Contributing](../CONTRIBUTING.md) · [Changelog](../CHANGELOG.md) ·
[Versioning and releases](../VERSION.md) · [Governance](../GOVERNANCE.md) ·
[Code of Conduct](../CODE_OF_CONDUCT.md) · [License](../LICENSE)
