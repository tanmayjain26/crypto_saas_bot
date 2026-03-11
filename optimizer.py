import itertools
import pandas as pd
import config

from data.market_data import fetch_ohlcv
from strategies.supertrend_strategy import apply_strategy
from engine.backtester import run_backtest


print("Fetching market data...")

df_base = fetch_ohlcv(config.SYMBOL, config.TIMEFRAME, config.DAYS)

print("Data loaded:", len(df_base), "candles")


# =============================
# Parameter ranges
# =============================

ATR_PERIODS = [7,10,12,14,18]
MULTIPLIERS = [1.5,2,2.5,3]
BREAKOUTS = [0.5,1,1.5,2]
ADX_THRESHOLDS = [5,8,10,12]


results = []

total = len(ATR_PERIODS) * len(MULTIPLIERS) * len(BREAKOUTS) * len(ADX_THRESHOLDS)

print("Total strategies to test:", total)


count = 0

for atr_period, multiplier, breakout, adx in itertools.product(
    ATR_PERIODS,
    MULTIPLIERS,
    BREAKOUTS,
    ADX_THRESHOLDS
):

    count += 1
    print(f"Running {count}/{total}")

    df = df_base.copy()

    # temporarily override config values
    config.BREAKOUT_ATR_MULT = breakout
    config.ADX_THRESHOLD = adx

    df = apply_strategy(
        df,
        atr_period,
        multiplier,
        config.CHANGE_ATR
    )

    df, final_balance, stats = run_backtest(
        df,
        config.INITIAL_BALANCE,
        config.POSITION_SIZE,
        config.TAKER_FEE
    )

    results.append({
        "ATR": atr_period,
        "Multiplier": multiplier,
        "Breakout": breakout,
        "ADX": adx,
        "FinalBalance": final_balance,
        "ProfitFactor": stats["Profit Factor"],
        "Sharpe": stats["Sharpe Ratio"],
        "Trades": stats["Total Trades"],
        "WinRate": stats["Win Rate (%)"]
    })


results_df = pd.DataFrame(results)


# =============================
# Top 10 by Final Balance
# =============================

print("\n==============================")
print("TOP 10 BY FINAL BALANCE")
print("==============================")

print(
    results_df.sort_values("FinalBalance", ascending=False)
    .head(10)
    .to_string(index=False)
)


# =============================
# Top 10 by Profit Factor
# =============================

print("\n==============================")
print("TOP 10 BY PROFIT FACTOR")
print("==============================")

print(
    results_df.sort_values("ProfitFactor", ascending=False)
    .head(10)
    .to_string(index=False)
)


# =============================
# Top 10 by Sharpe Ratio
# =============================

print("\n==============================")
print("TOP 10 BY SHARPE RATIO")
print("==============================")

print(
    results_df.sort_values("Sharpe", ascending=False)
    .head(10)
    .to_string(index=False)
)