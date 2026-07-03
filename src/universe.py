"""
The universe of stocks the worker tracks.

Symbols follow Yahoo Finance conventions:
  - US stocks: plain ticker (e.g. "AAPL")
  - NSE India: ".NS" suffix (e.g. "RELIANCE.NS")
  - BSE India: ".BO" suffix (add later if needed)

To add more stocks, just append to STOCKS. The worker will pick them up
on the next run.
"""

STOCKS = [
    # ─── US TOP 30 BY MARKET CAP ───────────────────────────────────────────
    {"symbol": "AAPL",  "name": "Apple Inc.",              "exchange": "NASDAQ", "sector": "Technology"},
    {"symbol": "MSFT",  "name": "Microsoft Corporation",   "exchange": "NASDAQ", "sector": "Technology"},
    {"symbol": "GOOGL", "name": "Alphabet Inc.",           "exchange": "NASDAQ", "sector": "Technology"},
    {"symbol": "AMZN",  "name": "Amazon.com Inc.",         "exchange": "NASDAQ", "sector": "Consumer Discretionary"},
    {"symbol": "NVDA",  "name": "NVIDIA Corporation",      "exchange": "NASDAQ", "sector": "Technology"},
    {"symbol": "META",  "name": "Meta Platforms Inc.",     "exchange": "NASDAQ", "sector": "Communication Services"},
    {"symbol": "TSLA",  "name": "Tesla Inc.",              "exchange": "NASDAQ", "sector": "Consumer Discretionary"},
    {"symbol": "BRK-B", "name": "Berkshire Hathaway",      "exchange": "NYSE",   "sector": "Financials"},
    {"symbol": "JPM",   "name": "JPMorgan Chase & Co.",    "exchange": "NYSE",   "sector": "Financials"},
    {"symbol": "V",     "name": "Visa Inc.",               "exchange": "NYSE",   "sector": "Financials"},
    {"symbol": "UNH",   "name": "UnitedHealth Group",      "exchange": "NYSE",   "sector": "Health Care"},
    {"symbol": "XOM",   "name": "Exxon Mobil Corporation", "exchange": "NYSE",   "sector": "Energy"},
    {"symbol": "JNJ",   "name": "Johnson & Johnson",       "exchange": "NYSE",   "sector": "Health Care"},
    {"symbol": "WMT",   "name": "Walmart Inc.",            "exchange": "NYSE",   "sector": "Consumer Staples"},
    {"symbol": "MA",    "name": "Mastercard Incorporated", "exchange": "NYSE",   "sector": "Financials"},
    {"symbol": "PG",    "name": "Procter & Gamble Co.",    "exchange": "NYSE",   "sector": "Consumer Staples"},
    {"symbol": "HD",    "name": "The Home Depot Inc.",     "exchange": "NYSE",   "sector": "Consumer Discretionary"},
    {"symbol": "LLY",   "name": "Eli Lilly and Company",   "exchange": "NYSE",   "sector": "Health Care"},
    {"symbol": "CVX",   "name": "Chevron Corporation",     "exchange": "NYSE",   "sector": "Energy"},
    {"symbol": "AVGO",  "name": "Broadcom Inc.",           "exchange": "NASDAQ", "sector": "Technology"},
    {"symbol": "ABBV",  "name": "AbbVie Inc.",             "exchange": "NYSE",   "sector": "Health Care"},
    {"symbol": "KO",    "name": "The Coca-Cola Company",   "exchange": "NYSE",   "sector": "Consumer Staples"},
    {"symbol": "PEP",   "name": "PepsiCo Inc.",            "exchange": "NASDAQ", "sector": "Consumer Staples"},
    {"symbol": "MRK",   "name": "Merck & Co. Inc.",        "exchange": "NYSE",   "sector": "Health Care"},
    {"symbol": "COST",  "name": "Costco Wholesale Corp.",  "exchange": "NASDAQ", "sector": "Consumer Staples"},
    {"symbol": "BAC",   "name": "Bank of America Corp.",   "exchange": "NYSE",   "sector": "Financials"},
    {"symbol": "ADBE",  "name": "Adobe Inc.",              "exchange": "NASDAQ", "sector": "Technology"},
    {"symbol": "CSCO",  "name": "Cisco Systems Inc.",      "exchange": "NASDAQ", "sector": "Technology"},
    {"symbol": "TMO",   "name": "Thermo Fisher Scientific","exchange": "NYSE",   "sector": "Health Care"},
    {"symbol": "MCD",   "name": "McDonald's Corporation",  "exchange": "NYSE",   "sector": "Consumer Discretionary"},

    # ─── INDIA TOP 30 (NIFTY 50 CONSTITUENTS) ──────────────────────────────
    {"symbol": "RELIANCE.NS",    "name": "Reliance Industries Ltd.",       "exchange": "NSE", "sector": "Energy"},
    {"symbol": "TCS.NS",         "name": "Tata Consultancy Services",      "exchange": "NSE", "sector": "Technology"},
    {"symbol": "HDFCBANK.NS",    "name": "HDFC Bank Limited",              "exchange": "NSE", "sector": "Financials"},
    {"symbol": "INFY.NS",        "name": "Infosys Limited",                "exchange": "NSE", "sector": "Technology"},
    {"symbol": "ICICIBANK.NS",   "name": "ICICI Bank Limited",             "exchange": "NSE", "sector": "Financials"},
    {"symbol": "HINDUNILVR.NS",  "name": "Hindustan Unilever Ltd.",        "exchange": "NSE", "sector": "Consumer Staples"},
    {"symbol": "ITC.NS",         "name": "ITC Limited",                    "exchange": "NSE", "sector": "Consumer Staples"},
    {"symbol": "SBIN.NS",        "name": "State Bank of India",            "exchange": "NSE", "sector": "Financials"},
    {"symbol": "BHARTIARTL.NS",  "name": "Bharti Airtel Limited",          "exchange": "NSE", "sector": "Communication Services"},
    {"symbol": "KOTAKBANK.NS",   "name": "Kotak Mahindra Bank",            "exchange": "NSE", "sector": "Financials"},
    {"symbol": "LT.NS",          "name": "Larsen & Toubro Ltd.",           "exchange": "NSE", "sector": "Industrials"},
    {"symbol": "AXISBANK.NS",    "name": "Axis Bank Limited",              "exchange": "NSE", "sector": "Financials"},
    {"symbol": "ASIANPAINT.NS",  "name": "Asian Paints Limited",           "exchange": "NSE", "sector": "Materials"},
    {"symbol": "MARUTI.NS",      "name": "Maruti Suzuki India Ltd.",       "exchange": "NSE", "sector": "Consumer Discretionary"},
    {"symbol": "BAJFINANCE.NS",  "name": "Bajaj Finance Limited",          "exchange": "NSE", "sector": "Financials"},
    {"symbol": "HCLTECH.NS",     "name": "HCL Technologies Ltd.",          "exchange": "NSE", "sector": "Technology"},
    {"symbol": "WIPRO.NS",       "name": "Wipro Limited",                  "exchange": "NSE", "sector": "Technology"},
    {"symbol": "ULTRACEMCO.NS",  "name": "UltraTech Cement Ltd.",          "exchange": "NSE", "sector": "Materials"},
    {"symbol": "SUNPHARMA.NS",   "name": "Sun Pharmaceutical Industries",  "exchange": "NSE", "sector": "Health Care"},
    {"symbol": "TITAN.NS",       "name": "Titan Company Limited",          "exchange": "NSE", "sector": "Consumer Discretionary"},
    {"symbol": "ONGC.NS",        "name": "Oil & Natural Gas Corp.",        "exchange": "NSE", "sector": "Energy"},
    {"symbol": "NTPC.NS",        "name": "NTPC Limited",                   "exchange": "NSE", "sector": "Utilities"},
    {"symbol": "ADANIENT.NS",    "name": "Adani Enterprises Limited",      "exchange": "NSE", "sector": "Materials"},
    {"symbol": "POWERGRID.NS",   "name": "Power Grid Corporation",         "exchange": "NSE", "sector": "Utilities"},
    {"symbol": "NESTLEIND.NS",   "name": "Nestle India Limited",           "exchange": "NSE", "sector": "Consumer Staples"},
    {"symbol": "TMPV.NS",        "name": "Tata Motors Passenger Vehicles Ltd.", "exchange": "NSE", "sector": "Consumer Discretionary"},
    {"symbol": "TMCV.NS",        "name": "Tata Motors Ltd. (Commercial Vehicles)", "exchange": "NSE", "sector": "Industrials"},    {"symbol": "TECHM.NS",       "name": "Tech Mahindra Limited",          "exchange": "NSE", "sector": "Technology"},
    {"symbol": "M&M.NS",         "name": "Mahindra & Mahindra Ltd.",       "exchange": "NSE", "sector": "Consumer Discretionary"},
    {"symbol": "JSWSTEEL.NS",    "name": "JSW Steel Limited",              "exchange": "NSE", "sector": "Materials"},
    {"symbol": "TATASTEEL.NS",   "name": "Tata Steel Limited",             "exchange": "NSE", "sector": "Materials"},
]

# Just the symbols, for convenience
SYMBOLS = [s["symbol"] for s in STOCKS]

# Lookup by symbol
BY_SYMBOL = {s["symbol"]: s for s in STOCKS}
