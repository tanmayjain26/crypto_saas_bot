from datetime import datetime


LOG_FILE = "trade_log.txt"


def log(message):

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    line = f"{timestamp} | {message}"

    print(line)

    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")