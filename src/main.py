"""
StockApp market data worker — entry point.

Batch B update: after updating prices, the worker also checks price alerts and
emails users whose thresholds were crossed. No separate scheduler needed — it
piggybacks on the existing 30-minute price run.

Usage:
  python -m src.main              # Single run (used by GitHub Actions)
  python -m src.main --loop       # Run forever, sleeping between iterations

Environment variables:
  SUPABASE_URL                — your project URL
  SUPABASE_SERVICE_ROLE_KEY   — secret key with full DB access
  RESEND_API_KEY              — (optional) enables price-alert emails
  ALERT_FROM_EMAIL            — (optional) verified sender, else resend.dev
"""

from __future__ import annotations

import argparse
import logging
import sys
import time

from dotenv import load_dotenv

from .alerts import check_alerts
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
    log.info("Prices written: %d rows", written)

    # Check price alerts against the freshly written prices.
    try:
        triggered = check_alerts()
        if triggered:
            log.info("Alerts triggered: %d", triggered)
    except Exception as e:  # noqa: BLE001
        # Never let alert failures break the price pipeline.
        log.exception("Alert check failed: %s", e)

    log.info("Run complete")


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
