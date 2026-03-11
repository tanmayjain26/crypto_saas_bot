import pandas as pd
import numpy as np


def supertrend_tv(df, period, multiplier, changeATR=True):

    src = (df["high"] + df["low"]) / 2

    tr1 = df["high"] - df["low"]
    tr2 = abs(df["high"] - df["close"].shift())
    tr3 = abs(df["low"] - df["close"].shift())

    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    if changeATR:
        atr = tr.ewm(alpha=1/period, adjust=False).mean()
    else:
        atr = tr.rolling(period).mean()

    up = src - multiplier * atr
    dn = src + multiplier * atr

    trend = [1]
    up_final = [up.iloc[0]]
    dn_final = [dn.iloc[0]]

    for i in range(1, len(df)):

        up1 = up_final[i-1]
        dn1 = dn_final[i-1]

        if df["close"].iloc[i-1] > up1:
            up_val = max(up.iloc[i], up1)
        else:
            up_val = up.iloc[i]

        if df["close"].iloc[i-1] < dn1:
            dn_val = min(dn.iloc[i], dn1)
        else:
            dn_val = dn.iloc[i]

        up_final.append(up_val)
        dn_final.append(dn_val)

        prev_trend = trend[i-1]

        if prev_trend == -1 and df["close"].iloc[i] > dn1:
            trend.append(1)
        elif prev_trend == 1 and df["close"].iloc[i] < up1:
            trend.append(-1)
        else:
            trend.append(prev_trend)

    df["up"] = up_final
    df["dn"] = dn_final
    df["trend"] = trend
    df["atr"] = atr

    df["buy"] = (df["trend"] == 1) & (df["trend"].shift() == -1)
    df["sell"] = (df["trend"] == -1) & (df["trend"].shift() == 1)

    return df