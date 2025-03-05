import os
import requests as req
from dotenv import load_dotenv

from db import VegapunkDB


load_dotenv("/Users/akshay.dadwal/work/vegapunk6969_bot/.env")


def broadcast_message(message):
    db_conn = VegapunkDB()

    token = os.getenv("BOT_TOKEN")

    users = db_conn.get_users()

    for user in users:
        url = f"https://api.telegram.org/bot{token}/sendMessage"

        payload = {
            "chat_id": user[2],
            "text": f"Hi @{user[1]},\n{message}",
        }

        req.post(url, json=payload)
    
    return
