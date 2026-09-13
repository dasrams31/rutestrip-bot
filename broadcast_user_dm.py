#!/usr/bin/env python3
import json
import os
import subprocess
import sys

sys.path.append("/home/ubuntu/rutestrip-bot")
from telegram_broadcast_helper import broadcast_to_subscribers

SUBSCRIBERS_PATH = "/home/ubuntu/rutestrip-bot/subscribers.json"

def send_to_all_users():
    if not os.path.exists(SUBSCRIBERS_PATH):
        return

    # 1. Panggil laporan cuaca ringkas
    res_cuaca = subprocess.run(["python3", "/home/ubuntu/rutestrip-bot/broadcast_cuaca_group_part1.py"], capture_output=True, text=True)
    cuaca_text = res_cuaca.stdout.strip()

    # 2. Panggil rekomendasi rute harian
    res_rec = subprocess.run(["python3", "/home/ubuntu/rutestrip-bot/broadcast_weekend_getaway.py"], capture_output=True, text=True)
    rec_text = res_rec.stdout.strip()

    # 3. Panggil tips survival & etika pendaki
    res_tips = subprocess.run(["python3", "/home/ubuntu/rutestrip-bot/broadcast_survival_tips.py"], capture_output=True, text=True)
    tips_text = res_tips.stdout.strip()

    message = f"""🌄 DAILY MOUNTAIN DIGEST (UPDATE PERSONAL) 🎒

{cuaca_text}

========================================

{rec_text}

========================================

{tips_text}

---
💡 Ketik `cuaca <nama_gunung>`, `rekomendasi <kriteria>`, atau `survival <topik>` kapan saja di DM!"""

    # Kirim ke seluruh pengguna DM (selain grup)
    broadcast_to_subscribers(message, targets="users")
    print(message)

if __name__ == "__main__":
    send_to_all_users()
