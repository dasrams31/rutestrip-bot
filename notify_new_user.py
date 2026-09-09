#!/usr/bin/env python3
import json
import os
import sys

# Tambahkan path hermes-agent agar impor gateway selalu aman
sys.path.append("/home/ubuntu/.hermes/hermes-agent")

SUB_FILE = "/home/ubuntu/rutestrip-bot/subscribers.json"
SEEN_FILE = "/home/ubuntu/rutestrip-bot/seen_subscribers.json"

def auto_approve_pairing(platform, user_id, user_name=""):
    try:
        from gateway.pairing import PairingStore
        ps = PairingStore()
        ps._approve_user(platform, str(user_id), user_name)
    except Exception:
        pass

def check_new_subscribers():
    if not os.path.exists(SUB_FILE):
        return

    try:
        with open(SUB_FILE, "r") as f:
            current_subs = json.load(f)
    except Exception:
        return

    seen_ids = set()
    if os.path.exists(SEEN_FILE):
        try:
            with open(SEEN_FILE, "r") as f:
                seen_ids = set(json.load(f))
        except Exception:
            pass

    new_users = []
    for chat_id_str, info in current_subs.items():
        if chat_id_str not in seen_ids:
            # Otomatis approve user baru di PairingStore
            user_name = info.get("user_name", "Tanpa Username")
            if not chat_id_str.startswith("-"):
                auto_approve_pairing("telegram", chat_id_str, user_name)
                
                username_display = f"@{user_name}" if user_name and not user_name.startswith("@") else user_name
                reg_time = info.get("subscribed_at", "N/A")
                new_users.append({
                    "id": chat_id_str,
                    "username": username_display,
                    "time": reg_time
                })
            seen_ids.add(chat_id_str)

    # Simpan state seen_ids yang baru
    try:
        with open(SEEN_FILE, "w") as f:
            json.dump(list(seen_ids), f, indent=2)
    except Exception:
        pass

    # Jika ada pengguna baru, cetak notifikasi (dikirim ke DM Admin)
    if new_users:
        lines = []
        for u in new_users:
            lines.append(f"• **Username:** {u['username']} (ID: `{u['id']}`)\n  ⏰ **Waktu:** `{u['time']}`")
        
        msg = (
            f"🎉 **NOTIFIKASI PENGGUNA BARU RUTESTRIP BOT!** 🎒\n\n"
            f"Ada **{len(new_users)} pengguna baru** yang baru saja bergabung & menggunakan bot:\n\n"
            + "\n\n".join(lines) +
            f"\n\n📊 Total Pengguna Terdaftar Saat Ini: **{len(current_subs)}**"
        )
        print(msg)

if __name__ == "__main__":
    check_new_subscribers()
