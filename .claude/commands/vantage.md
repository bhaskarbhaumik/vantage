---
description: Run a Vantage dossier (Verified Account Navigator) for a company
argument-hint: <company legal name> [backend] [tier]
---

Invoke the **vantage** skill to produce a **Vantage** dossier (*Verified Account Navigator:
Targeting, Analysis & GTM Engine*, blueprint v3.0.0). When the Vantage plugin is installed this is
the same as `/vantage:generate`.

User request / target: $ARGUMENTS

Follow the skill precisely. It resolves `VANTAGE_REPO` and then follows
`skills/generate/SKILL.md` in that repo:

1. Determine the **client legal name** (ask only if it is truly absent) and infer
   ticker / vertical / tier. Tier is `EXECUTIVE` | `STANDARD` | `FULL_ANNEX`; default `FULL_ANNEX`,
   but pick `EXECUTIVE` if the user signalled they want a fast read.
2. Read `~/.config/vantage/default.json` (or `vantage config show`) for the default backend, tier
   and `auth.mode`; if the user named a backend in the arguments, use it. Show `vantage backends`
   readiness if unsure. **Never add `--auth api-key` yourself**: it switches the run from the
   user's Claude subscription to metered API billing. Ask first.
3. Run the dossier: use the native Workflow tool for the `workflow` backend (opt in explicitly),
   otherwise `uv run --project "$VANTAGE_REPO" vantage run --backend <b> …`.
4. Report: dossier path · **Overall Confidence** and verification result · P7R remediation rounds
   and their §21.8 outcome · agents ok/total with any non-returning agent **named** · topics that
   stopped on budget rather than diminishing returns (§21.12) · top high-materiality gaps · and,
   if the Capability Pack or Account-Team Input Sheet was not attached, which fields are
   consequently `[INTERNAL REQUIRED]`.

If preflight reports an **entity ambiguity**, relay it rather than proceeding past it. To turn the
finished dossier into a deck, document, PDF or microsite, use `/vantage:export`.
