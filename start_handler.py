#!/usr/bin/env python3
import json
import os
import datetime

SUBSCRIBERS_PATH = "/home/ubuntu/rutestrip-bot/subscribers.json"
ADMIN_USER_ID = "606533609"

ADMIN_START_MSG = """Halo Mas Rama! 🏔️👑 (Mode Admin)

Selamat datang kembali di Control Panel RuteStrip Bot.
Sistem beroperasi normal dan seluruh layanan aktif:

🛡️ Status Keamanan:
• Akses Terminal & VPS: AKTIF (Khusus Akun Anda)
• Guardrail Pengguna Umum: AKTIF (Isolasi Penuh 100%)
• Auto-Push GitLab: AKTIF (Realtime)
• Total Cron Job: 17 Jadwal Aktif

Silakan ketik perintah konfigurasi, eksekusi shell, atau pertanyaan pendakian kapan saja di chat ini! 🚀"""

USER_START_MSG = """Halo Sobat Pendaki! 👋🏔️✨
Selamat datang di RuteStrip Bot — Asisten Pintar Pendakian Gunung di Indonesia!

Saya siap membantumu merencanakan pendakian yang aman, nyaman, dan berkesan:

🧭 Rekomendasi Rute Trek:
Ketik: "rekomendasi gunung untuk pemula" atau "jalur tektok di jawa tengah"

⛅ Prakiraan Cuaca Live:
Ketik: "cuaca merbabu", "cuaca prau", "cuaca semeru"

🎒 Panduan Logistik & Survival:
Ketik: "logistik untuk 3 orang 2 hari", "penanganan hipotermia"

🗺️ Peta Trek & Navigasi:
Ketik: "peta merbabu", "track gpx sindoro"

🌐 Platform & Komunitas Resmi:
• Website: https://rutestrip.web.id
• WebChat AI: https://airutestrip.web.id
• Grup Komunitas: @rutestrip_group
• Channel Berita: @rutestrip

Salam Lestari & Selamat Menjelajah! 🏕️🥾"""

def register_subscriber_if_new(chat_id, user_name):
    try:
        data = {}
        if os.path.exists(SUBSCRIBERS_PATH):
            with open(SUBSCRIBERS_PATH, "r") as f:
                data = json.load(f)
        
        chat_id_str = str(chat_id)
        if chat_id_str not in data:
            data[chat_id_str] = {
                "chat_id": int(chat_id) if str(chat_id).lstrip("-").isdigit() else chat_id,
                "user_name": user_name or "",
                "subscribed_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            }
            with open(SUBSCRIBERS_PATH, "w") as f:
                json.dump(data, f, indent=2)
            
            # Copy juga ke /home/ubuntu/subscribers.json jika ada
            alt_path = "/home/ubuntu/subscribers.json"
            if os.path.exists(alt_path):
                with open(alt_path, "w") as f:
                    json.dump(data, f, indent=2)
    except Exception as e:
        print(f"[Subscriber Register Error] {e}")

def get_start_reply(source) -> str:
    user_id = str(getattr(source, "user_id", "") or "")
    chat_id = str(getattr(source, "chat_id", "") or "")
    user_name = str(getattr(source, "user_name", "") or "")

    if user_id == ADMIN_USER_ID:
        return ADMIN_START_MSG
    else:
        if chat_id:
            register_subscriber_if_new(chat_id, user_name)
        return USER_START_MSG

if __name__ == "__main__":
    class DummySource:
        user_id = "1786049024"
        chat_id = "1786049024"
        user_name = "Misaka"
    print(get_start_reply(DummySource()))
