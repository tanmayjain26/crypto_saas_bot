import config
from indicators.supertrend_tv import supertrend_tv
import pandas as pd
import numpy as np


def apply_strategy(df, atr_period, multiplier, changeATR):

    # =========================
    # Supertrend
    # =========================
    df = supertrend_tv(df, atr_period, multiplier, changeATR)

    # =========================
    # EMA200 (15m trend)
    # =========================
    df["ema200"] = df["close"].ewm(span=200).mean()

    # =========================
    # 1H Trend Filter
    # =========================
    df["ema800"] = df["close"].ewm(span=800).mean()

    # =========================
    # ATR volatility filter
    # =========================
    df["atr_mean"] = df["atr"].rolling(50).mean()

    # =========================
    # ADX calculation
    # =========================
    high = df["high"]
    low = df["low"]
    close = df["close"]

    plus_dm = high.diff()
    minus_dm = low.diff() * -1

    plus_dm[plus_dm < 0] = 0
    minus_dm[minus_dm < 0] = 0

    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())

    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    atr = tr.rolling(config.ADX_PERIOD).mean()

    plus_di = 100 * (plus_dm.rolling(config.ADX_PERIOD).mean() / atr)
    minus_di = 100 * (minus_dm.rolling(config.ADX_PERIOD).mean() / atr)

    dx = (abs(plus_di - minus_di) / (plus_di + minus_di)) * 100
    df["adx"] = dx.rolling(config.ADX_PERIOD).mean()

    # =========================
    # Signal column
    # =========================
    df["signal"] = 0

    # =========================
    # Base Supertrend signals with momentum filter
    # =========================
    buy_signal = df["buy"] & ((df["close"] - df["up"]) > 0.5 * df["atr"])
    sell_signal = df["sell"] & ((df["dn"] - df["close"]) > 0.5 * df["atr"])

    # =========================
    # EMA200 trend filter
    # =========================
    buy_signal = buy_signal & (df["close"] > df["ema200"])
    sell_signal = sell_signal & (df["close"] < df["ema200"])

    # =========================
    # 1H trend confirmation
    # =========================
    buy_signal = buy_signal & (df["close"] > df["ema800"])
    sell_signal = sell_signal & (df["close"] < df["ema800"])

    # =========================
    # ATR volatility filter
    # =========================
    volatility = df["atr"] / df["atr_mean"]

    buy_signal = buy_signal & (volatility > 1) & (volatility < 2.5)
    sell_signal = sell_signal & (volatility > 1) & (volatility < 2.5)

    # =========================
    # ADX trend filter
    # =========================
    adx_trend = df["adx"].diff()

    buy_signal = buy_signal & (df["adx"] > config.ADX_THRESHOLD) & (adx_trend > 0)
    sell_signal = sell_signal & (df["adx"] > config.ADX_THRESHOLD) & (adx_trend > 0)

    # =========================
    # Assign signals
    # =========================
    df.loc[buy_signal, "signal"] = 1
    df.loc[sell_signal, "signal"] = -1

    # =========================
    # Export signals for TradingView
    # =========================
    df["long_signal"] = buy_signal
    df["short_signal"] = sell_signal

    export_df = df[["timestamp", "close", "long_signal", "short_signal"]]

    export_df.to_csv("tv_signals.csv", index=False)

    return df