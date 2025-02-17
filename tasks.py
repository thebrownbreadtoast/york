import os
import requests as req
from dotenv import load_dotenv

from db import VegapunkDB


load_dotenv()


def handle_updates():
    db_conn = VegapunkDB()

    token = os.getenv("BOT_TOKEN")

    if not token:
        return

    url = f"https://api.telegram.org/bot{token}/getUpdates"

    response = req.get(url)

    if response.status_code != 200:
        return

    updates = response.json()["result"]

    for update in updates:
        username = update["message"]["chat"]["username"]
        chat_id = update["message"]["chat"]["id"]

        command = update["message"]["text"]

        match command:
            case "/notify":
                db_conn.add_user(username, chat_id)
            case "/stop":
                db_conn.remove_user(username, chat_id)
            case _:
                pass
    
    return

def check_for_new_chapter():
    import ipdb;ipdb.set_trace()
    db_conn = VegapunkDB()

    token = os.getenv("BOT_TOKEN")

    last_chapter_id = db_conn.get_last_chapter()[1]

    latest_chapter_api = f"https://api.api-onepiece.com/v2/chapters/en/{last_chapter_id + 1}"
    latest_chapter_link = f"https://w12.read-onepiece.net/manga/one-piece-chapter-{last_chapter_id + 1}/"

    response = req.get(latest_chapter_api)

    if response.status_code != 200:
        return
    
    chapter_response = response.json()

    chapter_id = chapter_response["id"]
    chapter_title = chapter_response["title"]

    existing_users = db_conn.get_users()

    for user in existing_users:
        msg = f"Hi @{user[1]}! A new chapter has been released: {chapter_title}.\n\nRead it here: {latest_chapter_link}"

        req.post(f"https://api.telegram.org/bot{token}/sendMessage", json={"chat_id": user[2], "text": msg})
    
    return
