"""
StockApp market data worker — entry point.

Usage:
  python -m src.main              # Single run (used by GitHub Actions)
  python -m src.main --loop       # Run forever, sleeping between iterations
  python -m src.main --loop --interval 900   # every 15 minutes

Environment variables (.env or GitHub Secrets):
  SUPABASE_URL                — your project URL
  SUPABASE_SERVICE_ROLE_KEY   — secret key with full DB access
"""

from __future__ import annotations

import argparse
import logging
import sys
import time

from dotenv import load_dotenv

from .db import upsert_stocks
from .fetcher import fetch_quotes
from .universe import SYMBOLS

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    level=logging.INFO,
)
log = logging.getLogger("worker")


def run_once() -> None:
    log.info("Starting run: %d symbols in universe", len(SYMBOLS))
    quotes = fetch_quotes(SYMBOLS)
    written = upsert_stocks(quotes)
    log.info("Run complete: wrote %d rows", written)


def main() -> int:
    load_dotenv()

    parser = argparse.ArgumentParser(description="StockApp market data worker")
    parser.add_argument("--loop", action="store_true", help="Run continuously")
    parser.add_argument(
        "--interval",
        type=int,
        default=1800,
        help="Seconds between runs in loop mode (default: 1800 = 30 min)",
    )
    args = parser.parse_args()

    if not args.loop:
        run_once()
        return 0

    log.info("Loop mode: interval=%ds", args.interval)
    while True:
        try:
            run_once()
        except Exception as e:  # noqa: BLE001
            log.exception("Run failed: %s", e)
        log.info("Sleeping %ds until next run", args.interval)
        time.sleep(args.interval)


if __name__ == "__main__":
    sys.exit(main())
