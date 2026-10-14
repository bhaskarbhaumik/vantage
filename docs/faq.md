# FAQ

**Does Vantage need an API key?**
No. The default `workflow` backend runs on your Claude plan through the Claude Code CLI and reads
no API key at all. Keys matter only when you opt into `--auth api-key`, which is billed per token.
See [Authentication and billing](auth.md).

**I have `ANTHROPIC_API_KEY` exported for another tool. Will Vantage use it?**
Not in `subscription` mode. The engine ignores it on purpose, so it cannot silently meter a run.

**What is the difference between `vantage` and `vantage-engine`?**
None: they are the same program. `vantage` is the primary name; `vantage-engine` is an alias kept
for scripts and the container entry point.

**And `vantage-tui`?**
The interactive terminal UI. `vantage --tui` launches it. It calls the `vantage` CLI underneath,
so it never does anything the CLI cannot. See [Terminal UI](tui.md).

**How long does a dossier take, and what does it cost?**
It depends on the company, the tier and the backend. A `FULL_ANNEX` dossier runs 29 agents with
web research, so expect minutes, not seconds. On the `workflow` backend it counts against your
Claude plan's usage; on the API backends you pay per token. Start with `--tier EXECUTIVE` for a
quick read.

**Which tier should I use?**
`FULL_ANNEX` (default) for a real pursuit: all 22 sections and §21.1–21.12. `STANDARD` for §0–§20
with condensed appendices. `EXECUTIVE` for a fast read: §0–§2 plus the §1 synthesis, from six
research agents.

**What does "Insufficient" mean?**
The verification gate found the evidence base too thin for the tier. Do not present the dossier.
Check §21.12 for topics that stopped on budget and re-run them, or narrow the scope.

**Why do some fields say `[INTERNAL REQUIRED]`?**
Win probability, account revenue, relationship strength and stakeholder access cannot be derived
from public evidence. They need the §21.10 Account-Team Input Sheet; capability claims need the
Capability Pack. §21.10 is emitted as a blank template for the account team to fill in. Attach
both with `--input-sheet ATTACHED --capability-pack ATTACHED` and re-run.

**Can verification just fix the problems it finds?**
It may downgrade or label, but never rewrite another agent's analysis, or it would stop being an
independent check. Instead, P7R sends each blocking finding back to the agent that owns the text,
then re-verifies from scratch. See [Architecture](architecture.md#p7r-owner-remediation).

**Can I present the scores to the company?**
No. Scores are internal decision aids built from outside-in public evidence, not measurements of
the company. Every export carries that disclaimer next to every score.

**Can I change the prompts or the dossier structure?**
Yes. The harness is Markdown read at runtime. Edit a brief, a rubric or a contract in `harness/`,
then read [CONTRIBUTING.md](../CONTRIBUTING.md#changing-the-harness-safely) about cache stability
and the registries that must stay in step.

**Can I use OpenAI or Gemini?**
On the API-driven backends, yes: enable the provider, point a model tier or a credential class at
it, and use `--auth api-key`. See [Configuration](configuration.md#providers) and
[Authentication](auth.md#credential-classes).

**Where are my runs?**
`~/.cache/vantage/run/<slug>/` by default (`engine.output_dir`). `vantage runs list` shows them;
`vantage runs path <slug>` prints one.

**Can I export without LibreOffice or the helper CLIs?**
Yes. Without LibreOffice you get everything except the PDF; each missing helper falls back to a
built-in rendering with a warning. See [Export](export.md#visual-helpers).

**Is the HTML export safe to host publicly?**
No. Treat it like the deck: it carries the classification marking, and it should only be shared
through access-controlled channels.

**Can I run Vantage in the cloud?**
Yes, with the `api` backend (or a framework backend) and `--auth api-key`. The `workflow` backend
needs an interactive Claude login. See [Deployment](deployment.md).

**How do I upgrade?**
Pull, `uv sync` with your extras, `npm ci && npm run build`, then
`uv run vantage config migrate --dry-run` and apply it. Read [CHANGELOG.md](../CHANGELOG.md) for
breaking changes.
