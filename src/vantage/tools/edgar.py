"""SEC EDGAR tool (edgartools) — Tier-1 filings for US registrants.

Defensive by design: on any failure it returns a flagged error string rather than raising, so
the agent loop treats an unavailable filing as a gap, not a crash.
"""

from __future__ import annotations

import asyncio
import os

from ..models.config import EdgarCfg
from ..providers.base import ToolSpec
from .base import ToolImpl

_SPEC = ToolSpec(
    name="sec_edgar",
    description=(
        "Look up a US SEC registrant on EDGAR and return recent filings and/or headline financials. "
        "Authoritative (Tier 1) for financials, segments, risk factors, governance. "
        "want='filings' lists recent filings; want='financials' returns the latest income "
        "statement / balance sheet highlights; want='facts' returns key company facts."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "ticker (preferred) or company name"},
            "want": {"type": "string", "enum": ["filings", "financials", "facts"], "default": "facts"},
            "form": {"type": "string", "description": "e.g. 10-K, 10-Q, 8-K, DEF 14A (for want=filings)"},
            "limit": {"type": "integer", "default": 8},
        },
        "required": ["query"],
    },
)


class EdgarTool(ToolImpl):
    def __init__(self, cfg: EdgarCfg) -> None:
        self.spec = _SPEC
        self._cfg = cfg
        self._identity = os.environ.get(cfg.identity_env, "")

    async def run(self, args: dict) -> str:
        if not self._identity:
            return self.error("SEC_EDGAR_IDENTITY not set (SEC requires 'Name email@example.com')")
        return await asyncio.to_thread(self._run_sync, args)

    def _run_sync(self, args: dict) -> str:
        try:
            import edgar

            edgar.set_identity(self._identity)
            query = args["query"]
            want = args.get("want", "facts")
            try:
                company = edgar.Company(query)
            except Exception:
                found = edgar.find(query)
                company = found[0] if hasattr(found, "__getitem__") else found

            if want == "filings":
                form = args.get("form")
                limit = max(1, min(int(args.get("limit", self._cfg.filings_limit)), self._cfg.filings_limit))
                filings = company.get_filings(form=form) if form else company.get_filings()
                rows = []
                for f in list(filings)[:limit]:
                    rows.append(f"- {getattr(f, 'form', '?')} | {getattr(f, 'filing_date', '?')} | {getattr(f, 'accession_no', '')}")
                return f"{company.name} ({company.cik}) recent filings:\n" + "\n".join(rows)

            if want == "financials":
                fin = company.financials
                parts = [f"{company.name} ({company.cik}) — latest financials"]
                for name in ("income_statement", "balance_sheet", "cashflow_statement"):
                    stmt = getattr(fin, name, None)
                    if stmt is not None:
                        parts.append(f"\n## {name}\n{str(stmt)[:self._cfg.statement_max_chars]}")
                return "\n".join(parts)

            # facts
            return (
                f"{company.name} | CIK {company.cik} | "
                f"SIC {getattr(company, 'sic', '?')} | "
                f"tickers {getattr(company, 'tickers', '?')} | "
                f"industry {getattr(company, 'industry', '?')}"
            )
        except Exception as e:
            return self.error(f"edgar: {e}")
