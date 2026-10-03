"""Tool base — a named callable exposing a ``ToolSpec`` and an async ``run``."""

from __future__ import annotations

from ..providers.base import ToolSpec


class ToolImpl:
    spec: ToolSpec

    async def run(self, args: dict) -> str:  # pragma: no cover - interface
        raise NotImplementedError

    @staticmethod
    def error(msg: str) -> str:
        """Tools never raise into the agent loop; they return a flagged error string."""
        return f"[tool error] {msg}"
