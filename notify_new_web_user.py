#!/usr/bin/env python3
import json
import os

WEB_USERS_DB = "/home/ubuntu/rutestrip-bot/users_auth.json"
SEEN_WEB_USERS_FILE = "/home/ubuntu/rutestrip-bot/seen_web_users.json"

def check_new_web_users():
    if not os.path.exists(WEB_USERS_DB):
        return

    try:
        with open(WEB_USERS_DB, "r") as f:
            current_users = json.load(f)
    except Exception:
        return

    seen_ids = set()
    if os.path.exists(SEEN_WEB_USERS_FILE):
        try:
            with open(SEEN_WEB_USERS_FILE, "r") as f:
                seen_ids = set(json.load(f))
        except Exception:
            pass

    new_web_users = []
    for uid, info in current_users.items():
        if uid not in seen_ids:
            new_web_users.append({
                "id": uid,
                "username": info.get("username", "N/A"),
                "email": info.get("email", "N/A"),
                "full_name": info.get("full_name", "N/A"),
                "created_at": info.get("created_at", "N/A")
            })
            seen_ids.add(uid)

    try:
        with open(SEEN_WEB_USERS_FILE, "w") as f:
            json.dump(list(seen_ids), f, indent=2)
    except Exception:
        pass

    if new_web_users:
        lines = []
        for u in new_web_users:
            lines.append(
                f"• **Username:** `{u['username']}`\n"
                f"  👤 **Nama:** {u['full_name']}\n"
                f"  📧 **Email:** `{u['email']}`\n"
                f"  ⏰ **Waktu Registrasi:** `{u['created_at']}`"
            )
        
        msg = (
            f"🌐 **NOTIFIKASI PENGGUNA BARU WEBCHAT AI!** 🤖✨\n\n"
            f"Ada **{len(new_web_users)} pengguna baru** yang baru saja mendaftar di WebChat AI (`airutestrip.web.id`):\n\n"
            + "\n\n".join(lines) +
            f"\n\n📊 Total Pengguna Terdaftar WebChat AI: **{len(current_users)}**"
        )
        print(msg)

if __name__ == "__main__":
    check_and_initialize = not os.path.exists(SEEN_WEB_USERS_FILE)
    if check_and_initialize:
        if os.path.exists(WEB_USERS_DB):
            try:
                users = json.load(open(WEB_USERS_DB))
                with open(SEEN_WEB_USERS_FILE, "w") as f:
                    json.dump(list(users.keys()), f, indent=2)
            except Exception:
                pass
    else:
        check_new_web_users()
