import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config

from data.market_data import fetch_ohlcv
from strategies.supertrend_strategy import apply_strategy
from live.paper_account import PaperAccount
from live.logger import log


account = PaperAccount(balance=config.INITIAL_BALANCE)


def run():

    df = fetch_ohlcv(
        config.SYMBOLS,
        config.TIMEFRAME,
        10
    )

    df = apply_strategy(
        df,
        config.ATR_PERIOD,
        config.MULTIPLIER,
        config.CHANGE_ATR
    )

    last = df.iloc[-1]

    price = last["close"]
    signal = last["signal"]
    atr = last["atr"]

    risk = account.balance * 0.01
    size = risk / (2 * atr)

    log(f"PRICE: {price} | SIGNAL: {signal}")

    if signal == 1 and account.position <= 0:

        if account.position == -1:
            account.close_position(price)

        account.open_long(price, size)

    elif signal == -1 and account.position >= 0:

        if account.position == 1:
            account.close_position(price)

        account.open_short(price, size)


if __name__ == "__main__":
    run()