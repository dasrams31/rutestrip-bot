import requests

BOT_TOKEN = "8366083249:AAFGt9Fblt4Ndsyq_o6Ks-yyrhWMhM2bH7w"
ADMIN_CHAT_ID = "606533609"

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

def send_web_reminder():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": ADMIN_CHAT_ID,
        "text": ANNOUNCEMENT_MSG,
        "parse_mode": "Markdown"
    }
    try:
        r = requests.post(url, json=payload, timeout=10)
        if r.status_code == 200:
            print("✅ Daily Web Chat reminder sent successfully via Telegram API!")
        else:
            print(f"Failed to send reminder: {r.status_code} {r.text}")
    except Exception as e:
        print("Error sending daily reminder:", e)

if __name__ == "__main__":
    send_web_reminder()
