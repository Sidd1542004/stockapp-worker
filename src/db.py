"""
Supabase writes for the stocks table.

Batch A update: the upsert payload now includes asset_type ("stock", "etf",
"crypto") so the UI can adapt for assets without traditional fundamentals.

Uses the SERVICE ROLE key — it bypasses row-level security so the worker can
freely write the shared stocks table. Guard this key like a password.
"""

from __future__ import annotations

import logging
import os
from datetime import datetime, timezone

from supabase import Client, create_client

from .universe import BY_SYMBOL

log = logging.getLogger(__name__)


def _client() -> Client:
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        raise RuntimeError(
            "Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY. "
            "Set them in your .env file (local) or GitHub Secrets (CI)."
        )
    return create_client(url, key)


def upsert_stocks(quotes: list[dict]) -> int:
    """
    Upsert price + fundamentals + asset_type into the `stocks` table.

    Metadata (name, exchange, sector, asset_type) is enriched from the universe
    so rows can be cleanly inserted if they don't yet exist. Returns rows
    written.
    """
    if not quotes:
        return 0

    now_iso = datetime.now(timezone.utc).isoformat()

    payload = []
    for q in quotes:
        meta = BY_SYMBOL.get(q["symbol"])
        if not meta:
            log.warning("Skipping %s: not in universe metadata", q["symbol"])
            continue
        payload.append({
            "symbol": q["symbol"],
            "name": meta["name"],
            "exchange": meta["exchange"],
            "sector": meta["sector"],
            "asset_type": meta.get("asset_type", "stock"),
            "current_price": q["current_price"],
            "day_change_pct": q["day_change_pct"],
            "market_cap": q.get("market_cap"),
            "pe_ratio": q.get("pe_ratio"),
            "dividend_yield": q.get("dividend_yield"),
            "updated_at": now_iso,
        })

    log.info("Upserting %d rows to Supabase", len(payload))
    client = _client()
    client.table("stocks").upsert(payload, on_conflict="symbol").execute()
    return len(payload)
