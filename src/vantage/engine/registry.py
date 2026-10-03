"""Backend registry — name → Backend class, plus a factory."""

from __future__ import annotations

from pathlib import Path

from ..blueprint.loader import Blueprint
from ..logging import EventEmitter
from ..models.config import Config
from .adk_backend import AdkBackend
from .agent_sdk_backend import AgentSdkBackend
from .api_backend import ApiBackend
from .base import Backend
from .crewai_backend import CrewAiBackend
from .langgraph_backend import LangGraphBackend
from .workflow_backend import WorkflowBackend

# Order matters for display: default first.
_CLASSES = [WorkflowBackend, ApiBackend, AgentSdkBackend, LangGraphBackend, AdkBackend, CrewAiBackend]
BACKENDS: dict[str, type[Backend]] = {c.name: c for c in _CLASSES}


def get_backend(
    name: str,
    cfg: Config,
    blueprint: Blueprint,
    harness_dir: str | Path,
    emitter: EventEmitter | None = None,
) -> Backend:
    cls = BACKENDS.get(name)
    if cls is None:
        raise ValueError(f"unknown backend {name!r}; choose from {list(BACKENDS)}")
    return cls(cfg, blueprint, harness_dir, emitter)
