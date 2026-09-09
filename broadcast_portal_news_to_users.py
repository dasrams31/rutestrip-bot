#!/usr/bin/env python3
import json
import os
import subprocess

SUB_FILE = "/home/ubuntu/rutestrip-bot/subscribers.json"

def send_portal_news_to_users():
    res = subprocess.run(["python3", "/home/ubuntu/rutestrip-bot/portal_news_scraper.py"], capture_output=True, text=True)
    news_text = res.stdout.strip()

    if not os.path.exists(SUB_FILE):
        return

    with open(SUB_FILE, "r") as f:
        subs = json.load(f)

    for chat_id_str, info in subs.items():
        if not chat_id_str.startswith("-"):
            print(news_text)

if __name__ == "__main__":
    send_portal_news_to_users()
