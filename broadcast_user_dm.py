#!/usr/bin/env python3
import json
import os
import subprocess

SUBSCRIBERS_PATH = "/root/rutestrip-bot/subscribers.json"
OWNER_ID = "606533609"

def send_to_all_users():
    if not os.path.exists(SUBSCRIBERS_PATH):
        return
    with open(SUBSCRIBERS_PATH, "r") as f:
        subscribers = json.load(f)

    # 1. Panggil laporan cuaca ringkas
    res_cuaca = subprocess.run(["python3", "/root/rutestrip-bot/broadcast_cuaca_group_part1.py"], capture_output=True, text=True)
    cuaca_text = res_cuaca.stdout.strip()

    # 2. Panggil rekomendasi rute harian
    res_rec = subprocess.run(["python3", "/root/rutestrip-bot/broadcast_weekend_getaway.py"], capture_output=True, text=True)
    rec_text = res_rec.stdout.strip()

    message = f"""🌄 **DAILY MOUNTAIN DIGEST (PERSONAL UPDATE)** 🎒

{cuaca_text}

========================================

{rec_text}

---
💡 *Ketik `cuaca <nama_gunung>` atau `rekomendasi <kriteria>` kapan saja di DM untuk cek rute spesifik!*"""

    # Kirim ke seluruh pengguna DM (selain grup)
    for chat_id_str, user_info in subscribers.items():
        if not chat_id_str.startswith("-"):
            print(f"Sending to User DM: {chat_id_str}")
            print(message)
            print("\n--- END OF MESSAGE ---\n")

if __name__ == "__main__":
    send_to_all_users()
