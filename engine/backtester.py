import numpy as np


def run_backtest(df, initial_balance, position_size, fee):

    balance = initial_balance
    position = 0
    entry_price = 0
    current_size = 0

    equity = []
    trades = []

    # Cooldown system
    cooldown = 0
    COOLDOWN_BARS = 3

    for i in range(len(df)):

        price = df["close"].iloc[i]
        up = df["up"].iloc[i]
        dn = df["dn"].iloc[i]

        # reduce cooldown
        if cooldown > 0:
            cooldown -= 1

        # =========================
        # Supertrend trailing stop
        # =========================

        if position == 1 and price < up:

            pnl = (price - entry_price) * current_size
            pnl -= price * current_size * fee

            balance += pnl
            trades.append(pnl)

            if pnl < 0:
                cooldown = COOLDOWN_BARS

            position = 0
            entry_price = 0
            current_size = 0


        elif position == -1 and price > dn:

            pnl = (entry_price - price) * current_size
            pnl -= price * current_size * fee

            balance += pnl
            trades.append(pnl)

            if pnl < 0:
                cooldown = COOLDOWN_BARS

            position = 0
            entry_price = 0
            current_size = 0


        # =========================
        # BUY SIGNAL
        # =========================

        if df["signal"].iloc[i] == 1 and cooldown == 0:

            if position == -1:

                pnl = (entry_price - price) * current_size
                pnl -= price * current_size * fee

                balance += pnl
                trades.append(pnl)

                if pnl < 0:
                    cooldown = COOLDOWN_BARS

            atr = df["atr"].iloc[i]
            atr_mean = df["atr_mean"].iloc[i]

            # volatility scaling
            volatility_scale = atr_mean / atr
            volatility_scale = max(0.5, min(volatility_scale, 1.5))

            # drawdown scaling
            peak_balance = max(equity) if equity else balance
            drawdown = (peak_balance - balance) / peak_balance
            drawdown_scale = max(0.4, 1 - drawdown)

            # final risk
            risk_per_trade = balance * 0.01 * volatility_scale * drawdown_scale

            current_size = risk_per_trade / (2 * atr)

            entry_price = price
            position = 1


        # =========================
        # SELL SIGNAL
        # =========================

        elif df["signal"].iloc[i] == -1 and cooldown == 0:

            if position == 1:

                pnl = (price - entry_price) * current_size
                pnl -= price * current_size * fee

                balance += pnl
                trades.append(pnl)

                if pnl < 0:
                    cooldown = COOLDOWN_BARS

            atr = df["atr"].iloc[i]
            atr_mean = df["atr_mean"].iloc[i]

            # volatility scaling
            volatility_scale = atr_mean / atr
            volatility_scale = max(0.5, min(volatility_scale, 1.5))

            # drawdown scaling
            peak_balance = max(equity) if equity else balance
            drawdown = (peak_balance - balance) / peak_balance
            drawdown_scale = max(0.4, 1 - drawdown)

            # final risk
            risk_per_trade = balance * 0.01 * volatility_scale * drawdown_scale

            current_size = risk_per_trade / (2 * atr)

            entry_price = price
            position = -1


        equity.append(balance)

    df = df.copy()
    df["equity"] = equity


    # =========================
    # Performance statistics
    # =========================

    total_trades = len(trades)

    wins = [t for t in trades if t > 0]
    losses = [t for t in trades if t < 0]

    win_rate = (len(wins) / total_trades) * 100 if total_trades else 0

    gross_profit = sum(wins)
    gross_loss = abs(sum(losses))

    profit_factor = gross_profit / gross_loss if gross_loss else 0


    eq = np.array(equity)

    peak = np.maximum.accumulate(eq)
    drawdown = (eq - peak) / peak

    max_dd = drawdown.min() * 100


    returns = np.diff(eq) / eq[:-1]

    sharpe = (returns.mean() / returns.std()) * np.sqrt(365) if returns.std() != 0 else 0


    stats = {
        "Total Trades": total_trades,
        "Win Rate (%)": win_rate,
        "Profit Factor": profit_factor,
        "Max Drawdown (%)": max_dd,
        "Sharpe Ratio": sharpe
    }

    return df, balance, stats