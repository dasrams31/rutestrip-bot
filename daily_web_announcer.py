import requests, json, os, time

BOT_TOKEN = "8366083249:AAFGt9Fblt4Ndsyq_o6Ks-yyrhWMhM2bH7w"
SUB_FILE = "/root/rutestrip-bot/subscribers.json"

ANNOUNCEMENT_MSG = """🏔️ **Info Pendaki RuteStrip!** 

Tahukah kamu? Selain di Telegram, **RuteStrip AI** juga hadir dalam versi **Web Chat Interaktif**! 🌐✨

Fitur Unggulan versi Web Chat:
🗺️ **Peta Satelit & Topografi Interaktif**
📥 **Download File GPX / KML Jalur Pendakian**
📊 **Perhitungan Naismith & Visualisasi Elevasi**
⚡ **Tampilan Modern & Bebas Hambatan**

Coba sekarang di browser kamu:
👉 **https://airutestrip.web.id**

Selamat beraktivitas dan salam lestari! 🥾🎒"""

def broadcast_web_reminder():
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

    print(f"📢 Starting daily web announcement broadcast to {len(subs)} subscribers...")
    for cid_str, info in subs.items():
        chat_id = info.get("chat_id")
        user_name = info.get("user_name", "")
        if not chat_id:
            continue
        
        payload = {
            "chat_id": chat_id,
            "text": ANNOUNCEMENT_MSG,
            "parse_mode": "Markdown"
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
        
        time.sleep(0.1) # Throttle to respect Telegram rate limits

    print(f"🏁 Broadcast finished: {success_count} succeeded, {fail_count} failed.")

if __name__ == "__main__":
    broadcast_web_reminder()
