"""
The universe of assets the worker tracks.

Batch A update: added an "asset_type" field ("stock", "etf", or "crypto") and
expanded coverage with popular ETFs and major cryptocurrencies.

Symbols follow Yahoo Finance conventions:
  - US stocks/ETFs: plain ticker (e.g. "AAPL", "SPY")
  - NSE India: ".NS" suffix (e.g. "RELIANCE.NS")
  - Crypto: "-USD" suffix (e.g. "BTC-USD")

To add more, append to STOCKS with the right asset_type. Crypto and ETFs are
handled gracefully everywhere (no P/E, no sector shown where not applicable).
"""

STOCKS = [
    # ─── US TOP 30 BY MARKET CAP ───────────────────────────────────────────
    {"symbol": "AAPL",  "name": "Apple Inc.",              "exchange": "NASDAQ", "sector": "Technology", "asset_type": "stock"},
    {"symbol": "MSFT",  "name": "Microsoft Corporation",   "exchange": "NASDAQ", "sector": "Technology", "asset_type": "stock"},
    {"symbol": "GOOGL", "name": "Alphabet Inc.",           "exchange": "NASDAQ", "sector": "Technology", "asset_type": "stock"},
    {"symbol": "AMZN",  "name": "Amazon.com Inc.",         "exchange": "NASDAQ", "sector": "Consumer Discretionary", "asset_type": "stock"},
    {"symbol": "NVDA",  "name": "NVIDIA Corporation",      "exchange": "NASDAQ", "sector": "Technology", "asset_type": "stock"},
    {"symbol": "META",  "name": "Meta Platforms Inc.",     "exchange": "NASDAQ", "sector": "Communication Services", "asset_type": "stock"},
    {"symbol": "TSLA",  "name": "Tesla Inc.",              "exchange": "NASDAQ", "sector": "Consumer Discretionary", "asset_type": "stock"},
    {"symbol": "BRK-B", "name": "Berkshire Hathaway",      "exchange": "NYSE",   "sector": "Financials", "asset_type": "stock"},
    {"symbol": "JPM",   "name": "JPMorgan Chase & Co.",    "exchange": "NYSE",   "sector": "Financials", "asset_type": "stock"},
    {"symbol": "V",     "name": "Visa Inc.",               "exchange": "NYSE",   "sector": "Financials", "asset_type": "stock"},
    {"symbol": "UNH",   "name": "UnitedHealth Group",      "exchange": "NYSE",   "sector": "Health Care", "asset_type": "stock"},
    {"symbol": "XOM",   "name": "Exxon Mobil Corporation", "exchange": "NYSE",   "sector": "Energy", "asset_type": "stock"},
    {"symbol": "JNJ",   "name": "Johnson & Johnson",       "exchange": "NYSE",   "sector": "Health Care", "asset_type": "stock"},
    {"symbol": "WMT",   "name": "Walmart Inc.",            "exchange": "NYSE",   "sector": "Consumer Staples", "asset_type": "stock"},
    {"symbol": "MA",    "name": "Mastercard Incorporated", "exchange": "NYSE",   "sector": "Financials", "asset_type": "stock"},
    {"symbol": "PG",    "name": "Procter & Gamble Co.",    "exchange": "NYSE",   "sector": "Consumer Staples", "asset_type": "stock"},
    {"symbol": "HD",    "name": "The Home Depot Inc.",     "exchange": "NYSE",   "sector": "Consumer Discretionary", "asset_type": "stock"},
    {"symbol": "LLY",   "name": "Eli Lilly and Company",   "exchange": "NYSE",   "sector": "Health Care", "asset_type": "stock"},
    {"symbol": "CVX",   "name": "Chevron Corporation",     "exchange": "NYSE",   "sector": "Energy", "asset_type": "stock"},
    {"symbol": "AVGO",  "name": "Broadcom Inc.",           "exchange": "NASDAQ", "sector": "Technology", "asset_type": "stock"},
    {"symbol": "ABBV",  "name": "AbbVie Inc.",             "exchange": "NYSE",   "sector": "Health Care", "asset_type": "stock"},
    {"symbol": "KO",    "name": "The Coca-Cola Company",   "exchange": "NYSE",   "sector": "Consumer Staples", "asset_type": "stock"},
    {"symbol": "PEP",   "name": "PepsiCo Inc.",            "exchange": "NASDAQ", "sector": "Consumer Staples", "asset_type": "stock"},
    {"symbol": "MRK",   "name": "Merck & Co. Inc.",        "exchange": "NYSE",   "sector": "Health Care", "asset_type": "stock"},
    {"symbol": "COST",  "name": "Costco Wholesale Corp.",  "exchange": "NASDAQ", "sector": "Consumer Staples", "asset_type": "stock"},
    {"symbol": "BAC",   "name": "Bank of America Corp.",   "exchange": "NYSE",   "sector": "Financials", "asset_type": "stock"},
    {"symbol": "ADBE",  "name": "Adobe Inc.",              "exchange": "NASDAQ", "sector": "Technology", "asset_type": "stock"},
    {"symbol": "CSCO",  "name": "Cisco Systems Inc.",      "exchange": "NASDAQ", "sector": "Technology", "asset_type": "stock"},
    {"symbol": "TMO",   "name": "Thermo Fisher Scientific","exchange": "NYSE",   "sector": "Health Care", "asset_type": "stock"},
    {"symbol": "MCD",   "name": "McDonald's Corporation",  "exchange": "NYSE",   "sector": "Consumer Discretionary", "asset_type": "stock"},

    # ─── INDIA TOP 30 (NIFTY 50 CONSTITUENTS) ──────────────────────────────
    {"symbol": "RELIANCE.NS",    "name": "Reliance Industries Ltd.",       "exchange": "NSE", "sector": "Energy", "asset_type": "stock"},
    {"symbol": "TCS.NS",         "name": "Tata Consultancy Services",      "exchange": "NSE", "sector": "Technology", "asset_type": "stock"},
    {"symbol": "HDFCBANK.NS",    "name": "HDFC Bank Limited",              "exchange": "NSE", "sector": "Financials", "asset_type": "stock"},
    {"symbol": "INFY.NS",        "name": "Infosys Limited",                "exchange": "NSE", "sector": "Technology", "asset_type": "stock"},
    {"symbol": "ICICIBANK.NS",   "name": "ICICI Bank Limited",             "exchange": "NSE", "sector": "Financials", "asset_type": "stock"},
    {"symbol": "HINDUNILVR.NS",  "name": "Hindustan Unilever Ltd.",        "exchange": "NSE", "sector": "Consumer Staples", "asset_type": "stock"},
    {"symbol": "ITC.NS",         "name": "ITC Limited",                    "exchange": "NSE", "sector": "Consumer Staples", "asset_type": "stock"},
    {"symbol": "SBIN.NS",        "name": "State Bank of India",            "exchange": "NSE", "sector": "Financials", "asset_type": "stock"},
    {"symbol": "BHARTIARTL.NS",  "name": "Bharti Airtel Limited",          "exchange": "NSE", "sector": "Communication Services", "asset_type": "stock"},
    {"symbol": "KOTAKBANK.NS",   "name": "Kotak Mahindra Bank",            "exchange": "NSE", "sector": "Financials", "asset_type": "stock"},
    {"symbol": "LT.NS",          "name": "Larsen & Toubro Ltd.",           "exchange": "NSE", "sector": "Industrials", "asset_type": "stock"},
    {"symbol": "AXISBANK.NS",    "name": "Axis Bank Limited",              "exchange": "NSE", "sector": "Financials", "asset_type": "stock"},
    {"symbol": "ASIANPAINT.NS",  "name": "Asian Paints Limited",           "exchange": "NSE", "sector": "Materials", "asset_type": "stock"},
    {"symbol": "MARUTI.NS",      "name": "Maruti Suzuki India Ltd.",       "exchange": "NSE", "sector": "Consumer Discretionary", "asset_type": "stock"},
    {"symbol": "BAJFINANCE.NS",  "name": "Bajaj Finance Limited",          "exchange": "NSE", "sector": "Financials", "asset_type": "stock"},
    {"symbol": "HCLTECH.NS",     "name": "HCL Technologies Ltd.",          "exchange": "NSE", "sector": "Technology", "asset_type": "stock"},
    {"symbol": "WIPRO.NS",       "name": "Wipro Limited",                  "exchange": "NSE", "sector": "Technology", "asset_type": "stock"},
    {"symbol": "ULTRACEMCO.NS",  "name": "UltraTech Cement Ltd.",          "exchange": "NSE", "sector": "Materials", "asset_type": "stock"},
    {"symbol": "SUNPHARMA.NS",   "name": "Sun Pharmaceutical Industries",  "exchange": "NSE", "sector": "Health Care", "asset_type": "stock"},
    {"symbol": "TITAN.NS",       "name": "Titan Company Limited",          "exchange": "NSE", "sector": "Consumer Discretionary", "asset_type": "stock"},
    {"symbol": "ONGC.NS",        "name": "Oil & Natural Gas Corp.",        "exchange": "NSE", "sector": "Energy", "asset_type": "stock"},
    {"symbol": "NTPC.NS",        "name": "NTPC Limited",                   "exchange": "NSE", "sector": "Utilities", "asset_type": "stock"},
    {"symbol": "ADANIENT.NS",    "name": "Adani Enterprises Limited",      "exchange": "NSE", "sector": "Materials", "asset_type": "stock"},
    {"symbol": "POWERGRID.NS",   "name": "Power Grid Corporation",         "exchange": "NSE", "sector": "Utilities", "asset_type": "stock"},
    {"symbol": "NESTLEIND.NS",   "name": "Nestle India Limited",           "exchange": "NSE", "sector": "Consumer Staples", "asset_type": "stock"},
    {"symbol": "TECHM.NS",       "name": "Tech Mahindra Limited",          "exchange": "NSE", "sector": "Technology", "asset_type": "stock"},
    {"symbol": "M&M.NS",         "name": "Mahindra & Mahindra Ltd.",       "exchange": "NSE", "sector": "Consumer Discretionary", "asset_type": "stock"},
    {"symbol": "JSWSTEEL.NS",    "name": "JSW Steel Limited",              "exchange": "NSE", "sector": "Materials", "asset_type": "stock"},
    {"symbol": "TATASTEEL.NS",   "name": "Tata Steel Limited",             "exchange": "NSE", "sector": "Materials", "asset_type": "stock"},
    {"symbol": "TMPV.NS",        "name": "Tata Motors Passenger Vehicles", "exchange": "NSE", "sector": "Consumer Discretionary", "asset_type": "stock"},

    # ─── POPULAR US ETFs ───────────────────────────────────────────────────
    {"symbol": "SPY",  "name": "SPDR S&P 500 ETF Trust",         "exchange": "NYSE ARCA", "sector": "ETF", "asset_type": "etf"},
    {"symbol": "VOO",  "name": "Vanguard S&P 500 ETF",           "exchange": "NYSE ARCA", "sector": "ETF", "asset_type": "etf"},
    {"symbol": "QQQ",  "name": "Invesco QQQ Trust",              "exchange": "NASDAQ",    "sector": "ETF", "asset_type": "etf"},
    {"symbol": "VTI",  "name": "Vanguard Total Stock Market ETF","exchange": "NYSE ARCA", "sector": "ETF", "asset_type": "etf"},
    {"symbol": "IWM",  "name": "iShares Russell 2000 ETF",       "exchange": "NYSE ARCA", "sector": "ETF", "asset_type": "etf"},
    {"symbol": "DIA",  "name": "SPDR Dow Jones Industrial ETF",  "exchange": "NYSE ARCA", "sector": "ETF", "asset_type": "etf"},
    {"symbol": "GLD",  "name": "SPDR Gold Shares",               "exchange": "NYSE ARCA", "sector": "ETF", "asset_type": "etf"},
    {"symbol": "VEA",  "name": "Vanguard FTSE Developed Mkts ETF","exchange": "NYSE ARCA", "sector": "ETF", "asset_type": "etf"},

    # ─── MAJOR CRYPTOCURRENCIES ────────────────────────────────────────────
    {"symbol": "BTC-USD",  "name": "Bitcoin",       "exchange": "CRYPTO", "sector": "Crypto", "asset_type": "crypto"},
    {"symbol": "ETH-USD",  "name": "Ethereum",      "exchange": "CRYPTO", "sector": "Crypto", "asset_type": "crypto"},
    {"symbol": "SOL-USD",  "name": "Solana",        "exchange": "CRYPTO", "sector": "Crypto", "asset_type": "crypto"},
    {"symbol": "BNB-USD",  "name": "BNB",           "exchange": "CRYPTO", "sector": "Crypto", "asset_type": "crypto"},
    {"symbol": "XRP-USD",  "name": "XRP",           "exchange": "CRYPTO", "sector": "Crypto", "asset_type": "crypto"},
    {"symbol": "ADA-USD",  "name": "Cardano",       "exchange": "CRYPTO", "sector": "Crypto", "asset_type": "crypto"},
    {"symbol": "DOGE-USD", "name": "Dogecoin",      "exchange": "CRYPTO", "sector": "Crypto", "asset_type": "crypto"},
    {"symbol": "AVAX-USD", "name": "Avalanche",     "exchange": "CRYPTO", "sector": "Crypto", "asset_type": "crypto"},
]

# Just the symbols, for convenience
SYMBOLS = [s["symbol"] for s in STOCKS]

# Lookup by symbol
BY_SYMBOL = {s["symbol"]: s for s in STOCKS}
