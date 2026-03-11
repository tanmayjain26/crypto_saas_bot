import requests
import config


def send_message(msg):
    url = f"https://api.telegram.org/bot{config.TELEGRAM_TOKEN}/sendMessage"

    data = {
        "chat_id": config.TELEGRAM_CHAT_ID,
        "text": msg
    }

    requests.post(url, data=data)