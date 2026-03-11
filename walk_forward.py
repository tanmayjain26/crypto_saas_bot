import pandas as pd
import config

from data.market_data import fetch_ohlcv
from strategies.supertrend_strategy import apply_strategy
from engine.backtester import run_backtest


CANDLES_PER_DAY = 96

TRAIN_DAYS = 270
TEST_DAYS = 90

TRAIN_SIZE = TRAIN_DAYS * CANDLES_PER_DAY
TEST_SIZE = TEST_DAYS * CANDLES_PER_DAY


def walk_forward():

    # Load market data
    df = fetch_ohlcv(
        config.SYMBOL,
        config.TIMEFRAME,
        config.DAYS
    )

    # Apply strategy indicators
    df = apply_strategy(
        df,
        config.ATR_PERIOD,
        config.MULTIPLIER,
        config.CHANGE_ATR
    )

    results = []

    start = 0

    while start + TRAIN_SIZE + TEST_SIZE < len(df):
        train = df.iloc[start:start + TRAIN_SIZE]
        test = df.iloc[start + TRAIN_SIZE:start + TRAIN_SIZE + TEST_SIZE]

        test_df, final_balance, stats = run_backtest(
            test.copy(),
            config.INITIAL_BALANCE,
            config.POSITION_SIZE,
            config.TAKER_FEE
        )

        result = {
            "Period Start": test["timestamp"].iloc[0],
            "Period End": test["timestamp"].iloc[-1],
            "Final Balance": final_balance,
            "Profit Factor": stats["Profit Factor"],
            "Sharpe": stats["Sharpe Ratio"],
            "Trades": stats["Total Trades"]
        }

        results.append(result)

        start += TEST_SIZE

    results_df = pd.DataFrame(results)

    print("\n========== WALK FORWARD RESULTS ==========\n")
    print(results_df)

    print("\nAverage PF:", results_df["Profit Factor"].mean())
    print("Average Sharpe:", results_df["Sharpe"].mean())


if __name__ == "__main__":
    walk_forward()