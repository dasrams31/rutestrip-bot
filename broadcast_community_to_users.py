#!/usr/bin/env python3
import json
import os
import requests
import time

SUB_FILE = "/root/rutestrip-bot/subscribers.json"

COMMUNITY_MSG = """Komunitas Pendaki RuteStrip Indonesia! 🎒

Yuk gabung dan dapatkan update info jalur pendakian, prakiraan cuaca realtime, serta diskusi sesama pendaki di Official Telegram RuteStrip! 📱✨

📢 Official Channel: https://t.me/rutestrip
🤖 Bot Interaktif: @rutestrip_bot
🌐 Web Chat App: https://airutestrip.web.id

Dapatkan info kuota simaksi, update kondisi gunung, dan tips keselamatan outdoor setiap hari!

Salam Lestari & Salam Pendaki! 🏕️🥾"""

def broadcast_to_users():
    if not os.path.exists(SUB_FILE):
        print("Subscribers file not found.")
        return

    with open(SUB_FILE, "r") as f:
        subs = json.load(f)

    for chat_id_str, info in subs.items():
        if not chat_id_str.startswith("-"):
            print(COMMUNITY_MSG)
            print("\n--- TARGET USER DM: " + chat_id_str + " ---\n")

if __name__ == "__main__":
    broadcast_to_users()
