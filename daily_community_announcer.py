import requests, json, os, time

BOT_TOKEN = "8366083249:AAFGt9Fblt4Ndsyq_o6Ks-yyrhWMhM2bH7w"
SUB_FILE = "/root/rutestrip-bot/subscribers.json"

COMMUNITY_MSG = """🏔️ **Komunitas Pendaki RuteStrip Indonesia!** 🎒

Yuk gabung dan dapatkan update info jalur pendakian, prakiraan cuaca realtime, serta diskusi sesama pendaki di Official Telegram RuteStrip! 📱✨

📢 **Official Channel**: [https://t.me/rutestrip](https://t.me/rutestrip)
🤖 **Bot Interaktif**: [@rutestrip_bot](https://t.me/rutestrip_bot)
🌐 **Web Chat App**: [https://airutestrip.web.id](https://airutestrip.web.id)

Dapatkan info kuota simaksi, update kondisi gunung, dan tips keselamatan outdoor setiap hari!

Salam Lestari & Salam Pendaki! 🏕️🥾"""

def broadcast_community():
    if not os.path.exists(SUB_FILE):
        print("No subscribers file found.")
        return
    
    try:
        with open(SUB_FILE, "r") as f:
            subs = json.load(f)
    except Exception as e:
        print("Error reading subscribers:", e)
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    success_count = 0
    fail_count = 0

    print(f"📢 Starting daily community announcement broadcast to {len(subs)} subscribers...")
    for cid_str, info in subs.items():
        chat_id = info.get("chat_id")
        user_name = info.get("user_name", "")
        if not chat_id:
            continue
        
        payload = {
            "chat_id": chat_id,
            "text": COMMUNITY_MSG,
            "parse_mode": "Markdown",
            "disable_web_page_preview": False
        }
        try:
            r = requests.post(url, json=payload, timeout=10)
            if r.status_code == 200:
                success_count += 1
                print(f"  ✅ Sent to {user_name} ({chat_id})")
            else:
                fail_count += 1
                print(f"  ❌ Failed for {user_name} ({chat_id}): {r.status_code} {r.text}")
        except Exception as e:
            fail_count += 1
            print(f"  ❌ Error sending to {chat_id}:", e)
        
        time.sleep(0.1)

    print(f"🏁 Community broadcast finished: {success_count} succeeded, {fail_count} failed.")

if __name__ == "__main__":
    broadcast_community()
