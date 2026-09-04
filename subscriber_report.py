#!/usr/bin/env python3
import json
import os

SUBSCRIBERS_PATH = "/root/rutestrip-bot/subscribers.json"

def generate_report():
    if not os.path.exists(SUBSCRIBERS_PATH):
        return "Basis data pengguna belum tersedia."
    
    with open(SUBSCRIBERS_PATH, "r") as f:
        data = json.load(f)
    
    users = []
    groups = []
    
    for key, val in data.items():
        chat_id = str(val.get("chat_id", key))
        name = val.get("user_name", "Tanpa Nama")
        if not name:
            name = "Grup Komunitas"
            
        if chat_id.startswith("-"):
            groups.append(f"• ID: {chat_id} | Nama: {name}")
        else:
            username_str = f"@{name}" if not name.startswith("@") and name != "Tanpa Nama" else name
            users.append(f"• ID: {chat_id} | Username: {username_str}")
    
    report = (
        "📊 LAPORAN RUTIN PENGGUNA RUTESTRIP BOT 🏔️\n\n"
        f"👥 Total Pelanggan Aktif: {len(data)}\n"
        f"👤 Pengguna Personal (DM): {len(users)}\n"
        f"💬 Grup Telegram: {len(groups)}\n\n"
        "Rincian Pengguna Personal:\n" + "\n".join(users) + "\n\n"
        "Rincian Grup Telegram:\n" + "\n".join(groups) + "\n\n"
        "Laporan ini diperbarui secara otomatis."
    )
    return report

if __name__ == "__main__":
    print(generate_report())
