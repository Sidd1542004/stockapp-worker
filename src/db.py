"""
Supabase writes for the stocks table.

We use the SERVICE ROLE key here — it bypasses row-level security so the
worker can freely UPDATE the shared stocks table. Guard this key like a
password: it grants full database access.
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
    Upsert the given quotes into the `stocks` table.

    Each quote must contain: symbol, current_price, day_change_pct.
    Metadata (name, exchange, sector) is enriched from the universe so that
    rows can be INSERTED cleanly if they don't yet exist.

    Returns the number of rows written.
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
            "current_price": q["current_price"],
            "day_change_pct": q["day_change_pct"],
            "updated_at": now_iso,
        })

    log.info("Upserting %d rows to Supabase", len(payload))
    client = _client()
    # on_conflict=symbol → INSERT if new, UPDATE if it already exists
    client.table("stocks").upsert(payload, on_conflict="symbol").execute()
    return len(payload)
