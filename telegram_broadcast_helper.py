#!/usr/bin/env python3
import os
import json
import urllib.request
import urllib.parse
import time

OFFICIAL_CHANNEL = "@rutestrip"

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

def broadcast_to_subscribers(message, targets="channel_and_users"):
    """
    targets options:
    - 'channel': hanya ke Official Channel (@rutestrip)
    - 'users': hanya ke DM seluruh pengguna personal
    - 'channel_and_users' (default): ke Official Channel (@rutestrip) + DM pengguna personal (TIDAK kirim ke grup agar tidak dobel karena Telegram otomatis meneruskan post channel ke grup)
    """
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

    send_targets = set()

    # Selalu sertakan Official Channel jika target memuat channel
    if targets in ["channel", "channel_and_users", "all"]:
        send_targets.add(OFFICIAL_CHANNEL)

    for chat_id_str in subs.keys():
        cid = str(chat_id_str).strip()
        
        # Filter ketat: ABAIKAN grup, service telegram 777000, dan bot
        if cid.startswith("-") or cid in ["@rutestrip_group", "777000", "Telegram"]:
            continue

        if cid == OFFICIAL_CHANNEL:
            if targets in ["channel", "channel_and_users", "all"]:
                send_targets.add(cid)
            continue

        # User personal DM
        if targets in ["users", "channel_and_users", "all"]:
            send_targets.add(cid)

    success_count = 0
    fail_count = 0

    for target_id in send_targets:
        ok = send_telegram_message(bot_token, target_id, message)
        if ok:
            success_count += 1
        else:
            fail_count += 1
        time.sleep(0.05)  # Rate limit safety

    return success_count, fail_count

if __name__ == "__main__":
    import sys
    msg = "Test broadcast system." if len(sys.argv) < 2 else sys.argv[1]
    s, f = broadcast_to_subscribers(msg, targets="channel_and_users")
    print(f"Broadcast selesai: {s} sukses, {f} gagal.")
