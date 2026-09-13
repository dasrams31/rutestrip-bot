#!/usr/bin/env python3
import json
import os
import subprocess
import sys

sys.path.append("/home/ubuntu/rutestrip-bot")
from telegram_broadcast_helper import broadcast_to_subscribers

SUB_FILE = "/home/ubuntu/rutestrip-bot/subscribers.json"

def send_portal_news_to_users():
    res = subprocess.run(["python3", "/home/ubuntu/rutestrip-bot/portal_news_scraper.py"], capture_output=True, text=True)
    news_text = res.stdout.strip()

    if not news_text:
        return

    # Kirim ke seluruh pengguna & grup
    broadcast_to_subscribers(news_text, targets="all")
    print(news_text)

if __name__ == "__main__":
    send_portal_news_to_users()
