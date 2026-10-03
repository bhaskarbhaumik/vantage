"""Assemble the tool set for a run and dispatch tool calls by name."""

from __future__ import annotations

import asyncio
from pathlib import Path

from ..models.config import Config
from ..providers.base import ToolSpec
from .base import ToolImpl
from .edgar import EdgarTool
from .fs import ListDirTool, ReadFileTool
from .market_data import MarketDataTool
from .web_search import WebSearchTool

# Tools available to each stage class. `submit` is injected by the executor (terminal).
RESEARCH_TOOLS = ["web_search", "sec_edgar", "market_data", "read_file", "list_dir"]
RECONCILE_TOOLS = ["read_file", "list_dir"]


class ToolRegistry:
    def __init__(self, cfg: Config, run_dir: Path, harness_dir: Path) -> None:
        self._tools: dict[str, ToolImpl] = {}
        self._timeout = cfg.engine.tool_timeout_seconds
        t = cfg.tools
        if t.web_search.enabled:
            self._tools["web_search"] = WebSearchTool(t.web_search)
        if t.edgar.enabled:
            self._tools["sec_edgar"] = EdgarTool(t.edgar)
        if t.market_data.enabled:
            self._tools["market_data"] = MarketDataTool()
        self._tools["read_file"] = ReadFileTool(run_dir, harness_dir)
        self._tools["list_dir"] = ListDirTool(run_dir)

    def has(self, name: str) -> bool:
        return name in self._tools

    def specs(self, names: list[str]) -> list[ToolSpec]:
        return [self._tools[n].spec for n in names if n in self._tools]

    async def run(self, name: str, args: dict) -> str:
        tool = self._tools.get(name)
        if tool is None:
            return ToolImpl.error(f"unknown tool: {name}")
        try:
            async with asyncio.timeout(self._timeout):
                return await tool.run(args)
        except TimeoutError:
            return ToolImpl.error(f"{name} timed out after {self._timeout:g}s")
