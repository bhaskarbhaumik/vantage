# Security Policy

## Supported versions

Vantage is pre-1.0. Security fixes land on `main` and ship in the next release of the latest minor
line only.

| Version | Supported |
|---|---|
| 0.2.x | Yes |
| < 0.2 | No |

## Reporting a vulnerability

Please **do not** open a public issue, discussion or pull request for a security problem.

Use GitHub private vulnerability reporting instead: on the repository page open
**Security → Report a vulnerability**
(<https://github.com/bhaskarbhaumik/vantage/security/advisories/new>). The report is visible only
to the maintainers.

Include what you can of:

- the affected version (`vantage version`) and backend;
- the impact, for example credential exposure, unintended metered API use, or code execution;
- steps to reproduce, with any secrets and client data removed.

Never include API keys, `.env` contents or confidential dossier text in a report. If a secret is
needed to reproduce, describe it instead.

You can expect an acknowledgement within 7 days and a status update at least every 14 days until
the report is resolved. Fixes are disclosed through a GitHub security advisory and the changelog,
with credit to the reporter unless you prefer otherwise.

## Scope

In scope: the Python engine, the CLI and TUI, the harness and workflow runner, the export
pipeline, the Claude Code plugin skills, and the deployment templates in `deploy/`.

Of particular interest:

- any path that reads, logs or persists an API key;
- any path that turns a subscription run into a metered API run without an explicit
  `--auth api-key` from the user;
- prompt or content injection from researched web content that escapes into commands, files outside
  the run directory, or exported collateral;
- generated HTML that loads remote content or runs script it should not.

Out of scope: vulnerabilities in third-party services or helper tools that Vantage calls, unless
Vantage uses them unsafely.

## Secrets and data policy

- **Credentials live in environment variables only.** Copy `.env.example` to `.env` locally; `.env`
  is ignored by git and must never be committed. Vantage never writes a key to its config file and
  never logs one.
- **Subscription-first authentication.** By default (`auth.mode=subscription`) the engine runs on
  the user's Claude plan and reads no API key, even if one is exported. API billing is opt-in per
  run (`--auth api-key`) or by an explicit config change (`vantage auth use api-key`).
- **Never commit generated dossiers, run directories or exports.** They can contain research about
  real companies and pursuit context supplied by an account team. `runs/` is ignored by git; keep
  it that way, and do not paste dossier content into public issues.
- If you commit a secret by mistake, rotate it immediately. Removing it from history is not enough.
