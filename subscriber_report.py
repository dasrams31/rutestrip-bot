#!/usr/bin/env python3
import json
import os

SUBSCRIBERS_PATH = "/root/rutestrip-bot/subscribers.json"
WEB_USERS_PATH = "/root/rutestrip-bot/users_auth.json"

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
    
    # 2. Ambil statistik & rincian pengguna WebChat AI
    web_users = []
    if os.path.exists(WEB_USERS_PATH):
        try:
            with open(WEB_USERS_PATH, "r") as f:
                wdata = json.load(f)
                for uid, winfo in wdata.items():
                    w_uname = winfo.get("username", "Tanpa Username")
                    w_email = winfo.get("email", "Tanpa Email")
                    w_name = winfo.get("full_name", w_uname)
                    web_users.append(f"• User: @{w_uname} ({w_name}) | Email: {w_email}")
        except Exception:
            pass

    report = (
        "📊 LAPORAN RUTIN PENGGUNA RUTESTRIP BOT & WEBCHAT 🏔️\n\n"
        f"👥 Total Pelanggan Bot Aktif: {len(data)}\n"
        f"👤 Pengguna Personal Telegram (DM): {len(users)}\n"
        f"💬 Grup Telegram: {len(groups)}\n\n"
        "Rincian Pengguna Personal Telegram:\n" + "\n".join(users) + "\n\n"
        "Rincian Grup Telegram:\n" + "\n".join(groups) + "\n\n"
        "========================================\n\n"
        f"🌐 LAPORAN PENGGUNA WEBCHAT AI (airutestrip.web.id)\n"
        f"👥 Total Akun WebChat Terdaftar: {len(web_users)}\n\n"
        "Rincian Akun WebChat AI:\n" + ("\n".join(web_users) if web_users else "• Belum ada pengguna terdaftar.") + "\n\n"
        "Laporan ini diperbarui secara otomatis."
    )
    return report

if __name__ == "__main__":
    print(generate_report())
