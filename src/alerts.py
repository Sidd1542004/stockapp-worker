"""
Price alert checking, folded into the existing worker run.

After the worker updates prices, it calls check_alerts(), which:
  1. Loads all un-triggered alerts joined with the latest price.
  2. Finds any whose threshold was crossed (price >= target for 'above',
     price <= target for 'below').
  3. Emails the user and marks the alert as triggered.

Email uses Resend (free tier: 100/day, 3,000/month). If RESEND_API_KEY isn't
set, alert-checking is skipped gracefully so the price update still succeeds.

This needs the SERVICE ROLE key (already used by the worker) because it reads
across all users' alerts and looks up their email addresses.
"""

from __future__ import annotations

import logging
import os

import requests
from supabase import create_client

log = logging.getLogger(__name__)


def _client():
    url = os.environ["SUPABASE_URL"]
    key = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
    return create_client(url, key)


def _send_email(to_email: str, subject: str, html: str) -> bool:
    """Send an email via Resend. Returns True on success."""
    api_key = os.environ.get("RESEND_API_KEY")
    if not api_key:
        return False

    # Resend requires a verified domain for custom 'from' addresses. Their
    # onboarding@resend.dev works out of the box for testing.
    from_addr = os.environ.get("ALERT_FROM_EMAIL", "StockApp <onboarding@resend.dev>")

    try:
        resp = requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "from": from_addr,
                "to": [to_email],
                "subject": subject,
                "html": html,
            },
            timeout=15,
        )
        if resp.status_code >= 300:
            log.warning("Resend error %s: %s", resp.status_code, resp.text[:200])
            return False
        return True
    except Exception as e:  # noqa: BLE001
        log.warning("Email send failed: %s", e)
        return False


def check_alerts() -> int:
    """
    Check all active alerts against current prices, email + mark triggered.
    Returns the number of alerts triggered this run.
    """
    if not os.environ.get("RESEND_API_KEY"):
        log.info("RESEND_API_KEY not set — skipping alert checks")
        return 0

    client = _client()

    # Active (un-triggered) alerts.
    alerts_resp = (
        client.table("price_alerts")
        .select("id, user_id, symbol, direction, target_price")
        .eq("triggered", False)
        .execute()
    )
    alerts = alerts_resp.data or []
    if not alerts:
        return 0

    # Current prices for the symbols involved.
    symbols = list({a["symbol"] for a in alerts})
    prices_resp = (
        client.table("stocks")
        .select("symbol, current_price, name")
        .in_("symbol", symbols)
        .execute()
    )
    price_map = {r["symbol"]: r for r in (prices_resp.data or [])}

    triggered_count = 0

    for alert in alerts:
        stock = price_map.get(alert["symbol"])
        if not stock or stock["current_price"] is None:
            continue

        price = float(stock["current_price"])
        target = float(alert["target_price"])
        direction = alert["direction"]

        crossed = (direction == "above" and price >= target) or (
            direction == "below" and price <= target
        )
        if not crossed:
            continue

        # Look up the user's email via the auth admin API.
        email = _get_user_email(client, alert["user_id"])
        if email:
            subject = f"{alert['symbol']} is {direction} ${target:.2f}"
            html = (
                f"<h2>Price alert triggered</h2>"
                f"<p><strong>{stock.get('name', alert['symbol'])} "
                f"({alert['symbol']})</strong> is now "
                f"<strong>${price:.2f}</strong>, which is {direction} your "
                f"target of ${target:.2f}.</p>"
                f"<p style='color:#888;font-size:12px'>You set this alert on "
                f"StockApp. This is a paper-trading app for learning — not "
                f"financial advice.</p>"
            )
            _send_email(email, subject, html)

        # Mark triggered regardless of email success, so we don't spam retries.
        client.table("price_alerts").update(
            {"triggered": True, "triggered_at": "now()"}
        ).eq("id", alert["id"]).execute()
        triggered_count += 1

    if triggered_count:
        log.info("Triggered %d price alerts", triggered_count)
    return triggered_count


def _get_user_email(client, user_id: str) -> str | None:
    """Fetch a user's email via the Supabase admin API."""
    try:
        resp = client.auth.admin.get_user_by_id(user_id)
        return resp.user.email if resp and resp.user else None
    except Exception as e:  # noqa: BLE001
        log.warning("Couldn't fetch email for %s: %s", user_id, e)
        return None
