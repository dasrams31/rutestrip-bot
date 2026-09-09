#!/usr/bin/env python3
import json
import os

COMMUNITY_MSG = """Komunitas Pendaki RuteStrip Indonesia! 🎒

Yuk gabung dan dapatkan update info jalur pendakian, prakiraan cuaca realtime, serta diskusi sesama pendaki di Official Telegram RuteStrip! 📱✨

📢 Official Channel: https://t.me/rutestrip
🤖 Bot Interaktif: @rutestrip_bot
🌐 Web Chat App: https://airutestrip.web.id

Dapatkan info kuota simaksi, update kondisi gunung, dan tips keselamatan outdoor setiap hari!

Salam Lestari & Salam Pendaki! 🏕️🥾"""

def broadcast_to_users():
    # Cukup cetak isi pesan murni (tanpa header/target debug)
    print(COMMUNITY_MSG)

if __name__ == "__main__":
    broadcast_to_users()
