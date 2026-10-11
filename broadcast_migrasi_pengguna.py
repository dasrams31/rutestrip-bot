#!/usr/bin/env python3
"""
Migrasi Pengumuman & Broadcast Reaktivasi ke Seluruh Database Pengguna Lama RuteStrip
"""

import urllib.request
import urllib.error
import json
import time

BOT_TOKEN = "8904397226:AAE4QF8GRYkGi_HWOQ5tTjZMJxrVDYoyoxc"

MESSAGE = """🏔️ <b>RUTESTRIP RESMI BERPINDAH KE BOT BARU!</b> 🥾✨

Halo Sobat Pendaki! 👋

Untuk meningkatkan kestabilan layanan, kecepatan respon AI, dan akurasi data cuaca Open-Meteo per pos pendakian, asisten pendakian RuteStrip kini <b>resmi beroperasi di bot baru</b>:

🤖 <b>Bot Baru:</b> <a href="https://t.me/rutestrip_hikingbot">@rutestrip_hikingbot</a>
🌐 <b>Web Portal:</b> https://airutestrip.web.id

━━━━━━━━━━━━━━━━━━━━
⚡ <b>Apa yang Baru di @rutestrip_hikingbot?</b>
🔹 <b>Chat Bebas & Luwes:</b> Bisa ngobrol santai tanpa harus kaku pakai garis miring (<code>/</code>).
🔹 <b>Prakiraan Cuaca Realtime:</b> Data suhu, angin, & potensi hujan per gunung.
🔹 <b>Kalkulator Naismith:</b> Estimasi jam tempuh fisik & logistik otomatis.
🔹 <b>Database 55+ GPX:</b> Unduh peta jalur resmi se-Pulau Jawa.

━━━━━━━━━━━━━━━━━━━━
👉 <b>Klik link berikut untuk mengaktifkan bot baru:</b>
👉 <a href="https://t.me/rutestrip_hikingbot">@rutestrip_hikingbot</a>

<i>Salam Lestari & Sampai Jumpa di Puncak!</i> 🌲⛰️"""

def main():
    # Kumpulkan seluruh ID dari semua database pengguna
    all_targets = set()
    
    # 1. Subscribers
    try:
        with open("/home/ubuntu/rutestrip-bot/subscribers.json") as f:
            d = json.load(f)
            for k in d.keys():
                if k.isdigit() or k.startswith("-100") or k.startswith("@"):
                    all_targets.add(k)
    except Exception:
        pass

    # 2. Chat Sessions
    try:
        with open("/home/ubuntu/rutestrip-bot/users_chat_sessions.json") as f:
            d = json.load(f)
            for k in d.keys():
                if k.isdigit() or k.startswith("-100") or k.startswith("@"):
                    all_targets.add(k)
    except Exception:
        pass

    # 3. Users Auth
    try:
        with open("/home/ubuntu/rutestrip-bot/users_auth.json") as f:
            d = json.load(f)
            for k in d.keys():
                if k.isdigit() or k.startswith("-100") or k.startswith("@"):
                    all_targets.add(k)
    except Exception:
        pass

    # Target Resmi
    all_targets.add("@rutestrip")

    print(f"[*] Total target teridentifikasi: {len(all_targets)}")
    
    success = 0
    blocked = 0

    for target in sorted(all_targets):
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": target,
            "text": MESSAGE,
            "parse_mode": "HTML",
            "disable_web_page_preview": False
        }
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                res = json.loads(resp.read().decode())
                if res.get("ok"):
                    print(f"    [+] Berhasil kirim ke {target}")
                    success += 1
        except urllib.error.HTTPError as e:
            # 400 chat not found / bot blocked by user
            blocked += 1
            print(f"    [-] Lewati {target}: {e.code} (Belum start bot baru / privasi Telegram)")
        except Exception as e:
            blocked += 1
            print(f"    [-] Error {target}: {e}")
        time.sleep(0.3)

    print(f"\n[✓] Selesai! Berhasil terkirim: {success}, Tertahan regulasi privasi DM bot baru: {blocked}")

if __name__ == "__main__":
    main()
