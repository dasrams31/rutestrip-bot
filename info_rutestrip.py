#!/usr/bin/env python3
import json
import sys
import os

INFO_PATH = os.path.join(os.path.dirname(__file__), "info_rutestrip.json")

def get_info():
    if not os.path.exists(INFO_PATH):
        return "Info RuteStrip tidak ditemukan."
    with open(INFO_PATH, "r") as f:
        data = json.load(f)
    
    return (
        "🏔️ **Informasi & Komunitas Resmi RuteStrip**\n\n"
        f"🌐 **Website Utama:** {data.get('website')}\n"
        f"🤖 **AI Chat Assistant:** {data.get('ai_chat')}\n"
        f"💬 **Grup Telegram:** {data.get('telegram_group')}\n"
        f"📢 **Channel Telegram:** {data.get('telegram_channel')}\n\n"
        "Bergabunglah dengan komunitas pendaki kami untuk info trek, cuaca, dan teman mendaki! 🎒"
    )

if __name__ == "__main__":
    print(get_info())
