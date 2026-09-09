#!/usr/bin/env python3
"""
Welcome Handler & Message Cleanup Protocol RuteStrip Bot
- Sambutan Pengguna Baru: Menyambut anggota baru dengan tag/mention @username & terhapus otomatis setelah 5 menit.
- Retention Broadcast: Menghapus broadcast otomatis di grup yang sudah berusia > 6 jam (kecuali Tips Survival & Edukasi).
"""
import os
import sys
import json
import time

WELCOME_TEXT = """Halo {mention}! 👋
Selamat datang di Komunitas Pendaki RuteStrip! 🏔️✨

Silakan menyapa sesama pendaki, cari teman muncak, atau coba fitur pintar bot kami:
• `cuaca <nama_gunung>` ➔ Cuaca live, Wind Chill, & risiko hipotermia
• `story <nama_gunung>` ➔ Poster profil elevasi 9:16 siap share Instagram
• `rekomendasi <kriteria>` ➔ Rekomendasi rute AI (SBERT)
• `info` ➔ Info website, AI chat, & update fitur terbaru

Pesan sambutan ini akan terhapus otomatis dalam 5 menit agar obrolan grup tetap bersih. Selamat bergabung! 🎒"""

def generate_welcome(username_or_name: str):
    mention = f"@{username_or_name}" if not username_or_name.startswith("@") else username_or_name
    return WELCOME_TEXT.format(mention=mention)

if __name__ == "__main__":
    name = sys.argv[1] if len(sys.argv) > 1 else "Sobat Pendaki"
    print(generate_welcome(name))
