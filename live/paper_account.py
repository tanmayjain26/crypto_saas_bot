import json
import os

STATE_FILE = "live/account_state.json"


class PaperAccount:

    def __init__(self, balance):
        self.balance = balance
        self.position = 0
        self.entry_price = None
        self.size = 0

        self.load()


    def load(self):

        if os.path.exists(STATE_FILE):

            with open(STATE_FILE, "r") as f:

                data = json.load(f)

                self.balance = data["balance"]
                self.position = data["position"]
                self.entry_price = data["entry_price"]
                self.size = data["size"]


    def save(self):

        data = {
            "balance": self.balance,
            "position": self.position,
            "entry_price": self.entry_price,
            "size": self.size
        }

        with open(STATE_FILE, "w") as f:
            json.dump(data, f)


    def open_long(self, price, size):

        self.position = 1
        self.entry_price = price
        self.size = size

        self.save()


    def open_short(self, price, size):

        self.position = -1
        self.entry_price = price
        self.size = size

        self.save()


    def close_position(self, price):

        if self.position == 1:

            pnl = (price - self.entry_price) * self.size

        elif self.position == -1:

            pnl = (self.entry_price - price) * self.size

        else:
            pnl = 0

        self.balance += pnl

        self.position = 0
        self.entry_price = None
        self.size = 0

        self.save()