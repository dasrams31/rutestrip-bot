#!/usr/bin/env python3
import os
import json
import urllib.request
import urllib.parse
import time

def send_telegram_message(bot_token, chat_id, text, parse_mode="Markdown"):
    api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode
    }
    req = urllib.request.Request(
        api_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 200
    except Exception:
        # Fallback without parse_mode if markdown parsing fails
        if parse_mode:
            payload.pop("parse_mode", None)
            try:
                req2 = urllib.request.Request(
                    api_url,
                    data=json.dumps(payload).encode("utf-8"),
                    headers={"Content-Type": "application/json"}
                )
                with urllib.request.urlopen(req2, timeout=10) as resp2:
                    return resp2.status == 200
            except Exception:
                return False
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
        return 0, 0

    sub_file = "/home/ubuntu/rutestrip-bot/subscribers.json"
    if not os.path.exists(sub_file):
        return 0, 0

    try:
        with open(sub_file, "r") as f:
            subs = json.load(f)
    except Exception:
        return 0, 0

    success_count = 0
    fail_count = 0
    for chat_id_str in subs.keys():
        is_group_or_channel = str(chat_id_str).startswith("-") or str(chat_id_str).startswith("@")
        
        if targets == "groups" and not is_group_or_channel:
            continue
        if targets == "users" and is_group_or_channel:
            continue
            
        ok = send_telegram_message(bot_token, chat_id_str, message)
        if ok:
            success_count += 1
        else:
            fail_count += 1
        time.sleep(0.04)
        
    return success_count, fail_count
