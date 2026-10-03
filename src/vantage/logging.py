"""Logging + the run-event emitter.

Two output channels, deliberately separated:

* **Human logs** → stderr via Rich. Never stdout, so the CLI can keep stdout clean for the
  JSON event stream the Ink TUI reads.
* **Run events** → an ``EventEmitter``: appends JSONL to ``<run>/run.jsonl``, optionally
  prints one JSON object per line to stdout (``--json`` mode), and fans out to a callback.
"""

from __future__ import annotations

import logging
import os
import sys
import time
from collections.abc import Callable
from pathlib import Path

from rich.console import Console
from rich.logging import RichHandler

from .models.events import RunEvent

_console = Console(stderr=True)


def get_console() -> Console:
    return _console


def get_logger(name: str = "vantage") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        level = os.environ.get("VANTAGE_LOG_LEVEL", "INFO").upper()
        handler = RichHandler(console=_console, rich_tracebacks=True, show_path=False, markup=True)
        handler.setFormatter(logging.Formatter("%(message)s", datefmt="[%X]"))
        logger.addHandler(handler)
        logger.setLevel(getattr(logging, level, logging.INFO))
        logger.propagate = False
    return logger


EventSink = Callable[[RunEvent], None]


class EventEmitter:
    """Fan-out sink for run events: JSONL file, optional stdout JSON, and callbacks."""

    def __init__(
        self,
        jsonl_path: str | Path | None = None,
        stdout_json: bool = False,
        callback: EventSink | None = None,
    ) -> None:
        self._fh = None
        if jsonl_path:
            p = Path(jsonl_path)
            p.parent.mkdir(parents=True, exist_ok=True)
            self._fh = open(p, "a", encoding="utf-8")
        self._stdout_json = stdout_json
        self._callback = callback

    def emit(self, event: RunEvent) -> None:
        if not event.ts:
            event.ts = time.time()
        line = event.to_json()
        if self._fh:
            self._fh.write(line + "\n")
            self._fh.flush()
        if self._stdout_json:
            sys.stdout.write(line + "\n")
            sys.stdout.flush()
        if self._callback:
            try:
                self._callback(event)
            except Exception:  # pragma: no cover - a bad sink must never kill a run
                pass

    # convenience helpers -------------------------------------------------------
    def event(self, type_: str, **kw) -> None:
        self.emit(RunEvent(type=type_, **kw))  # type: ignore[arg-type]

    def close(self) -> None:
        if self._fh:
            self._fh.close()
            self._fh = None
