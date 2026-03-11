import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import config

from data.market_data import fetch_ohlcv
from strategies.supertrend_strategy import apply_strategy
from engine.backtester import run_backtest


portfolio_balance = 0

for symbol in config.SYMBOLS:

    print("\n==============================")
    print("Running backtest for:", symbol)
    print("==============================")

    df = fetch_ohlcv(symbol, config.TIMEFRAME, config.DAYS)

    df = apply_strategy(
        df,
        config.ATR_PERIOD,
        config.MULTIPLIER,
        config.CHANGE_ATR
    )

    df, final_balance, stats = run_backtest(
        df,
        config.INITIAL_BALANCE,
        config.POSITION_SIZE,
        config.TAKER_FEE
    )

    portfolio_balance += final_balance

    print("Final Balance:", final_balance)
    print("\n------ Strategy Statistics ------")

    for k, v in stats.items():
        print(k, ":", v)


    # -------- Price + Supertrend chart --------
    plt.figure(figsize=(14,7))

    plt.plot(df["timestamp"], df["close"], color="black", label="Price")

    uptrend = df[df["trend"] == 1]
    downtrend = df[df["trend"] == -1]

    plt.plot(uptrend["timestamp"], uptrend["up"], color="green", label="Supertrend Up")
    plt.plot(downtrend["timestamp"], downtrend["dn"], color="red", label="Supertrend Down")

    plt.scatter(df[df["buy"]]["timestamp"], df[df["buy"]]["close"], color="green", marker="^")
    plt.scatter(df[df["sell"]]["timestamp"], df[df["sell"]]["close"], color="red", marker="v")

    plt.legend()
    plt.grid()

    plt.savefig(f"{symbol.replace('/','_')}_supertrend_chart.png")


    # -------- Equity curve --------
    plt.figure(figsize=(14,7))

    plt.plot(df["timestamp"], df["equity"], label="Balance")

    plt.title(f"Equity Curve - {symbol}")
    plt.xlabel("Time")
    plt.ylabel("Balance")

    plt.legend()
    plt.grid()

    plt.savefig(f"{symbol.replace('/','_')}_equity_curve.png")


print("\n==============================")
print("PORTFOLIO TOTAL BALANCE")
print("==============================")
print(portfolio_balance)