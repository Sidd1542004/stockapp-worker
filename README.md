# StockApp

An all-in-one stock platform for both beginners and pros — covering global
markets (US + India), ETFs, and crypto. Research, paper trade, learn, compete,
and get AI-powered insights. Built entirely on **free-tier** services.

> **Educational paper-trading platform. Not financial advice. It does not
> execute real trades, and market data may be delayed.**

---

## Table of contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [The two projects](#the-two-projects)
- [Tech stack](#tech-stack)
- [Getting started](#getting-started)
- [Environment variables](#environment-variables)
- [Database setup](#database-setup)
- [Running day to day](#running-day-to-day)
- [Deployment](#deployment)
- [Security & privacy](#security--privacy)
- [Common gotchas](#common-gotchas)
- [Roadmap ideas](#roadmap-ideas)

---

## Overview

StockApp is a two-part system:

1. **stockapp-web** — a Next.js web app: the entire user experience (landing
   page, auth, dashboard, screener, trading, learning, AI, and more).
2. **stockapp-worker** — a small Python service that keeps prices fresh and
   sends price-alert emails, running free on GitHub Actions every 30 minutes.

The two never talk directly — they connect only through a shared **Supabase**
database. The worker writes prices; the web app reads them. That clean
separation means you can run, restart, or redeploy either independently.

The whole thing runs on free tiers: Supabase, Vercel, GitHub Actions, Groq
(AI), Finnhub (news), and Resend (email). No paid services required.

---

## Features

**Market data & research**
- Live-ish prices for stocks, ETFs, and crypto (US + Indian markets)
- Stock detail pages with candlestick charts (1M–5Y) and key fundamentals
- Peer comparison table with a search bar to compare against any asset
- Screener — filter by sector, valuation, yield, market cap, momentum
- Natural-language screener — "cheap dividend stocks" → real results (AI)
- Sector heatmap — every sector color-coded by today's move
- Market news feed (Finnhub)

**Paper trading**
- Per-user $100,000 virtual portfolio, tracked in your own database
- Market buy/sell orders that fill instantly at the latest price
- Holdings with live P&L; portfolio analytics (allocation, best/worst)
- Atomic trade execution via a Postgres function (no race conditions)

**Engagement**
- Watchlists with realtime price updates; shareable via public link
- Price alerts — email when a symbol crosses your target
- Leaderboard — ranks paper-trading returns across users (privacy-safe)
- Settings — leaderboard username / opt-out

**Learning & onboarding**
- "Learn" tab: plain-English lessons + a "Discover" panel of preset screens
- Tap-to-learn tooltips on fundamentals
- Dedicated onboarding page after signup, with activity-based progress

**AI (via Groq — free tier)**
- Explain a stock in plain English
- AI-generated pros & cons
- Portfolio risk summary
- Natural-language screener

All AI output carries a clear "not financial advice" disclaimer.

**Landing page**
- Professional dark "market terminal" landing page with a live ticker and a
  live screener preview pulled from real data.

---

## Architecture

```
                    ┌──────────────────────────┐
   Yahoo Finance ──►│   stockapp-worker (Py)   │
                    │  every 30 min via GH      │
                    │  Actions:                 │
                    │   • fetch prices + funda  │
                    │   • write to Supabase     │
                    │   • check alerts, email   │
                    └───────────┬──────────────┘
                                │ writes
                                ▼
                    ┌──────────────────────────┐
                    │        Supabase          │
                    │  Postgres + Auth + RLS    │
                    │  + Realtime               │
                    └───────────┬──────────────┘
                                │ reads
                                ▼
   Users  ◄────────►  ┌──────────────────────────┐  ◄──► Groq (AI)
                      │   stockapp-web (Next.js) │  ◄──► Finnhub (news)
                      │   on Vercel               │
                      └──────────────────────────┘
```

---

## The two projects

| | stockapp-web | stockapp-worker |
|---|---|---|
| **What** | The web app / UI | Data + alerts service |
| **Language** | TypeScript (Next.js) | Python |
| **Runs on** | Vercel | GitHub Actions (cron) |
| **Env vars in** | Vercel settings | GitHub Secrets |
| **Talks to** | Supabase, Groq, Finnhub | Supabase, Yahoo, Resend |

Each project has its own detailed README. This file is the overview.

---

## Tech stack

- **Next.js 16** (App Router) + **TypeScript** + **Tailwind CSS**
- **Supabase** — Postgres, auth, row-level security, realtime
- **TradingView Lightweight Charts v5** — candlestick charts
- **Python 3.11** + **yfinance** — the data worker
- **Groq** — AI (free tier, OpenAI-compatible)
- **Finnhub** — news · **Resend** — alert emails
- **Vercel** (web) + **GitHub Actions** (worker) — hosting, free

---

## Getting started

You need free accounts on: **GitHub**, **Supabase**, **Vercel**, and
(optional but recommended) **Groq**, **Finnhub**, and **Resend**.

### 1. Web app

```bash
cd stockapp-web
npm install
cp .env.local.example .env.local     # fill in your keys (see below)
npm run dev
```

Open http://localhost:3000.

### 2. Worker

```bash
cd stockapp-worker
python -m venv .venv
source .venv/bin/activate             # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                   # fill in your keys
python -m src.main                     # one run: fetch + write + check alerts
```

---

## Environment variables

**Web app** (`stockapp-web/.env.local`, and Vercel project settings):

```
NEXT_PUBLIC_SUPABASE_URL=https://your-project-ref.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-public-key
GROQ_API_KEY=your-groq-key             # AI features
FINNHUB_API_KEY=your-finnhub-key       # market news
```

**Worker** (`stockapp-worker/.env`, and GitHub Secrets):

```
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-secret-key
RESEND_API_KEY=your-resend-key         # optional: alert emails
ALERT_FROM_EMAIL=StockApp <onboarding@resend.dev>
```

If a key is missing, that feature degrades gracefully (AI shows "AI is off",
news shows a note, alerts save without emailing) — nothing crashes.

> ⚠️ The **service role key** bypasses row-level security. Keep it only in the
> worker's `.env` (gitignored) and GitHub Secrets — never in the web app, never
> committed. Never commit any `.env` file.

---

## Database setup

Run these SQL files in the Supabase SQL Editor, in order (all idempotent):

1. `schema.sql` — core tables (stocks, watchlists) + RLS
2. `phase3-migration.sql` — realtime + default watchlist trigger
3. `phase4-migration.sql` — portfolios, positions, orders + trade function
4. `phase5-migration.sql` — fundamental columns for screening
5. `phase6-migration.sql` — onboarding
6. `batchA-migration.sql` — asset_type (ETF/crypto) columns
7. `batchB-migration.sql` — profiles, alerts, sharing, leaderboard
8. `landing-anon-read.sql` — lets the public landing page read live prices

---

## Running day to day

Most of the time you're just working on the web app:

```bash
cd stockapp-web
npm run dev
```

Prices stay fresh automatically — the worker runs in the cloud every 30
minutes. You only run the worker locally to force a refresh or test changes.

| Task | Folder | Command |
|---|---|---|
| Web dev | stockapp-web | `npm run dev` |
| After dep changes | stockapp-web | `npm install` then `npm run dev` |
| Force a price update | stockapp-worker | `.venv\Scripts\python -m src.main` |

---

## Deployment

**Web app → Vercel.** Push `stockapp-web` to GitHub, import it on Vercel, add
all the `.env.local` variables under the project's Environment Variables, and
deploy. Every push to `main` auto-deploys.

**Worker → GitHub Actions.** Push `stockapp-worker` to a **public** repo (for
unlimited Actions minutes), add the secrets under Settings → Secrets → Actions,
and trigger the first run from the Actions tab. It then runs every 30 minutes.

---

## Security & privacy

- **Row-level security** on all user tables — users see only their own
  portfolios, positions, orders, watchlists, and alerts.
- **Leaderboard** exposes only username + return %, via a SECURITY DEFINER
  function. Holdings are never readable by other users.
- **Shared watchlists** return only the list name and symbols — never the
  owner's identity.
- **Public landing page** can read only the `stocks` table (public market
  data); everything else stays private.
- **AI** prompts forbid buy/sell recommendations; every output is disclaimed.
- This is a **paper-trading** app. Real execution would require a licensed
  broker integration and the appropriate financial licenses.

---

## Common gotchas

- **Supabase free tier pauses** after 7 days of no activity. If the app throws
  DB errors after a break, open the Supabase dashboard once to wake it.
- **Turbopack stale cache** — after adding a file you may see a false "module
  not found". Stop the server, delete `.next`
  (`Remove-Item -Recurse -Force .next` in PowerShell), and `npm run dev`.
- **`middleware.ts` deprecation** on Next 16 — rename it to `proxy.ts` (no code
  changes) to silence the warning.
- **Symbols change** — companies get renamed/demerged/delisted. The worker
  skips a failing symbol instead of crashing; update it in `universe.py`.
- **Groq model changes** — if AI calls fail with a model error, update the one
  `MODEL` constant in `src/lib/groq.ts` to a current model from
  https://console.groq.com/docs/models.
- **Vercel env vars** — set them in Vercel; `.env.local` is local only.

---

## Roadmap ideas

Honest, high-value next steps (none require paid services):

- **Expected range / volatility** — "this stock typically moves ±2.4% a day"
  (sound, teaches risk — unlike unreliable price prediction).
- **Technical indicators** (RSI, moving averages) — unlocks crossover/RSI
  screens; the worker would compute and store them from price history.
- **Light/dark toggle**, **limit orders + order history**, **mobile polish**.
- **Custom email domain** for alerts; **re-enable email confirmation** on signup.
- **Error monitoring** (Sentry free tier); **rate limiting** on AI endpoints.
- **Beta launch** to 10–20 real users for feedback before building more.

The single highest-value step is getting it in front of real people — you'll
learn more from that than from any additional feature.

---

## Credits

Built iteratively across six phases plus two feature batches and several
refinements: foundation & auth → market data → charts & watchlists → paper
trading → screener & analytics → learn/news/onboarding → data & discovery
(ETFs, crypto, peers, heatmap) → engagement & AI (leaderboard, sharing, alerts,
Groq) → landing page. All on free-tier infrastructure.
