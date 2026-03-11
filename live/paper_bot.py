import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config

from data.market_data import fetch_ohlcv
from strategies.supertrend_strategy import apply_strategy
from live.paper_account import PaperAccount
from live.logger import log
from live.telegram import send_message


account = PaperAccount(balance=config.INITIAL_BALANCE)


def run():

    for symbol in config.SYMBOLS:

        df = fetch_ohlcv(symbol, config.TIMEFRAME, days=10)

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

        log(f"{symbol} PRICE: {price} | SIGNAL: {signal}")

        # LONG
        if signal == 1 and account.position != 1:

            if account.position == -1:
                account.close_position(price)

            account.open_long(price, size)
            send_message(f"BUY {symbol} at {price}")

        # SHORT
        elif signal == -1 and account.position != -1:

            if account.position == 1:
                account.close_position(price)

            account.open_short(price, size)
            send_message(f"SELL {symbol} at {price}")


if __name__ == "__main__":
    run()