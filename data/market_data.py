import ccxt
import pandas as pd
import datetime
import time


def fetch_ohlcv(symbol, timeframe, days):

    exchange = ccxt.delta()

    since = exchange.parse8601(
        (datetime.datetime.utcnow() - datetime.timedelta(days=days)).isoformat()
    )

    all_bars = []

    while True:
        bars = exchange.fetch_ohlcv(symbol, timeframe, since=since, limit=500)

        if len(bars) == 0:
            break

        all_bars += bars
        since = bars[-1][0] + 1

        if len(bars) < 500:
            break

        time.sleep(exchange.rateLimit / 1000)

    df = pd.DataFrame(
        all_bars,
        columns=["timestamp", "open", "high", "low", "close", "volume"]
    )

    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")

    return df