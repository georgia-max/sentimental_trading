"""Fetch historical auction (open/close) prices from the Alpaca Market Data API.

Hits GET /v2/stocks/auctions and handles pagination via next_page_token.
Credentials are read from .env (ALPACA_PAPER_API_KEY / ALPACA_PAPER_SECRET_KEY).
"""

import os

import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("ALPACA_PAPER_API_KEY")
SECRET_KEY = os.getenv("ALPACA_PAPER_SECRET_KEY")

URL = "https://data.alpaca.markets/v2/stocks/auctions"

HEADERS = {
    "accept": "application/json",
    "APCA-API-KEY-ID": API_KEY,
    "APCA-API-SECRET-KEY": SECRET_KEY,
}

PARAMS = {
    "symbols": "TSLA",
    "start": "2024-01-03T01:02:03.123456789Z",
    "end": "2026-01-04T01:02:03.123456789Z",
    "limit": 1000,
    "feed": "sip",
    "sort": "asc",
}


def get_auctions(params):
    """Yield each page of auction data, following next_page_token to the end."""
    params = dict(params)
    while True:
        resp = requests.get(URL, headers=HEADERS, params=params, timeout=30)
        resp.raise_for_status()
        payload = resp.json()
        yield payload

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

    total = 0
    for page in get_auctions(PARAMS):
        auctions = page.get("auctions", {})
        for symbol, days in auctions.items():
            for day in days:
                opens = day.get("o", [])
                closes = day.get("c", [])
                print(
                    f"{symbol} {day.get('d')}: "
                    f"{len(opens)} opening / {len(closes)} closing auction(s)"
                )
                total += 1

    print(f"\nDone. {total} auction day(s) retrieved.")


if __name__ == "__main__":
    main()
