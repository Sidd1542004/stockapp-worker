# StockApp — Market Data Worker

A lightweight Python service that keeps the StockApp database fresh. It fetches
prices and fundamentals for the whole asset universe, writes them to Supabase,
and checks price alerts — emailing users when their thresholds are crossed.

Runs **free** on GitHub Actions every 30 minutes. No dedicated server needed.

This is the **worker**. It pairs with the **web app** (Next.js) — see that
project's README. The two connect only through the shared Supabase database:
the worker writes prices, the web app reads them.

---

## What it does

On each run (every ~30 minutes via GitHub Actions):

1. **Fetches quotes** — batch-downloads the latest price + day change for the
   whole universe from Yahoo Finance (via `yfinance`), and pulls key
   fundamentals (market cap, P/E, dividend yield) per symbol.
2. **Writes to Supabase** — upserts everything into the `stocks` table, which
   the web app reads for dashboards, screening, charts, and trading.
3. **Checks price alerts** — compares fresh prices against users' active alerts
   and emails anyone whose target was crossed (via Resend), marking the alert
   triggered so it won't fire twice.

If email isn't configured, alert-checking is skipped gracefully and the price
update still succeeds.

---

## The universe

Defined in `src/universe.py` — currently 76 assets:

- **60 stocks** — 30 US mega-caps + 30 Indian (Nifty) names
- **8 ETFs** — SPY, VOO, QQQ, VTI, IWM, DIA, GLD, VEA
- **8 cryptocurrencies** — BTC, ETH, SOL, BNB, XRP, ADA, DOGE, AVAX

Each entry has a `symbol`, `name`, `exchange`, `sector`, and `asset_type`
(`stock` / `etf` / `crypto`). To add more, append to the list — the next run
picks them up automatically.

**Symbol conventions (Yahoo Finance):**

| Asset          | Format         | Example        |
|----------------|----------------|----------------|
| US stock/ETF   | plain ticker   | `AAPL`, `SPY`  |
| India (NSE)    | `.NS` suffix   | `RELIANCE.NS`  |
| India (BSE)    | `.BO` suffix   | `RELIANCE.BO`  |
| Crypto         | `-USD` suffix  | `BTC-USD`      |
| UK (LSE)       | `.L` suffix    | `HSBA.L`       |

Note: symbols change over time (companies get renamed, demerged, delisted). The
fetcher skips any symbol that fails rather than crashing, so a stale entry just
means one missing row until you update it.

---

## Tech stack

- **Python 3.11+**
- **yfinance** — free Yahoo Finance data (no API key)
- **supabase** (Python client) — database writes
- **requests** — calling the Resend email API
- **python-dotenv** — local env loading
- **GitHub Actions** — free scheduler (unlimited minutes on public repos)

---

## Project structure

```
src/
├── universe.py      The list of tracked assets + metadata
├── fetcher.py       Batch price download + per-symbol fundamentals
├── db.py            Upserts into the Supabase stocks table
├── alerts.py        Checks price alerts, sends emails via Resend
└── main.py          Entry point: run once, or loop
.github/workflows/
└── update-quotes.yml  Runs the worker every 30 minutes
requirements.txt
```

---

## Environment variables

Create `.env` in the project root (never commit it):

```
# Supabase — same URL as the web app; use the SERVICE ROLE key (not anon).
# Find it in Supabase: Project Settings → API → service_role (secret).
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-secret-key

# Resend — price-alert emails (free tier) from https://resend.com. Optional:
# without it, alerts are stored but no email is sent.
RESEND_API_KEY=your-resend-key
ALERT_FROM_EMAIL=StockApp <onboarding@resend.dev>
```

> ⚠️ The **service role key** bypasses row-level security and has full database
> access. Treat it like a password. It belongs only in `.env` (gitignored) and
> GitHub Secrets — never in the web app, never committed, never shared.

---

## Running locally

```bash
python -m venv .venv
source .venv/bin/activate         # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python -m src.main                # single run (fetch + write + check alerts)
python -m src.main --loop         # run forever, 30-min interval
python -m src.main --loop --interval 900   # every 15 minutes
```

A run typically takes a minute or two (fundamentals are fetched per symbol).
You should see it upsert ~76 rows. Refresh the web app dashboard to see fresh
prices.

Shortcut (skip venv activation):

```bash
.venv\Scripts\python -m src.main    # Windows, one line
```

---

## Deploying (GitHub Actions — free)

This is the recommended way to keep prices fresh automatically.

1. Push this folder to a GitHub repo. **Make it public** for unlimited Actions
   minutes (private repos are capped at 2,000/month).
2. Add repo secrets under **Settings → Secrets and variables → Actions**:
   - `SUPABASE_URL`
   - `SUPABASE_SERVICE_ROLE_KEY`
   - `RESEND_API_KEY` (optional, for alert emails)
   - `ALERT_FROM_EMAIL` (optional)
3. Trigger the first run: **Actions → Update stock quotes → Run workflow**.

From then on it runs itself every 30 minutes. (GitHub's cron is best-effort and
may drift 5–15 minutes during peak load — that's normal.)

---

## Troubleshooting

- **"Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY"** — `.env` isn't being
  read. Run from the worker root and confirm `.env` exists there.
- **RLS violation on write** — you used the anon key. Use the `service_role` key.
- **A symbol logs "possibly delisted"** — that ticker changed or was removed.
  Update it in `universe.py` (e.g. Tata Motors demerged into `TMPV.NS`/`TMCV.NS`).
- **`getaddrinfo failed`** — the Supabase URL is wrong/placeholder, or no network.
- **`YFRateLimitError`** — Yahoo temporarily rate-limited your IP; wait ~15 min,
  or reduce universe size / run frequency.
- **Alerts not emailing** — `RESEND_API_KEY` not set, or the sender domain isn't
  verified (use the default `onboarding@resend.dev` for testing).

---

## Notes

- **Crypto trades 24/7**, so BTC-USD etc. always have fresh prices; stocks and
  ETFs follow market hours.
- **Dividend yield** is normalized to a fraction (0.02 = 2%) before storing —
  see `_normalize_yield` in `fetcher.py` — because Yahoo is inconsistent about
  fraction vs percentage.
- **Free-data caveat**: `yfinance` is an unofficial scraper with no SLA and
  typically ~15-min-delayed retail quotes. Fine for research, learning, and
  paper trading; not for production real-money execution.
- **Alerts fire once** — after triggering, an alert is marked `triggered` and
  won't re-fire. Users create a new one if they want to be alerted again.

---

## How it fits with the web app

```
Yahoo Finance ──► worker (this) ──► Supabase ──► web app (Next.js)
                      │                              ▲
                      └── checks alerts, emails ─────┘ (users set alerts in-app)
```

The worker never talks to the web app directly — everything flows through the
shared Supabase database. That clean separation means you can run, restart, or
redeploy either one independently.
