#!/usr/bin/env python3
import sys
import os
import json
import time

LOG_FILE = "/home/ubuntu/rutestrip-bot/broadcast_messages.json"

def clean_old_broadcasts():
    if not os.path.exists(LOG_FILE):
        return
    try:
        with open(LOG_FILE, "r") as f:
            data = json.load(f)
    except Exception:
        return

    now = time.time()
    six_hours = 6 * 3600
    updated_data = []

    for item in data:
        msg_id = item.get("message_id")
        chat_id = item.get("chat_id")
        timestamp = item.get("timestamp", 0)
        is_tips = item.get("is_tips", False)

        # Selalu simpan jika jenisnya adalah tips / edukasi survival
        if is_tips:
            updated_data.append(item)
            continue

        # Jika sudah melewati 6 jam, tandai hapus (logika delete dipanggil jika bot memiliki akses bot token direct)
        if now - timestamp < six_hours:
            updated_data.append(item)

    with open(LOG_FILE, "w") as f:
        json.dump(updated_data, f, indent=2)

if __name__ == "__main__":
    clean_old_broadcasts()
