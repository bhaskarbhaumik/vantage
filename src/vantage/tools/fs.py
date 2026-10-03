"""Run-directory file tools: read_file, list_dir. Sandboxed to the run dir + harness."""

from __future__ import annotations

from pathlib import Path

from ..providers.base import ToolSpec
from .base import ToolImpl


class _Sandboxed:
    def __init__(self, roots: list[Path]) -> None:
        self._roots = [r.resolve() for r in roots]

    def resolve(self, rel: str) -> Path | None:
        for root in self._roots:
            p = (root / rel).resolve()
            if str(p).startswith(str(root)):
                if p.exists():
                    return p
        # also allow absolute paths that live under a root
        p = Path(rel).resolve()
        if any(str(p).startswith(str(r)) for r in self._roots) and p.exists():
            return p
        return None


class ReadFileTool(ToolImpl):
    def __init__(self, run_dir: Path, harness_dir: Path) -> None:
        self._sb = _Sandboxed([run_dir, harness_dir])
        self.spec = ToolSpec(
            name="read_file",
            description=(
                "Read a UTF-8 text file from the current run directory (sections/, state/, qa/) "
                "or the harness. Paths are relative to the run dir. Use to consume upstream "
                "sections, state.json, fragments, and evidence-audit output."
            ),
            input_schema={
                "type": "object",
                "properties": {"path": {"type": "string", "description": "relative path, e.g. sections/04-financials.md"}},
                "required": ["path"],
            },
        )

    async def run(self, args: dict) -> str:
        p = self._sb.resolve(args.get("path", ""))
        if not p:
            return self.error(f"not found or out of sandbox: {args.get('path')!r}")
        try:
            text = p.read_text(encoding="utf-8")
        except Exception as e:  # pragma: no cover
            return self.error(str(e))
        return text[:200_000]


class ListDirTool(ToolImpl):
    def __init__(self, run_dir: Path) -> None:
        self._root = run_dir.resolve()
        self.spec = ToolSpec(
            name="list_dir",
            description="List files under a directory in the current run (relative to the run dir).",
            input_schema={
                "type": "object",
                "properties": {"path": {"type": "string", "default": "."}},
            },
        )

    async def run(self, args: dict) -> str:
        rel = args.get("path", ".")
        p = (self._root / rel).resolve()
        if not str(p).startswith(str(self._root)) or not p.exists():
            return self.error(f"not found or out of sandbox: {rel!r}")
        entries = sorted(str(x.relative_to(self._root)) + ("/" if x.is_dir() else "") for x in p.iterdir())
        return "\n".join(entries) or "(empty)"
