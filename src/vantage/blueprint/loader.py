"""Read-through access to the bundled harness prompt/contract library.

The harness Markdown is the single source of truth for *what* each agent does. The engine never
hard-codes section content; it hands each agent its brief plus the shared contracts at runtime,
exactly as the Claude Code Workflow harness does.
"""

from __future__ import annotations

import json
from pathlib import Path


class Blueprint:
    def __init__(self, harness_dir: Path) -> None:
        self.dir = Path(harness_dir)
        if not self.dir.exists():
            raise FileNotFoundError(f"harness dir not found: {self.dir}")
        self._cache: dict[str, str] = {}

    @property
    def dossier_suffix(self) -> str:
        """``<slug>-<suffix>.md`` — the dossier file name suffix."""
        return "vantage"

    # ---- raw file access (instance-cached) -----------------------------------
    def _read(self, rel: str) -> str:
        if rel in self._cache:
            return self._cache[rel]
        p = self.dir / rel
        if not p.exists():
            raise FileNotFoundError(f"harness file missing: {rel} (looked in {self.dir})")
        text = p.read_text(encoding="utf-8")
        self._cache[rel] = text
        return text

    # ---- named docs -----------------------------------------------------------
    def system_prompt(self) -> str:
        return self._read("prompts/system-vantage-analyst.md")

    def common(self) -> str:
        return self._read("prompts/briefs/_common.md")

    def brief(self, filename: str) -> str:
        return self._read(f"prompts/briefs/{filename}")

    def id_allocation(self) -> str:
        return self._read("prompts/id-allocation.md")

    def blueprint_doc(self) -> str:
        return self._read("blueprint/vantage-blueprint-v3.md")

    def evidence_policy(self) -> str:
        return self._read("blueprint/evidence-policy.md")

    def jurisdiction_adapters(self) -> str:
        return self._read("blueprint/jurisdiction-adapters.md")

    def tooling_map(self) -> str:
        return self._read("blueprint/tooling-map.md")

    def section_contracts(self) -> str:
        return self._read("blueprint/section-contracts.md")

    def scoring_rubrics(self) -> str:
        return self._read("blueprint/scoring-rubrics.md")

    def vertical_modules(self) -> str:
        return self._read("blueprint/vertical-modules.md")

    def verification_protocol(self) -> str:
        return self._read("blueprint/verification-protocol.md")

    def state_schema(self) -> dict:
        return json.loads(self._read("state/state.schema.json"))

    def workflow_path(self) -> Path:
        return self.dir / "workflows/vantage-v3.workflow.mjs"

    # ---- convenience bundles --------------------------------------------------
    def reference_docs(self) -> dict[str, str]:
        """The shared contracts every agent may consult, keyed by short name."""
        return {
            "blueprint": self.blueprint_doc(),
            "evidence_policy": self.evidence_policy(),
            "section_contracts": self.section_contracts(),
            "id_allocation": self.id_allocation(),
            "jurisdiction_adapters": self.jurisdiction_adapters(),
            "tooling_map": self.tooling_map(),
            "scoring_rubrics": self.scoring_rubrics(),
            "vertical_modules": self.vertical_modules(),
            "verification_protocol": self.verification_protocol(),
        }
