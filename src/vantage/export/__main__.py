"""``python -m vantage.export`` — the small engine CLI the export harness drives.

    python -m vantage.export inspect <dossier> [--section 1.4] [--json]
    python -m vantage.export plan    <dossier> --out <dir> [--depth standard] [--site-mode microsite] [--force]
    python -m vantage.export render  <dossier> --out <dir> [--format pptx ...] [--depth ...] [--json]
    python -m vantage.export schemas [--out harness/export/state]

``render`` is deterministic: it renders from the plans in ``<out>/plan/`` (authored or scaffold)
and never writes plans. The user-facing command is ``vantage export``; this entry point exists so
the Workflow agents have a stable, dependency-light interface.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _inspect(args) -> int:
    from .api import find_dossier
    from .dossier import load_dossier
    from .richtext import plain

    dossier = load_dossier(find_dossier(Path(args.dossier)))
    if args.section:
        node = dossier.find(args.section)
        if node is None:
            print(f"no section {args.section!r}", file=sys.stderr)
            return 1
        print(f"§{node.id} {plain(node.title)}  (level {node.level})")
        for block in node.blocks:
            extra = ""
            if block.kind == "table":
                extra = f" {len(block.rows)}×{len(block.header)} {block.header[:6]}"
            elif block.kind in {"chart", "figure"}:
                extra = f" {block.spec.id} {block.spec.title}"
            elif block.kind in {"paragraph", "callout"}:
                extra = f" {plain(block.text)[:100]}"
            print(f"  {block.kind}{extra}")
        for child in node.children:
            print(f"  └ §{child.id} {plain(child.title)}")
        return 0
    if args.json:
        print(json.dumps({
            "client": dossier.client, "as_of": dossier.as_of, "version": dossier.version,
            "tier": dossier.tier, "overall_confidence": dossier.overall_confidence,
            "eqi": dossier.eqi, "verification": dossier.verification,
            "client_domain": dossier.client_domain, "stats": dossier.stats(),
            "sections": [{"id": s.id, "title": plain(s.title),
                          "children": [c.id for c in s.children]} for s in dossier.sections],
        }, indent=2))
        return 0
    print(dossier.title)
    for key, value in dossier.front_matter.items():
        print(f"  {key}: {plain(value)[:140]}")
    print(f"  stats: {dossier.stats()}")
    for section in dossier.sections:
        print(f"  §{section.id:>4}  {plain(section.title)}  ({len(section.children)} subsections)")
    return 0


def _plan(args) -> int:
    from .api import find_dossier
    from .dossier import load_dossier
    from .pipeline import AuthoredPlanExists, write_plans

    source = find_dossier(Path(args.dossier))
    out = Path(args.out).expanduser() if args.out else source.parent / "exports"
    try:
        written = write_plans(load_dossier(source), out, args.depth, args.site_mode,
                              force=args.force)
    except AuthoredPlanExists as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    for path in sorted(written.glob("*.json")):
        print(f"  {path}  {path.stat().st_size // 1024 or 1} KB")
    return 0


def _render(args) -> int:
    from ..settings import load_config
    from .api import export, options_from_config

    cfg = load_config()
    opts = options_from_config(
        cfg, Path(args.dossier), formats=args.format or None, depth=args.depth,
        site_mode=args.site_mode, out_dir=Path(args.out) if args.out else None,
        classification=args.classification, brand=args.brand, authoring="deterministic")

    def emit(event) -> None:
        if args.json:
            print(event.to_json(), flush=True)
        elif event.type in {"artifact", "run_warning", "stage_done"}:
            print(f"{event.type:<12} {event.stage or ''} {event.message or ''}", file=sys.stderr)

    result = export(opts, emit=emit)
    if args.json:
        print(json.dumps({"result": result.to_dict()}))
    else:
        print(json.dumps(result.to_dict(), indent=2))
    return 0


def _schemas(args) -> int:
    from .pipeline import write_schemas

    target = Path(args.out) if args.out else (
        Path(__file__).resolve().parents[3] / "harness" / "export" / "state")
    for path in write_schemas(target):
        print(f"  {path}")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m vantage.export", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("inspect")
    p.add_argument("dossier")
    p.add_argument("--section", "-s")
    p.add_argument("--json", action="store_true")
    p = sub.add_parser("plan")
    p.add_argument("dossier")
    p.add_argument("--out", "-o")
    p.add_argument("--depth", default="standard", choices=["exec", "standard", "full"])
    p.add_argument("--site-mode", default="microsite", choices=["microsite", "deck"])
    p.add_argument("--force", action="store_true")
    p = sub.add_parser("render")
    p.add_argument("dossier")
    p.add_argument("--out", "-o")
    p.add_argument("--format", "-f", action="append", choices=["pptx", "docx", "pdf", "html"])
    p.add_argument("--depth", choices=["exec", "standard", "full"])
    p.add_argument("--site-mode", choices=["microsite", "deck"])
    p.add_argument("--classification")
    p.add_argument("--brand")
    p.add_argument("--json", action="store_true")
    p = sub.add_parser("schemas")
    p.add_argument("--out")
    args = ap.parse_args(argv)
    return {"inspect": _inspect, "plan": _plan, "render": _render, "schemas": _schemas}[
        args.cmd](args)


if __name__ == "__main__":
    raise SystemExit(main())
