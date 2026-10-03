"""Assemble the final Markdown dossier (step P8) — deterministic, mints nothing.

Collates section files in blueprint order (§0 → §1 → §2 → §3 … §21), prepends the title block
carrying Overall Confidence and the resolved entity, and generates the **register appendices**
(§21.1, §21.9, §21.10, §21.11, §21.12) from merged state. The narrative appendices §21.2–21.7 are
written by the ``appendices`` agent and slot in as a section file.

Two rules govern everything here: **an unresolved reference is recorded, never invented into
existence**, and a section that says "no evidence found" stays exactly that.
"""

from __future__ import annotations

import re
from pathlib import Path

from .. import TAGLINE
from ..models.state import VantageState

#: Section files in assembly order. §1 is placed FIRST and was written LAST.
SECTION_ORDER = [
    "00-run-contract.md",       # §0
    "01-exec-brief.md",         # §1
    "02-methodology.md",        # §2
    "03-company.md",            # §3
    "04-market.md",             # §4
    "05-business-model.md",     # §5
    "06-financials.md",         # §6
    "07-operations.md",         # §7
    "08-technology.md",         # §8
    "09-strategy.md",           # §9
    "10-leadership.md",         # §10
    "11-competition.md",        # §11
    "12-customers.md",          # §12
    "13-signals.md",            # §13
    "14-risk.md",               # §14
    "15-ai-readiness.md",       # §15
    "16-vendors.md",            # §16
    "17-esg.md",                # §17
    "18-opportunity.md",        # §18
    "19-account-strategy.md",   # §19
    "20-playbook.md",           # §20
]

#: Appendix section files, in §21 order. Register appendices are generated, not read.
APPENDIX_FILES = [
    ("21-appendices.md", "§21.2–21.7 narrative appendices"),
    ("21-8-verification.md", "§21.8 Verification Summary"),
    ("21-11-contradictions.md", "§21.11 contradiction register (draft)"),
    ("21-vertical-annex.md", "vertical module annex"),
]

_MATERIALITY = {"high": 0, "medium": 1, "low": 2}
_CONF = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
_REF = re.compile(r"\[((?:S|C|O|R|P|A|U|G|X|Q)-[0-9][0-9A-Za-z.\-]*)")


def _table(headers: list[str], rows: list[list], empty: str = "_No entries._") -> str:
    if not rows:
        return empty
    out = ["| " + " | ".join(headers) + " |",
           "|" + "|".join(["---"] * len(headers)) + "|"]
    for r in rows:
        out.append("| " + " | ".join(
            ("" if c is None else str(c)).replace("|", "\\|").replace("\n", " ") for c in r) + " |")
    return "\n".join(out)


# ---------------------------------------------------------------------------
# Register appendices — generated from merged state
# ---------------------------------------------------------------------------

def _appendix_21_1(s: VantageState) -> str:
    rows = [[x.get("id"), x.get("title"), x.get("publisher"), x.get("doc_id"), x.get("pub_date"),
             x.get("accessed"), x.get("url"), x.get("language"), x.get("retrieval_status") or "ok",
             x.get("tier"), ", ".join(x.get("sections") or [])]
            for x in sorted(s.source_manifest, key=lambda z: z.get("id", ""))]
    body = _table(["ID", "Title", "Publisher", "Doc ID", "Pub date", "Accessed", "URL",
                   "Lang", "Retrieval", "Tier", "Sections fed"], rows,
                  "_No sources recorded. This is itself a finding — see §21.12._")

    # Failed retrievals are evidence about coverage, not noise to drop (V1h).
    failed = [x for x in s.source_manifest
              if (x.get("retrieval_status") or "ok") not in ("ok", "partial")]
    note = ""
    if failed:
        note = (f"\n\n**Failed retrievals ({len(failed)} of {len(s.source_manifest)}).** Recorded rather than dropped — a manifest "
                "showing only successes misrepresents coverage.\n\n" + _table(
            ["ID", "Status", "What was attempted instead"],
            [[x.get("id"), x.get("retrieval_status"), x.get("retrieval_note") or "_not recorded_"]
             for x in failed]))
    return body + note


def _appendix_21_9(s: VantageState, limit: int = 60) -> str:
    ranked = sorted(
        s.claim_ledger,
        key=lambda c: (_MATERIALITY.get(c.get("materiality"), 3),
                       _CONF.get(c.get("confidence"), 3), c.get("id", "")),
    )[:limit]
    rows = [[c.get("id"), (c.get("claim") or "")[:200], c.get("section"),
             ", ".join(c.get("sources") or []), c.get("status"),
             c.get("verification_method"), c.get("audit_verdict"), c.get("confidence")]
            for c in ranked]
    head = _table(["ID", "Claim", "§", "Sources", "Evidence status", "Verification method",
                   "Audit verdict", "Confidence"], rows)
    total = len(s.claim_ledger)
    return (f"The {len(ranked)} most material claims of {total} in the ledger, ranked by "
            f"materiality then confidence.\n\n{head}")


_INPUT_SHEET_TEMPLATE = """\
Not supplied for this run. The fields below **cannot** be derived from public evidence and are not
inferred anywhere in this dossier. Every gated field in §1.4, §1.6, §15.6, §16.4, §18.1, §19.5, and
§19.9 reads `[INTERNAL REQUIRED]` as a result.

Completing this sheet and re-running unlocks those fields.

| Field | Value |
|---|---|
| Current the pursuing organization revenue at this account (FY, currency) | `[INTERNAL]` |
| Active contracts — scope, value, end date | `[INTERNAL]` |
| Delivery history and current satisfaction | `[INTERNAL]` |
| Named relationships and access level per stakeholder | `[INTERNAL]` |
| Open pipeline and stage | `[INTERNAL]` |
| Referenceable comparable clients | `[INTERNAL]` |
| Known exclusions, conflicts, or no-bid constraints | `[INTERNAL]` |
| Account team and executive sponsor | `[INTERNAL]` |
"""


def _appendix_21_10(s: VantageState) -> str:
    if s.account_team_input:
        return _table(["Field", "Value"],
                      [[k, v] for k, v in s.account_team_input.items()])
    return _INPUT_SHEET_TEMPLATE


def _appendix_21_11(s: VantageState) -> str:
    contra = _table(
        ["ID", "Topic", "Kind", "Positions", "Resolution", "Rationale", "Decision impact", "Status"],
        [[x.get("id"), x.get("topic"), x.get("kind"),
          " vs ".join(str(p.get("value")) for p in (x.get("positions") or [])),
          x.get("resolution"), x.get("rationale"), x.get("decision_impact"), x.get("status")]
         for x in sorted(s.contradictions, key=lambda z: z.get("id", ""))],
        "_No contradictions recorded._")

    gaps = sorted(s.data_gaps,
                  key=lambda z: (_MATERIALITY.get(z.get("materiality"), 3), z.get("id", "")))
    gap_tbl = _table(
        ["ID", "Missing", "§", "Where searched", "Best available", "Resolution path", "Materiality"],
        [[g.get("id"), g.get("item"), g.get("section"),
          "; ".join(g.get("searched") or []) or "_not recorded_",
          g.get("best_available"), g.get("resolution_path"), g.get("materiality")]
         for g in gaps], "_No data gaps recorded._")

    contested = s.contested_facts()
    contested_note = ""
    if contested:
        contested_note = ("\n\n### Contested canonical facts\n\nThese were reported differently by "
                          "two or more agents and are **omitted from downstream use** rather than "
                          "reconciled by guess.\n\n" + _table(
            ["Fact", "Competing values", "Reported by"],
            [[k, " vs ".join(str(v) for v in (s.carry_forward_facts[k].get("competing_values") or [])),
              ", ".join(str(v) for v in (s.carry_forward_facts[k].get("contested_by") or []) if v)]
             for k in contested]))

    return ("### Contradiction register\n\n" + contra + contested_note +
            "\n\n### Data-gap register\n\n" + gap_tbl)


def _appendix_21_12(s: VantageState) -> str:
    rows = []
    for c in sorted(s.coverage, key=lambda z: _sort_section(z.get("section"))):
        expected = c.get("expected") or []
        retrieved = c.get("retrieved") or []
        missing = [e for e in expected if e not in retrieved]
        rows.append([c.get("section"), ", ".join(expected) or "—", ", ".join(retrieved) or "—",
                     ", ".join(missing) or "—", c.get("stop_reason"), c.get("residual_risk")])
    tbl = _table(["§", "Expected source classes", "Retrieved", "Not retrieved",
                  "Stop reason", "Residual risk"], rows,
                 "_No coverage records. Section completeness cannot be assessed for this run._")

    budget = [c.get("section") for c in s.coverage if c.get("stop_reason") == "budget"]
    note = ""
    if budget:
        note = ("\n\n> **Stopped on budget, not on diminishing returns:** §" +
                " · §".join(str(b) for b in budget) +
                ".\n> These topics were not exhausted. Extending the fetch budget and re-running "
                "them would materially improve coverage — as distinct from there being nothing to "
                "find.")
    return tbl + note


def _sort_section(sec) -> tuple:
    try:
        return tuple(int(p) for p in str(sec).split("."))
    except (TypeError, ValueError):
        return (999,)


def _scoring_notes(s: VantageState) -> str:
    if not s.scoring_inputs:
        return "_No scoring models applied._"
    lines = []
    for name, block in s.scoring_inputs.items():
        model = block.get("model", name)
        if block.get("composite_suppressed"):
            verdict = "**composite suppressed** (≥2 dimensions at LOW confidence)"
        elif block.get("not_reliably_assessable_reason"):
            verdict = f"NOT RELIABLY ASSESSABLE — {block['not_reliably_assessable_reason']}"
        else:
            verdict = f"composite {block.get('composite')}"
        renorm = block.get("renormalized_from")
        extra = f" · weights renormalized from {renorm}% to 100%" if renorm else ""
        lines.append(f"- **{model}** — {verdict} · band: {block.get('band') or '—'}{extra}")
    return "\n".join(lines)


def unresolved_references(body: str, s: VantageState) -> list[str]:
    """Every inline reference that does not resolve against the merged registers.

    Recorded, never invented into existence — creating a manifest entry so a citation resolves
    would convert a traceability failure into a fabricated source.
    """
    known: set[str] = set()
    known |= {x.get("id") for x in s.source_manifest}
    known |= {x.get("id") for x in s.claim_ledger}
    for reg in (s.data_gaps, s.contradictions, s.open_questions, s.stakeholders,
                s.risks, s.opportunities, s.use_cases, s.actions):
        known |= {x.get("id") for x in reg}
    known.discard(None)
    found = {m.group(1) for m in _REF.finditer(body)}
    return sorted(found - known)


# ---------------------------------------------------------------------------
# Assembly
# ---------------------------------------------------------------------------


def _adjustment_is_live(eqi, eqi_att, suppressed) -> bool:
    """True only when the ownership-form adjustment actually moved the score.

    For a public filer with a full adapter set every attainable maximum is
    CONFIRMED+HIGH and EQI_attainment is identical to EQI_raw. The protocol calls the
    adjustment inert in that case, so it must leave the title block untouched rather
    than print one number twice under two labels.
    """
    if suppressed:
        return True
    if eqi is None or eqi_att is None:
        return False
    return abs(float(eqi_att) - float(eqi)) >= 0.05


def _eqi_label(eqi, eqi_att, suppressed) -> str:
    """`EQI` when the adjustment is inert, `EQI_raw` when a second number follows it."""
    if eqi is None:
        return ""
    tag = "EQI_raw" if _adjustment_is_live(eqi, eqi_att, suppressed) else "EQI"
    return f" ({tag} {eqi})"


def _attainment_suffix(eqi_att, band_att, suppressed, ownership_form: str | None, eqi=None) -> str:
    """Render the ownership-form attainment qualifier for the title block.

    Never returns a bare band: the qualifier is always named "attainment" and always
    carries the ownership form, so it cannot be read off as a promotion of the raw band
    (verification-protocol.md V13d).
    """
    if suppressed:
        return (" · **attainment** SUPPRESSED — >50% of a denominator is structurally "
                "unattainable; this target may not be researchable to dossier standard")
    if eqi_att is None or band_att is None:
        return ""
    if not _adjustment_is_live(eqi, eqi_att, suppressed):
        return ""
    form = f", `{ownership_form}` — ceiling-bound" if ownership_form else ""
    return f" · **attainment** {band_att} (EQI_att {eqi_att}{form})"


def assemble(run_dir: Path, state: VantageState, slug: str, *, client: str, research_as_of: str,
             tier: str = "FULL_ANNEX", dossier_suffix: str = "vantage") -> Path:
    run_dir = Path(run_dir)
    rc = state.run_contract
    ver = state.verification or {}
    band = ver.get("overall_confidence") or "not assessed"
    eqi = ver.get("eqi")
    result = ver.get("result") or "not run"

    # Ownership-form adjustment (verification-protocol.md § Ownership-form adjustment).
    # EQI_attainment answers "did we get what was gettable"; EQI_raw answers "how much
    # evidence is under this". Guard V13d: the attainment score is never published alone
    # and never substitutes for the raw band in the title block.
    eqi_att = ver.get("eqi_attainment")
    band_att = ver.get("attainment_confidence")
    att_suppressed = ver.get("eqi_attainment_suppressed")  # V13c

    ids = " · ".join(x for x in [
        rc.entity.legal_name or client,
        f"LEI {rc.entity.lei}" if rc.entity.lei else None,
        f"CIK {rc.entity.cik}" if rc.entity.cik else None,
        rc.entity.ticker,
        rc.ownership_form,
    ] if x)

    title = (
        f"# Vantage — {client}\n\n"
        f"**Vantage:** {TAGLINE}  \n"
        f"**Classification:** Internal account research — Sales Intelligence  \n"
        f"**Prepared by:** Vantage contributors  \n"
        f"**Version:** 3.0.0 · **Output tier:** {tier}  \n"
        f"**As-of Date:** {research_as_of}  \n"
        f"**Entity Resolved:** {ids}  \n"
        f"**Jurisdiction adapter(s):** {', '.join(rc.jurisdictions) or '—'} · "
        f"**Reporting standard:** {rc.reporting_standard or '—'}  \n"
        f"**Overall Confidence:** {band}"
        + _eqi_label(eqi, eqi_att, att_suppressed)
        + _attainment_suffix(eqi_att, band_att, att_suppressed, rc.ownership_form, eqi)
        + f" · **Verification:** {result}\n\n"
        "> Scores in this dossier are evidence-based internal decision aids derived from "
        "outside-in public evidence. They are not measurements of the client and must not be "
        "presented to the client.\n"
    )
    if rc.entity.ambiguity:
        title += (f"\n> ⚠ **Entity ambiguity recorded during preflight:** {rc.entity.ambiguity} "
                  "Facts in this dossier may attach to more than one entity; see §0 and §3.6.\n")

    sections_dir = run_dir / "sections"
    body_parts, missing = [], []
    for fname in SECTION_ORDER:
        fp = sections_dir / fname
        if fp.exists():
            body_parts.append(fp.read_text(encoding="utf-8").strip())
        else:
            missing.append(fname)
    body = "\n\n---\n\n".join(body_parts)

    appendix_parts = ["# 21. Appendices & Reference Data",
                      "## 21.1 Source Manifest\n\n" + _appendix_21_1(state)]
    for fname, _desc in APPENDIX_FILES:
        fp = sections_dir / fname
        if fp.exists():
            appendix_parts.append(fp.read_text(encoding="utf-8").strip())
    appendix_parts += [
        "## 21.9 Claim Ledger\n\n" + _appendix_21_9(state),
        "## 21.10 Account-Team Input Sheet\n\n" + _appendix_21_10(state),
        "## 21.11 Contradiction & Data-Gap Register\n\n" + _appendix_21_11(state),
        "## 21.12 Source-Completeness Scorecard\n\n" + _appendix_21_12(state),
        "## Scoring logic applied\n\n" + _scoring_notes(state),
    ]
    appendices = "\n\n".join(appendix_parts)

    unresolved = unresolved_references(body + "\n" + appendices, state)
    notes = []
    if missing:
        notes.append("**Sections absent from this run:** " + ", ".join(missing) +
                     ". Named rather than absorbed — see §21.12 and the Verification Summary.")
    if unresolved:
        notes.append("**Unresolved references (recorded, not invented):** " +
                     ", ".join(unresolved[:40]) +
                     (f" … and {len(unresolved) - 40} more" if len(unresolved) > 40 else ""))
    if state.merge_defects:
        kinds = sorted({d.get("kind") for d in state.merge_defects})
        notes.append("**Structural defects recorded at merge:** " + ", ".join(kinds) + ".")
    assembly_notes = ("\n\n## Assembly notes\n\n" + "\n\n".join(notes)) if notes else ""

    doc = "\n\n".join([
        title, "---", body, "---", appendices + assembly_notes,
        f"\n---\n\n*Generated by Vantage · blueprint v3.0.0 · as of {research_as_of}*",
    ])
    out = run_dir / f"{slug}-{dossier_suffix}.md"
    out.write_text(doc, encoding="utf-8")
    return out
