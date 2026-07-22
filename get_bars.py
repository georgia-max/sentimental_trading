"""Fetch historical OHLCV bars for TSLA from the Alpaca Market Data API.

Hits GET /v2/stocks/{symbol}/bars and follows next_page_token to page through
the full range. Credentials are read from .env — never hardcode them.
"""

import os

import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("ALPACA_PAPER_API_KEY")
SECRET_KEY = os.getenv("ALPACA_PAPER_SECRET_KEY")

SYMBOL = "TSLA"
URL = f"https://data.alpaca.markets/v2/stocks/{SYMBOL}/bars"

HEADERS = {
    "accept": "application/json",
    "APCA-API-KEY-ID": API_KEY,
    "APCA-API-SECRET-KEY": SECRET_KEY,
}

PARAMS = {
    "timeframe": "12Hour",
    "start": "2024-01-03T01:02:03.123456789Z",
    "end": "2026-01-04T01:02:03.123456789Z",
    "limit": 1000,
    "adjustment": "raw",
    "feed": "sip",
    "sort": "asc",
}


def get_bars(params):
    """Yield each bar dict, following next_page_token across all pages."""
    params = dict(params)
    while True:
        resp = requests.get(URL, headers=HEADERS, params=params, timeout=30)
        resp.raise_for_status()
        payload = resp.json()

        for bar in payload.get("bars", []):
            yield bar

        token = payload.get("next_page_token")
        if not token:
            break
        params["page_token"] = token


def main():
    if not API_KEY or not SECRET_KEY:
        raise SystemExit(
            "Missing credentials: set ALPACA_PAPER_API_KEY and "
            "ALPACA_PAPER_SECRET_KEY in your .env file."
        )

    count = 0
    for bar in get_bars(PARAMS):
        print(
            f"{bar['t']}  O:{bar['o']:>10.2f}  H:{bar['h']:>10.2f}  "
            f"L:{bar['l']:>10.2f}  C:{bar['c']:>10.2f}  V:{bar['v']:>12,}"
        )
        count += 1

    print(f"\nDone. {count} bar(s) retrieved for {SYMBOL}.")


if __name__ == "__main__":
    main()
