# StockApp — Phase 2: Market Data Worker

A tiny Python service that fetches stock prices from Yahoo Finance and
writes them to the same Supabase database your Phase 1 Next.js app reads
from. As soon as this worker is running, your dashboard will show live
prices with **zero changes** to the Next.js code.

**Deploys free via GitHub Actions — no server needed.**

---

## What Phase 2 adds

- 60-stock universe (30 US + 30 India, easily extensible in `src/universe.py`)
- Batch fetching via `yfinance` — one HTTP request per run for the entire universe
- Upsert into your existing `stocks` table (both INSERT new rows and UPDATE existing)
- Runs every 30 minutes via GitHub Actions (free, no infra)
- Also runnable locally in loop mode for development

## What Phase 2 does NOT add

- Historical price data (Phase 3 — needed for charts)
- Real-time streaming (Phase 3 uses Supabase Realtime to push updates to the UI)
- Fundamentals (P/E, market cap, dividends) — Phase 3
- News — Phase 6

---

## Prerequisites

- **Python 3.11+** (`python --version` to check)
- A Supabase project from Phase 1 with the `stocks` table already created
- A GitHub account (for the free scheduler)

---

## Local setup — test it in 5 minutes

### 1. Install

```bash
cd stockapp-worker
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Get your service role key

In the Supabase dashboard: **Project Settings → API**.
You'll see two keys — `anon` (which your Next.js app uses) and
`service_role` (which the worker uses). Copy the **service_role** one.

> ⚠️ The service role key bypasses row-level security. Treat it like a
> password. It goes in `.env` (gitignored) and GitHub Secrets — never
> commit it, never put it in your Next.js code, never share it.

### 3. Configure environment

```bash
cp .env.example .env
```

Edit `.env`:

```
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOi...(the service_role key)
```

### 4. Run it once

```bash
python -m src.main
```

You should see output like:

```
INFO worker: Starting run: 60 symbols in universe
INFO src.fetcher: Downloading quotes for 60 symbols
[*********************100%***********************]  60 of 60 completed
INFO src.fetcher: Successfully fetched 60 / 60 quotes
INFO src.db: Upserting 60 rows to Supabase
INFO worker: Run complete: wrote 60 rows
```

Now open your Next.js app dashboard — you should see 60 stocks with
fresh prices instead of the 10 hardcoded ones. 🎉

### 5. (Optional) Run in a loop

For development, you can keep it running locally:

```bash
python -m src.main --loop --interval 900   # every 15 minutes
```

But for production, GitHub Actions is the right answer — no need to leave
your laptop on.

---

## Deploy via GitHub Actions (production)

This is the free scheduler. Every 30 min, GitHub spins up an Ubuntu VM,
installs deps, runs the worker, and shuts down. You pay nothing.

### 1. Push the worker to GitHub

```bash
cd stockapp-worker
git init
git add .
git commit -m "Phase 2: market data worker"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/stockapp-worker.git
git push -u origin main
```

> **Recommendation:** make this repo **public**. Public repos get
> UNLIMITED GitHub Actions minutes. Private repos are limited to 2,000
> minutes/month on the free plan, and at every 30 min that's tight.

### 2. Add the two secrets

In the GitHub repo: **Settings → Secrets and variables → Actions →
New repository secret**.

Add two secrets with these exact names:

| Name                          | Value                                    |
|-------------------------------|------------------------------------------|
| `SUPABASE_URL`                | Your Supabase project URL                |
| `SUPABASE_SERVICE_ROLE_KEY`   | The `service_role` key (NOT the anon)    |

### 3. Trigger the first run

Go to **Actions → Update stock quotes → Run workflow → Run**.
Watch the logs — after ~1 minute you should see 60 stocks upserted.

From then on, it runs itself every 30 minutes.

---

## Adding more stocks to the universe

Edit `src/universe.py` and append entries. Symbol conventions:

| Exchange   | Format             | Example         |
|------------|--------------------|-----------------|
| US NASDAQ  | plain ticker       | `AAPL`, `NVDA`  |
| US NYSE    | plain ticker       | `JPM`, `V`      |
| India NSE  | `.NS` suffix       | `RELIANCE.NS`   |
| India BSE  | `.BO` suffix       | `RELIANCE.BO`   |
| UK LSE     | `.L` suffix        | `HSBA.L`        |
| Japan TSE  | `.T` suffix        | `7203.T`        |

Commit, push, and the next scheduled run will pick them up automatically.

---

## Troubleshooting

**"Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY"** — your `.env`
isn't being read. Make sure you're running from the `stockapp-worker`
directory and `.env` exists there.

**"insert or update on table 'stocks' violates row-level security"** — you
used the anon key instead of the service_role key. Get the service_role
key from Supabase (it's the second, "secret" one).

**"YFRateLimitError"** — Yahoo has temporarily rate-limited your IP. Wait
15 minutes and try again. If it persists, reduce the universe size or
run less frequently.

**GitHub Actions cron isn't firing on time** — GitHub's cron is
best-effort and often delays free-tier jobs by 5–15 minutes during peak
load. This is normal. If it stops entirely, check for a GitHub Actions
outage.

---

## Testing checklist for Phase 2

- [ ] `python -m src.main` runs locally without errors
- [ ] After running, Next.js dashboard shows 60 stocks (not 10)
- [ ] Stock prices in the dashboard match roughly what Yahoo Finance shows
- [ ] `updated_at` in the `stocks` table is a recent timestamp
- [ ] GitHub Actions workflow completes successfully when triggered manually
- [ ] Workflow runs automatically on the next 30-min mark

All six passing = Phase 2 complete. Phase 3 will add historical price
charts, a Supabase Realtime subscription for live UI updates, and the
watchlist add/remove UI.

---

## Alternative deployment options (if you outgrow GitHub Actions)

- **Railway** — $5/month free credit, always-on background worker
- **Fly.io** — free tier with a small always-on VM
- **Supabase Edge Functions + pg_cron** — everything in one place; steeper learning curve
- **Render Cron Jobs** — free tier available with limitations

For MVP scale (up to a few thousand users), GitHub Actions is more than
enough.
