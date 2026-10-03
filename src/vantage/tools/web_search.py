"""Web search tool — Tavily (default) or Brave. The engine's substitute for Claude Code's
built-in web_search, which programmatic backends do not have."""

from __future__ import annotations

import asyncio
import os

import httpx

from ..models.config import WebSearchCfg
from ..providers.base import ToolSpec
from .base import ToolImpl

_SPEC = ToolSpec(
    name="web_search",
    description=(
        "Search the public web for current information. Returns ranked results with title, URL, "
        "and a content snippet. Use targeted queries; prefer primary sources (filings, IR, "
        "official press). Each result's URL should be registered as a source when cited."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "query": {"type": "string"},
            "max_results": {"type": "integer", "default": 6},
        },
        "required": ["query"],
    },
)


class WebSearchTool(ToolImpl):
    def __init__(self, cfg: WebSearchCfg) -> None:
        self.spec = _SPEC
        self._cfg = cfg
        self._provider = cfg.provider
        self._key_env = ("BRAVE_API_KEY" if cfg.provider == "brave"
                         and cfg.api_key_env == "TAVILY_API_KEY" else cfg.api_key_env)
        self._key = os.environ.get(self._key_env, "")

    async def run(self, args: dict) -> str:
        query = args.get("query", "").strip()
        if not query:
            return self.error("empty query")
        n = max(1, min(int(args.get("max_results", self._cfg.max_results)), self._cfg.max_results))
        if not self._key:
            return self.error(
                f"{self._provider} web search key not set "
                f"({self._key_env})"
            )
        try:
            async with asyncio.timeout(self._cfg.timeout_seconds):
                if self._provider == "brave":
                    return await self._brave(query, n)
                return await self._tavily(query, n)
        except Exception as e:  # pragma: no cover
            return self.error(f"{self._provider}: {e}")

    async def _tavily(self, query: str, n: int) -> str:
        from tavily import AsyncTavilyClient

        client = AsyncTavilyClient(api_key=self._key)
        res = await client.search(query=query, max_results=n, search_depth=self._cfg.search_depth)
        lines = []
        for r in res.get("results", []):
            lines.append(f"- {r.get('title', '')}\n  {r.get('url', '')}\n  {(r.get('content') or '')[:self._cfg.snippet_max_chars]}")
        if res.get("answer"):
            lines.insert(0, f"Answer: {res['answer']}\n")
        return "\n".join(lines) or "(no results)"

    async def _brave(self, query: str, n: int) -> str:
        async with httpx.AsyncClient(timeout=self._cfg.timeout_seconds) as c:
            resp = await c.get(
                "https://api.search.brave.com/res/v1/web/search",
                params={"q": query, "count": n},
                headers={"X-Subscription-Token": self._key, "Accept": "application/json"},
            )
            resp.raise_for_status()
            data = resp.json()
        lines = []
        for r in (data.get("web", {}) or {}).get("results", [])[:n]:
            lines.append(f"- {r.get('title', '')}\n  {r.get('url', '')}\n  {(r.get('description') or '')[:self._cfg.snippet_max_chars]}")
        return "\n".join(lines) or "(no results)"
