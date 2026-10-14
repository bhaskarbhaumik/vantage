"""Run events — the structured stream the Ink TUI (and logs) consume."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

EventType = Literal[
    "run_start",
    "stage_start",
    "agent_start",
    "agent_tool",
    "agent_progress",
    "agent_done",
    "agent_error",
    "stage_done",
    "run_done",
    "run_warning",
    "run_error",
    "log",
    # `vantage export`: one per file written; data = {format, path, bytes, pages?, slides?}.
    "artifact",
]


class RunEvent(BaseModel):
    """One line of the run's JSONL event stream."""

    type: EventType
    ts: float = 0.0
    stage: str | None = None
    agent: str | None = None
    message: str | None = None
    data: dict[str, Any] = Field(default_factory=dict)

    def to_json(self) -> str:
        return self.model_dump_json()
