import os
import requests


class Telegram:

    @staticmethod
    def send_telegram_message(payload) -> None:
        # URL to fetch chat id: https://api.telegram.org/bot<bot_token>/getUpdates
        bot_token = os.environ.get('TELEGRAMBOTTOKEN')
        bot_chat_id = os.environ.get('TELEGRAMBOTCHATID')
        try:
            url_req = "https://api.telegram.org/bot"+bot_token + \
                "/sendMessage"+"?chat_id="+bot_chat_id+"&text="+payload.get('message')
            results = requests.get(url_req)
        except Exception as e:
            print('Exception occured in telegram call : %s', str(e))