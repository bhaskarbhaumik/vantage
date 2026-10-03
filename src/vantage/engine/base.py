"""Backend interface."""

from __future__ import annotations

import importlib
import importlib.util
import warnings
from abc import ABC, abstractmethod
from pathlib import Path

from ..blueprint.loader import Blueprint
from ..logging import EventEmitter
from ..models.config import Config
from ..pipeline.orchestrator import RunJob, RunResult


def probe_available(module: str) -> tuple[bool, str | None]:
    """Report whether an optional dependency is usable.

    Returns ``(installed, import_error)``:
      * ``(False, None)``   — not installed (fast; no execution, so no import-time noise).
      * ``(True, None)``    — installed and imports cleanly.
      * ``(True, "<err>")`` — installed but fails to import here (e.g. a transitive dep that is
                              incompatible with this Python version).

    Import-time warnings are suppressed so diagnostics stay clean — some optional deps (e.g.
    crewai → chromadb) emit a ``UserWarning`` on Python 3.14.
    """
    try:
        if importlib.util.find_spec(module) is None:
            return (False, None)
    except Exception:
        return (False, None)
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            importlib.import_module(module)
        return (True, None)
    except Exception as e:  # installed but not importable (e.g. Python-version incompatibility)
        return (True, f"{type(e).__name__}: {e}")


class Backend(ABC):
    name: str = "base"

    def __init__(
        self,
        cfg: Config,
        blueprint: Blueprint,
        harness_dir: str | Path,
        emitter: EventEmitter | None = None,
    ) -> None:
        self.cfg = cfg
        self.bp = blueprint
        self.harness_dir = Path(harness_dir)
        self.emitter = emitter or EventEmitter()

    @abstractmethod
    async def run(self, job: RunJob) -> RunResult: ...

    def check(self) -> list[str]:
        """Return a list of human-readable readiness issues (empty = ready)."""
        return []

    # helpers -------------------------------------------------------------------
    def _run_dir(self, job: RunJob) -> Path:
        d = Path(self.cfg.engine.output_dir).expanduser() / job.slug
        d.mkdir(parents=True, exist_ok=True)
        return d

    def _empty_result(self, job: RunJob) -> RunResult:
        return RunResult(slug=job.slug, run_dir=str(self._run_dir(job)))

    def _anthropic_key(self) -> str:
        from ..auth import key_env

        return key_env(self.cfg, "anthropic")

    def _auth_issues(self) -> list[str]:
        """Credential readiness under the active auth mode (subscription vs api-key)."""
        from ..auth import readiness

        return readiness(self.cfg, self.name)
