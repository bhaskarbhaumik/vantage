"""Canonical Vantage run state (schema 3.0) as tolerant Pydantic models.

Mirrors ``harness/state/state.schema.json``, which implements the v3 handoff contract of
``vantage-20260829.md`` extended with the registers a parallel harness needs. Agent *fragments* are
validated loosely (``extra='allow'``) because they are authored by an LLM; the merge logic below
assembles them into a single ``VantageState`` that assembly and §21 consume.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

_Loose = ConfigDict(extra="allow")

EVIDENCE_STATUSES = ("CONFIRMED", "ANNOUNCED", "OBSERVED-SIGNAL", "INFERRED", "UNKNOWN")
CONFIDENCES = ("HIGH", "MEDIUM", "LOW")
RETRIEVAL_STATUSES = ("ok", "partial", "paywall", "blocked", "dead", "parse_error", "not_attempted")
STOP_REASONS = ("diminishing_returns", "budget", "not_applicable")


class Entity(BaseModel):
    model_config = _Loose
    legal_name: str = ""
    common_name: str | None = None
    lei: str | None = None
    cik: str | None = None
    registry_id: str | None = None
    ticker: str | None = None
    exchanges: list[str] = Field(default_factory=list)
    hq: str | None = None
    fy_end: str | None = None
    latest_fy_label: str | None = None
    #: Non-null when resolution required an assumption. Unclosable ambiguity is a stop condition.
    ambiguity: str | None = None


class RunContract(BaseModel):
    """§0. Settled once by ``preflight``; a hard gate on everything downstream."""

    model_config = _Loose
    target: str = ""
    entity_candidates: list[dict] = Field(default_factory=list)
    entity: Entity = Field(default_factory=Entity)
    ownership_form: str = "public"
    jurisdictions: list[str] = Field(default_factory=lambda: ["generic"])
    reporting_standard: str | None = None
    languages: list[str] = Field(default_factory=lambda: ["en"])
    verticals: dict[str, Any] = Field(default_factory=dict)
    tier: str = "FULL_ANNEX"
    fetch_budget: dict[str, int] = Field(default_factory=dict)
    exclusions: list[str] = Field(default_factory=list)
    capability_pack: str = "NOT_ATTACHED"
    capability_pack_dated: str | None = None
    account_team_input_sheet: str = "NOT_ATTACHED"
    precomputed_financials: str = "NOT_ATTACHED"
    as_of: str = ""


class Source(BaseModel):
    model_config = _Loose
    id: str
    title: str | None = None
    publisher: str | None = None
    doc_id: str | None = None
    pub_date: str | None = None
    accessed: str | None = None
    url: str | None = None
    archived_url: str | None = None
    language: str | None = None
    retrieval_status: str | None = None
    retrieval_note: str | None = None
    tier: int | None = None
    provenance_class: str | None = None
    independence: str | None = None
    sections: list[str] = Field(default_factory=list)
    minted_by: str | None = None


class Claim(BaseModel):
    model_config = _Loose
    id: str
    claim: str | None = None
    section: str | None = None
    sources: list[str] = Field(default_factory=list)
    locators: list[str] = Field(default_factory=list)
    status: str | None = None
    confidence: str | None = None
    dimensions: dict[str, Any] = Field(default_factory=dict)
    entity: str | None = None
    materiality: str | None = None
    verification_method: str | None = None
    audit_verdict: str | None = None
    minted_by: str | None = None


class DataGap(BaseModel):
    model_config = _Loose
    id: str
    item: str | None = None
    section: str | None = None
    searched: list[str] = Field(default_factory=list)
    queries_tried: list[str] = Field(default_factory=list)
    best_available: str | None = None
    resolution_path: str | None = None
    materiality: str | None = None


class Contradiction(BaseModel):
    model_config = _Loose
    id: str
    topic: str | None = None
    kind: str | None = None
    positions: list[dict] = Field(default_factory=list)
    resolution: str | None = None
    rationale: str | None = None
    decision_impact: str | None = None
    status: str | None = None


class Coverage(BaseModel):
    model_config = _Loose
    section: str
    expected: list[str] = Field(default_factory=list)
    retrieved: list[str] = Field(default_factory=list)
    stop_reason: str | None = None
    residual_risk: str | None = None


# Registers keyed by the entity's id field, so merge is idempotent (last write wins per id).
_LIST_FIELDS = [
    "source_manifest", "claim_ledger", "contradictions", "data_gaps", "open_questions",
    "coverage", "stakeholders", "risks", "opportunities", "use_cases", "actions",
    "visuals", "section_outputs", "research_log", "handoff",
]

#: Registers exactly one agent may mint. A second agent's copy is a defect to report, not merge.
SINGLE_OWNER = {
    "stakeholders": "leadership",
    "risks": "risk",
    "opportunities": "opportunity",
    "use_cases": "ai-readiness",
    "actions": "playbook",
}

#: Fragment keys that older/looser agent output may use for the v3 canonical names.
_ALIASES = {
    "sources": "source_manifest",
    "claims": "claim_ledger",
    "gaps": "data_gaps",
    "canonical_facts": "carry_forward_facts",
    "canonical_facts_proposed": "carry_forward_facts",
}


class VantageState(BaseModel):
    """The merged run state. Append-only in spirit; merge dedupes registers by ``id``."""

    model_config = ConfigDict(extra="allow")

    schema_version: str = "3.0"
    run_contract: RunContract = Field(default_factory=RunContract)
    phase_completed: str | int | None = None
    sections_complete: list[str] = Field(default_factory=list)
    id_blocks: dict[str, Any] = Field(default_factory=dict)

    source_manifest: list[dict] = Field(default_factory=list)
    claim_ledger: list[dict] = Field(default_factory=list)
    contradictions: list[dict] = Field(default_factory=list)
    data_gaps: list[dict] = Field(default_factory=list)
    open_questions: list[dict] = Field(default_factory=list)
    coverage: list[dict] = Field(default_factory=list)

    carry_forward_facts: dict[str, Any] = Field(default_factory=dict)
    precomputed_financials: dict[str, Any] | None = None

    stakeholders: list[dict] = Field(default_factory=list)
    risks: list[dict] = Field(default_factory=list)
    opportunities: list[dict] = Field(default_factory=list)
    use_cases: list[dict] = Field(default_factory=list)
    actions: list[dict] = Field(default_factory=list)
    visuals: list[dict] = Field(default_factory=list)
    peer_set: dict[str, Any] | None = None

    scoring_inputs: dict[str, Any] = Field(default_factory=dict)
    account_team_input: dict[str, Any] | None = None
    capability_pack: dict[str, Any] | None = None

    section_outputs: list[dict] = Field(default_factory=list)
    research_log: list[dict] = Field(default_factory=list)
    evidence_audit: dict[str, Any] | None = None
    verification: dict[str, Any] = Field(default_factory=dict)
    handoff: list[dict] = Field(default_factory=list)

    #: Structural defects found while merging. Recorded, never repaired — the Verification Pass
    #: is the only agent whose job is to find them, and a silent fix hides them from it.
    merge_defects: list[dict] = Field(default_factory=list)
    #: Summary of what the last source-merge did, for the digest and for V10c/V10h.
    merge_report: dict[str, Any] = Field(default_factory=dict)

    # ---- merge ----------------------------------------------------------------
    def merge_fragment(self, frag: dict[str, Any], agent: str | None = None) -> None:
        """Fold one agent fragment into the state. Registers dedupe by ``id``."""
        frag = _normalize(frag)
        agent = agent or frag.get("agent")

        for field_name in _LIST_FIELDS:
            incoming = frag.get(field_name)
            if not incoming or not isinstance(incoming, list):
                continue
            # A single-owner register minted by the wrong agent is a defect (V10g), not a merge.
            owner = SINGLE_OWNER.get(field_name)
            if owner and agent and agent != owner:
                self.merge_defects.append({
                    "kind": "single_owner_violation", "register": field_name,
                    "owner": owner, "minted_by": agent, "count": len(incoming),
                })
                continue
            existing = getattr(self, field_name)
            by_id = {r.get("id"): i for i, r in enumerate(existing)
                     if isinstance(r, dict) and r.get("id")}
            for row in incoming:
                if not isinstance(row, dict):
                    continue
                rid = row.get("id")
                if rid and rid in by_id:
                    existing[by_id[rid]].update(row)
                else:
                    if rid:
                        by_id[rid] = len(existing)
                    existing.append(row)

        for field_name in ("carry_forward_facts", "scoring_inputs", "id_blocks"):
            block = frag.get(field_name)
            if isinstance(block, dict):
                _merge_facts(getattr(self, field_name), block) if field_name == "carry_forward_facts" \
                    else getattr(self, field_name).update(block)

        for field_name in ("precomputed_financials", "peer_set", "evidence_audit",
                           "account_team_input", "capability_pack"):
            val = frag.get(field_name)
            if isinstance(val, dict) and val:
                cur = getattr(self, field_name)
                setattr(self, field_name, {**cur, **val} if isinstance(cur, dict) else val)

        if isinstance(frag.get("verification"), dict):
            self.verification.update(frag["verification"])
        if isinstance(frag.get("run_contract"), dict):
            self.run_contract = RunContract.model_validate(
                {**self.run_contract.model_dump(), **frag["run_contract"]}
            )

    # ---- derived views --------------------------------------------------------
    def refuted_claim_ids(self) -> set[str]:
        """Claim IDs the adversarial audit refuted. Binding on §18 (V3f)."""
        ea = self.evidence_audit or {}
        ids = set(ea.get("refuted") or [])
        for v in ea.get("verdicts") or []:
            if isinstance(v, dict) and v.get("verdict") == "REFUTED" and v.get("claim_id"):
                ids.add(v["claim_id"])
        return ids

    def contested_facts(self) -> list[str]:
        return [k for k, v in self.carry_forward_facts.items()
                if isinstance(v, dict) and v.get("contested")]

    # ---- io -------------------------------------------------------------------
    def save(self, path: str | Path) -> None:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(self.model_dump(exclude_none=False), indent=2, ensure_ascii=False),
                     encoding="utf-8")

    @classmethod
    def load(cls, path: str | Path) -> VantageState:
        return cls.model_validate(json.loads(Path(path).read_text(encoding="utf-8")))


def _normalize(frag: dict[str, Any]) -> dict[str, Any]:
    """Accept the looser key names an LLM may emit, without losing the canonical ones."""
    out = dict(frag)
    for alias, canonical in _ALIASES.items():
        if alias in out and canonical not in out:
            out[canonical] = out.pop(alias)
    return out


def _merge_facts(target: dict[str, Any], incoming: dict[str, Any]) -> None:
    """Fold proposed canonical facts in, marking disagreements rather than picking a winner.

    Two agents reporting different values for the same fact is V10f — the signature failure of a
    parallel harness. Omitting a contested fact is always better than guessing one, because
    everything built on the wrong value is wrong and nothing downstream will notice.
    """
    for key, new in incoming.items():
        if key not in target:
            target[key] = new
            continue
        old = target[key]
        if not (isinstance(old, dict) and isinstance(new, dict)):
            continue
        if old.get("contested"):
            old.setdefault("competing_values", []).append(new.get("value"))
            continue
        if _comparable(old) and _comparable(new) and _comparable(old) != _comparable(new):
            old["contested"] = True
            old["competing_values"] = [old.get("value"), new.get("value")]
            old["contested_by"] = [old.get("source"), new.get("source")]
        else:
            for k, v in new.items():
                old.setdefault(k, v)


def _comparable(fact: dict[str, Any]) -> tuple | None:
    """A fact's identity for conflict detection: value plus the things that make it meaningful.

    Different period, entity, basis, or unit means different facts, not a contradiction —
    the four false-positive causes the `contradiction` brief warns about.
    """
    if "value" not in fact:
        return None
    return (str(fact.get("value")).strip().lower(), fact.get("currency"), fact.get("unit"),
            fact.get("as_of"), fact.get("basis"), fact.get("entity"))
