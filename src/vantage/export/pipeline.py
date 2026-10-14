"""Plan loading and the scaffold record — the contract between the agents and the renderers.

**Agents write plans, code writes files.** Plans are read from ``<out>/plan/*.json`` when present
and derived deterministically when not. A plan on disk is classified so the result can say whether
the collateral got editorial judgement or the deterministic mapping:

``authored``  the file differs from the scaffold this module wrote — an agent (or a person) wrote it
``scaffold``  the file is byte-identical to the scaffold; nobody edited it
``derived``   no valid file on disk; the plan was built in memory for this run
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from .models import DeckPlan, DocPlan, Dossier, SitePlan
from .plan import build_deck_plan, build_doc_plan, build_site_plan

#: Written beside the plans, holding the digest of each scaffold. Without it "a plan file
#: exists" is indistinguishable from "an agent authored a plan".
SCAFFOLD_RECORD = ".scaffold.json"


def plan_dir(out_dir: Path) -> Path:
    return Path(out_dir) / "plan"


def _digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf8")).hexdigest()


def _record(plans: Path) -> dict[str, str]:
    record = plans / SCAFFOLD_RECORD
    if not record.exists():
        return {}
    try:
        data = json.loads(record.read_text(encoding="utf8"))
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def load_or_build_plans(dossier: Dossier, out_dir: Path, depth: str = "standard",
                        site_mode: str = "microsite",
                        warnings: list[str] | None = None
                        ) -> tuple[DeckPlan, DocPlan, SitePlan, dict[str, str]]:
    """Prefer a plan on disk; fall back to the derived one, per collateral.

    A malformed plan degrades *that* collateral to its derived plan and records a warning — it
    never fails the run.
    """
    plans = plan_dir(out_dir)
    scaffold = _record(plans)
    sources: dict[str, str] = {}

    def pick(name: str, model, builder):
        path = plans / f"{name}.json"
        if path.exists():
            try:
                raw = path.read_text(encoding="utf8")
                value = model.model_validate(json.loads(raw))
            except Exception as exc:
                if warnings is not None:
                    warnings.append(f"plan/{path.name} is not a valid {model.__name__} "
                                    f"({str(exc).splitlines()[0][:160]}); using the derived plan")
            else:
                sources[name] = ("scaffold" if scaffold.get(name) == _digest(raw)
                                 else "authored")
                return value
        sources[name] = "derived"
        return builder()

    deck = pick("deck", DeckPlan, lambda: build_deck_plan(dossier, depth))
    doc = pick("doc", DocPlan, lambda: build_doc_plan(dossier, depth))
    site = pick("site", SitePlan, lambda: build_site_plan(dossier, site_mode, depth))
    return deck, doc, site, sources


class AuthoredPlanExists(RuntimeError):
    """Raised rather than overwrite a plan somebody has already written."""

    def __init__(self, names: list[str]) -> None:
        self.names = names
        super().__init__(f"refusing to overwrite authored plan(s): {', '.join(names)}. "
                         f"Pass force=True (--force) to discard them.")


def write_plans(dossier: Dossier, out_dir: Path, depth: str = "standard",
                site_mode: str = "microsite", force: bool = False,
                keep_authored: bool = False) -> Path:
    """Write the derived plans to disk as the agents' starting point.

    Records each file's digest so a later run can tell an authored plan from an untouched
    scaffold. Unless ``force``, refuses to clobber a plan that has diverged from the scaffold
    (``keep_authored`` leaves such a plan in place and writes the rest).
    """
    plans = plan_dir(out_dir)
    plans.mkdir(parents=True, exist_ok=True)
    built = {
        "deck": build_deck_plan(dossier, depth),
        "doc": build_doc_plan(dossier, depth),
        "site": build_site_plan(dossier, site_mode, depth),
    }
    scaffold = _record(plans)
    authored = [name for name in built
                if (plans / f"{name}.json").exists()
                and scaffold.get(name) != _digest((plans / f"{name}.json").read_text("utf8"))]
    if authored and not force and not keep_authored:
        raise AuthoredPlanExists(authored)
    digests = dict(scaffold)
    for name, value in built.items():
        if name in authored and not force:
            continue
        raw = value.model_dump_json(indent=2)
        (plans / f"{name}.json").write_text(raw, encoding="utf8")
        digests[name] = _digest(raw)
    (plans / SCAFFOLD_RECORD).write_text(json.dumps(digests, indent=2), encoding="utf8")
    return plans


def write_schemas(target: Path) -> list[Path]:
    """Emit JSON Schema for the plan models (``harness/export/state``)."""
    target.mkdir(parents=True, exist_ok=True)
    written = []
    for name, model in (("deck.plan.schema.json", DeckPlan), ("doc.plan.schema.json", DocPlan),
                        ("site.plan.schema.json", SitePlan)):
        schema = model.model_json_schema()
        schema["$schema"] = "https://json-schema.org/draft/2020-12/schema"
        schema["title"] = model.__name__
        schema["description"] = (model.__doc__ or "").strip() or f"Vantage export {model.__name__}"
        path = target / name
        path.write_text(json.dumps(schema, indent=2) + "\n", encoding="utf8")
        written.append(path)
    return written
