#!/usr/bin/env python3
import os
import json
import urllib.request
import urllib.parse
import time

def send_telegram_message(bot_token, chat_id, text):
    api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    req = urllib.request.Request(
        api_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 200
    except Exception as e:
        return False

def broadcast_to_subscribers(message, targets="all"):
    # targets: 'all', 'groups', 'users'
    env_vars = {}
    env_path = "/home/ubuntu/.hermes/.env"
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    env_vars[k.strip()] = v.strip().strip('"\'')

    bot_token = env_vars.get("TELEGRAM_BOT_TOKEN")
    if not bot_token:
        return

    sub_file = "/home/ubuntu/rutestrip-bot/subscribers.json"
    if not os.path.exists(sub_file):
        return

    try:
        with open(sub_file, "r") as f:
            subs = json.load(f)
    except Exception:
        return

    for chat_id_str in subs.keys():
        is_group = chat_id_str.startswith("-")
        if targets == "groups" and not is_group:
            continue
        if targets == "users" and is_group:
            continue
            
        send_telegram_message(bot_token, chat_id_str, message)
        time.sleep(0.05)
