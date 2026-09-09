#!/usr/bin/env python3
import json
import sys
import os

INFO_PATH = os.path.join(os.path.dirname(__file__), "info_rutestrip.json")

def get_info():
    data = {
        "website": "https://rutestrip.web.id",
        "ai_chat": "https://airutestrip.web.id",
        "telegram_group": "@rutestrip_group",
        "telegram_channel": "@rutestrip"
    }
    if os.path.exists(INFO_PATH):
        try:
            with open(INFO_PATH, "r") as f:
                data.update(json.load(f))
        except:
            pass
    
    return (
        "🏔️ **INFORMASI RESMI & FITUR BARU RUTESTRIP BOT**\n\n"
        f"🌐 **Website Utama:** {data.get('website')}\n"
        f"🤖 **AI Chat RuteStrip:** {data.get('ai_chat')}\n"
        f"💬 **Grup Telegram Komunitas:** {data.get('telegram_group')}\n"
        f"📢 **Channel Informasi Resmi:** {data.get('telegram_channel')}\n\n"
        "✨ **UPDATE FITUR TERBARU:**\n"
        "1. 🥶 **Kalkulator Wind Chill & Risiko Hipotermia** ➔ Ketik `cuaca <nama_gunung>` (analisis suhu terasa, 4 level risiko, & rekomendasi layering pakaian).\n"
        "2. 📱 **Auto Story Card / Infografis Rute (9:16)** ➔ Ketik `story <nama_gunung>` atau `infografis <nama_gunung>` (poster profil elevasi GPX, elev gain, jarak, & waktu Naismith siap share Instagram/WA).\n\n"
        "💡 *Ketik `help` untuk melihat daftar lengkap 12 fitur pendakian.*"
    )

if __name__ == "__main__":
    print(get_info())
