#!/Users/akshay.dadwal/work/vegapunk6969_bot/env/bin/python

import logging
import os
import requests as req
from bs4 import BeautifulSoup

from datetime import datetime, timezone
from dotenv import load_dotenv

from db import VegapunkDB


load_dotenv("/Users/akshay.dadwal/work/vegapunk6969_bot/.env")


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def handle_updates():
    logger.info("Processing Telegram bot events...")

    db_conn = VegapunkDB()

    offset = db_conn.get_offset()[1]

    token = os.getenv("BOT_TOKEN")

    if not token:
        return

    url = f"https://api.telegram.org/bot{token}/getUpdates"

    response = req.get(url)

    if response.status_code != 200:
        logger.error("Failed to fetch bot events from Telegram.")

        return

    updates = response.json()["result"]

    for update in updates:
        timestamp = update["message"]["date"]

        if offset > timestamp:
            logger.warning(f"Skipping old event | {update}")

            continue

        try:
            username = update["message"]["chat"]["username"]
            chat_id = update["message"]["chat"]["id"]

            command = update["message"]["text"]
        except KeyError:
            continue

        match command:
            case "/notify":
                db_conn.add_user(username, chat_id)

                logger.info(f"User added to notification list. | {update}")
            case "/stop":
                db_conn.remove_user(username, chat_id)

                logger.info(f"User removed from notification list. | {update}")
            case _:
                logger.warning(f"Unknown command event. | {update}")

                pass
    
    db_conn.add_or_update_offset()

    logger.info(f"Processed new Telegram bot events and updated offset_timestamp to {offset}.")

    return

def check_for_new_chapter():
    logger.info("Checking for new chapter...")

    db_conn = VegapunkDB()

    token = os.getenv("BOT_TOKEN")

    last_chapter_id = db_conn.get_last_chapter()[1]

    latest_chapter_link = f"https://read-onepiece.net/manga/one-piece-chapter-{last_chapter_id + 1}/"

    response = req.get(latest_chapter_link)

    if response.status_code != 200:
        logger.info("No new chapter found.")

        return

    soup = BeautifulSoup(response.content, features="html.parser")

    total_pages = len(soup.find("div", class_="entry-content").find("center").find_all("img"))

    if (total_pages < 5):
	# Adding `> 5` as a safe-check, because sometimes publisher adds some random placeholder images.
        logger.info(f"Chapter {last_chapter_id + 1} not published yet.")

        return

    existing_users = db_conn.get_users()

    for user in existing_users:
        msg = f"Hi @{user[1]}! A new chapter has been released.\nRead it here: {latest_chapter_link}"

        req.post(f"https://api.telegram.org/bot{token}/sendMessage", json={"chat_id": user[2], "text": msg})
    
    db_conn.add_chapter(last_chapter_id + 1, f"Chapter {last_chapter_id + 1}")

    logger.info("Notified all users about new chapter and updated last_chapter_id.")
    
    return


if __name__ == "__main__":
    handle_updates()
    check_for_new_chapter()
