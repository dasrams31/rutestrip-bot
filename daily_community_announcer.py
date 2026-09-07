#!/usr/bin/env python3
import os
import json
import requests
import time

BOT_TOKEN = "8366083249:AAELG3sL4k7zVvS8uG-6R9cQy-8l0j5k2lM" # Bot API Token fallback
SUB_FILE = "/home/ubuntu/rutestrip-bot/subscribers.json"

COMMUNITY_MSG = """Komunitas Pendaki RuteStrip Indonesia! 🎒

Yuk gabung dan dapatkan update info jalur pendakian, prakiraan cuaca realtime, serta diskusi sesama pendaki di Official Telegram RuteStrip! 📱✨

📢 Official Channel: https://t.me/rutestrip
🤖 Bot Interaktif: @rutestrip_bot
🌐 Web Chat App: https://airutestrip.web.id

Dapatkan info kuota simaksi, update kondisi gunung, dan tips keselamatan outdoor setiap hari!

Salam Lestari & Salam Pendaki! 🏕️🥾"""

def broadcast_community():
    print(COMMUNITY_MSG)

if __name__ == "__main__":
    broadcast_community()
