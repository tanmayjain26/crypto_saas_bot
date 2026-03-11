from live.logger import log


class PaperAccount:

    def __init__(self, balance=1000):

        self.balance = balance
        self.position = 0
        self.entry_price = None
        self.size = 0

    def open_long(self, price, size):

        self.position = 1
        self.entry_price = price
        self.size = size

        log(f"OPEN LONG @ {price}")

    def open_short(self, price, size):

        self.position = -1
        self.entry_price = price
        self.size = size

        log(f"OPEN SHORT @ {price}")

    def close_position(self, price):

        if self.position == 1:

            pnl = (price - self.entry_price) * self.size

        elif self.position == -1:

            pnl = (self.entry_price - price) * self.size

        else:
            return

        self.balance += pnl

        log(f"CLOSE @ {price} | PnL: {pnl:.2f}")
        log(f"BALANCE: {self.balance:.2f}")

        self.position = 0
        self.entry_price = None
        self.size = 0