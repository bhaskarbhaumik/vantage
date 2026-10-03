"""Market-data tool (yfinance) — quotes, multiples, and headline statements for a ticker."""

from __future__ import annotations

import asyncio

from ..providers.base import ToolSpec
from .base import ToolImpl

_SPEC = ToolSpec(
    name="market_data",
    description=(
        "Fetch market data for a public ticker: price, market cap, valuation multiples "
        "(P/E, EV/EBITDA), sector, and headline income-statement lines. Use for §4.5 valuation "
        "context. Figures are point-in-time; label the retrieval date when cited."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "ticker": {"type": "string"},
            "want": {"type": "string", "enum": ["summary", "financials"], "default": "summary"},
        },
        "required": ["ticker"],
    },
)


class MarketDataTool(ToolImpl):
    def __init__(self) -> None:
        self.spec = _SPEC

    async def run(self, args: dict) -> str:
        return await asyncio.to_thread(self._run_sync, args)

    def _run_sync(self, args: dict) -> str:
        try:
            import yfinance as yf

            t = yf.Ticker(args["ticker"])
            if args.get("want") == "financials":
                fin = t.financials
                return f"{args['ticker']} income statement (recent):\n{str(fin)[:3000]}"
            info = t.info or {}
            keys = [
                "shortName", "sector", "industry", "currentPrice", "currency", "marketCap",
                "trailingPE", "forwardPE", "enterpriseToEbitda", "priceToSalesTrailing12Months",
                "totalRevenue", "ebitda", "profitMargins", "revenueGrowth", "recommendationKey",
                "targetMeanPrice", "numberOfAnalystOpinions",
            ]
            lines = [f"{k}: {info.get(k)}" for k in keys if info.get(k) is not None]
            return f"{args['ticker']} market data:\n" + "\n".join(lines) if lines else self.error("no data")
        except Exception as e:  # pragma: no cover
            return self.error(f"yfinance: {e}")
