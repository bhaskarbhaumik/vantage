"""Deterministic source-merge (step P4a).

Reads every agent fragment, folds them into one ``VantageState``, deduplicates the Source Manifest,
rewrites retired IDs across the section files, and reports — never repairs — the structural
defects the Verification Pass exists to find.

Done in Python rather than by an LLM because collation must be exact and reproducible. The
``18-source-merge.md`` brief governs the Claude Code Workflow backend, which performs the same
work with an agent; the standard is identical.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from ..blueprint.stages import AGENTS
from ..models.state import VantageState

_TRACKING = re.compile(r"[?&](utm_[a-z]+|gclid|fbclid|mc_cid|mc_eid)=[^&]*", re.I)


def _norm_url(u: str | None) -> str | None:
    if not u:
        return None
    s = _TRACKING.sub("", u.strip()).rstrip("/?&").lower()
    for prefix in ("https://", "http://"):
        if s.startswith(prefix):
            s = s[len(prefix):]
    return s[4:] if s.startswith("www.") else s


def _id_num(sid: str) -> int:
    try:
        return int(str(sid).split("-", 1)[1])
    except (IndexError, ValueError):
        return 10**9


def _match_key(s: dict) -> str:
    """URL first, then document identifier, then title+publisher+date — the brief's order."""
    if url := _norm_url(s.get("url")):
        return f"url::{url}"
    if doc := (s.get("doc_id") or "").strip():
        return f"doc::{doc.lower()}"
    return "meta::{}|{}|{}".format(
        (s.get("title") or "").strip().lower(),
        (s.get("publisher") or "").strip().lower(),
        (s.get("pub_date") or "").strip(),
    )


def dedupe_sources(state: VantageState) -> dict[str, str]:
    """Collapse sources pointing at the same document, keeping the LOWEST id.

    The backbone ``S-0001``–``S-0049`` therefore wins, which is what makes citing the backbone the
    cheap path for every agent. Returns ``{retired_id: kept_id}``.
    """
    ordered = sorted(state.source_manifest, key=lambda s: _id_num(s.get("id", "")))
    seen: dict[str, str] = {}
    rewrite: dict[str, str] = {}
    keepers: dict[str, dict] = {}

    for s in ordered:
        key = _match_key(s)
        if key in seen:
            keeper = keepers[seen[key]]
            rewrite[s["id"]] = seen[key]
            # Fold extras onto the keeper WITHOUT overwriting what it already has.
            for k, v in s.items():
                if k == "sections":
                    merged = list(dict.fromkeys((keeper.get("sections") or []) + (v or [])))
                    keeper["sections"] = merged
                elif k != "id":
                    keeper.setdefault(k, v)
        else:
            seen[key] = s["id"]
            keepers[s["id"]] = s

    state.source_manifest = list(keepers.values())
    return rewrite


def apply_rewrites(state: VantageState, rewrite: dict[str, str], run_dir: Path) -> int:
    """Rewrite retired source IDs in the claim ledger and in every section file on disk."""
    if not rewrite:
        return 0
    for claim in state.claim_ledger:
        if srcs := claim.get("sources"):
            claim["sources"] = list(dict.fromkeys(rewrite.get(s, s) for s in srcs))
        if locs := claim.get("locators"):
            claim["locators"] = [_rewrite_text(loc, rewrite) for loc in locs]

    touched = 0
    sections = run_dir / "sections"
    if sections.exists():
        for fp in sorted(sections.glob("*.md")):
            text = fp.read_text(encoding="utf-8")
            new = _rewrite_text(text, rewrite)
            if new != text:
                fp.write_text(new, encoding="utf-8")
                touched += 1
    return touched


def _rewrite_text(text: str, rewrite: dict[str, str]) -> str:
    # Longest-first so S-0500 is not clipped by a rule for S-050.
    for old in sorted(rewrite, key=len, reverse=True):
        text = re.sub(rf"\b{re.escape(old)}\b", rewrite[old], text)
    return text


def find_false_triangulation(state: VantageState, rewrite: dict[str, str]) -> list[dict]:
    """Claims whose corroboration collapsed to one document after dedup.

    A claim scored ``HIGH`` on two sources that turn out to be one document is confidence
    inflation no other check can see, and it exists *only* because agents ran concurrently.
    Reported for V10h; the composite is downgraded here so nothing downstream inherits the
    inflated score.
    """
    if not rewrite:
        return []
    collapsed = []
    for claim in state.claim_ledger:
        srcs = claim.get("sources") or []
        if len(srcs) >= 2 or claim.get("confidence") != "HIGH":
            continue
        # After rewriting, a HIGH claim with a single source that used to have several.
        dims = claim.get("dimensions") or {}
        if (dims.get("corroboration") or 0) >= 2 and len(set(srcs)) < 2:
            dims["corroboration"] = len(set(srcs))
            claim["dimensions"] = dims
            claim["confidence"] = "MEDIUM"
            collapsed.append({
                "claim_id": claim.get("id"), "section": claim.get("section"),
                "surviving_source": srcs[0] if srcs else None,
                "note": "corroboration collapsed to one document after source dedup; downgraded HIGH -> MEDIUM",
            })
    return collapsed


def find_structural_defects(state: VantageState, run_dir: Path, expected: list[str]) -> list[dict]:
    """Record — do not repair. Silently fixing a defect hides it from `verification`."""
    defects: list[dict] = list(state.merge_defects)

    # Missing fragments and sections, named by agent (V10e).
    frag_dir = run_dir / "state" / "fragments"
    for label in expected:
        spec = AGENTS.get(label)
        if spec is None:
            continue
        if not (frag_dir / f"{label}.json").exists():
            defects.append({"kind": "missing_fragment", "agent": label})
        if spec.out and not (run_dir / "sections" / spec.out).exists():
            defects.append({"kind": "missing_section", "agent": label, "file": spec.out})

    # Out-of-block IDs (V1c) and duplicate IDs (V10b).
    prefixes = {"S-": "source_manifest", "G-": "data_gaps", "X-": "contradictions", "Q-": "open_questions"}
    seen_ids: dict[str, str] = {}
    for prefix, field_name in prefixes.items():
        for row in getattr(state, field_name):
            rid, owner = row.get("id"), row.get("minted_by")
            if not rid:
                continue
            if rid in seen_ids and seen_ids[rid] != owner:
                defects.append({"kind": "duplicate_id", "id": rid,
                                "minted_by": [seen_ids[rid], owner]})
            seen_ids[rid] = owner
            spec = AGENTS.get(owner or "")
            if spec and spec.block and rid.startswith(prefix):
                try:
                    n = int(rid.split("-", 1)[1])
                except ValueError:
                    continue
                if not (spec.block[0] <= n <= spec.block[1]):
                    defects.append({"kind": "out_of_block_id", "id": rid, "minted_by": owner,
                                    "block": list(spec.block)})

    # Claims citing sources that are not in the manifest (V1a).
    manifest = {s.get("id") for s in state.source_manifest}
    for claim in state.claim_ledger:
        for sid in claim.get("sources") or []:
            if sid not in manifest:
                defects.append({"kind": "unresolved_source_ref",
                                "claim": claim.get("id"), "source": sid})
    return defects


def merge_fragments(run_dir: Path, base_state: dict[str, Any] | None = None,
                    expected_labels: list[str] | None = None) -> VantageState:
    """Fold every fragment into one state document, dedupe, rewrite, and report defects."""
    run_dir = Path(run_dir)
    state = VantageState()

    # Start from preflight's state.json so the run contract and backbone survive.
    existing = run_dir / "state" / "state.json"
    if existing.exists():
        try:
            state = VantageState.model_validate(json.loads(existing.read_text(encoding="utf-8")))
        except Exception:  # a malformed state.json is a defect, not a stop
            state.merge_defects.append({"kind": "unreadable_state_json"})
    # Defects describe THIS merge. A "missing_fragment" recorded at P4a is stale by P8b,
    # when the agent has since run — recompute rather than accumulate.
    state.merge_defects = [d for d in state.merge_defects if d.get("kind") == "unreadable_state_json"]
    if base_state:
        state.merge_fragment(base_state)

    frag_dir = run_dir / "state" / "fragments"
    if frag_dir.exists():
        for fp in sorted(frag_dir.glob("*.json")):
            try:
                frag = json.loads(fp.read_text(encoding="utf-8"))
            except Exception:
                state.merge_defects.append({"kind": "unreadable_fragment", "file": fp.name})
                continue
            if isinstance(frag, dict):
                state.merge_fragment(frag, agent=frag.get("agent") or fp.stem)

    pf = run_dir / "state" / "precomputed-financials.json"
    if pf.exists() and not state.precomputed_financials:
        try:
            state.precomputed_financials = json.loads(pf.read_text(encoding="utf-8"))
        except Exception:
            state.merge_defects.append({"kind": "unreadable_precomputed_financials"})

    rewrite = dedupe_sources(state)
    touched = apply_rewrites(state, rewrite, run_dir)
    collapsed = find_false_triangulation(state, rewrite)
    state.merge_defects = find_structural_defects(state, run_dir, expected_labels or [])

    state.merge_report = {
        "sources_after_dedup": len(state.source_manifest),
        "sources_retired": len(rewrite),
        "sections_rewritten": touched,
        "false_triangulation": collapsed,
        "defects": state.merge_defects,
    }

    (run_dir / "qa").mkdir(parents=True, exist_ok=True)
    (run_dir / "qa" / "source-rewrite-map.json").write_text(
        json.dumps(rewrite, indent=2, ensure_ascii=False), encoding="utf-8")
    state.save(run_dir / "state" / "state.json")
    return state
