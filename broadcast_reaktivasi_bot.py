#!/usr/bin/env python3
"""
Broadcast Announcer: Notifikasi Re-Aktivasi RuteStrip Hiking Bot ke Seluruh Pengguna & Channel
Dikirim via Bot Baru: @rutestrip_hikingbot (Format HTML Aman)
"""

import urllib.request
import urllib.error
import json
import time

BOT_TOKEN = "8904397226:AAE4QF8GRYkGi_HWOQ5tTjZMJxrVDYoyoxc"

MESSAGE = """🏔️ <b>RUTESTRIP HIKING BOT KEMBALI AKTIF!</b> 🥾✨

Halo Sobat Pendaki! 👋

Layanan asisten pintar pendakian gunung di Pulau Jawa kini telah <b>resmi aktif kembali</b> dengan performa yang lebih cepat, akurat, dan stabil di bot baru kami:

🤖 <b>Bot Resmi:</b> @rutestrip_hikingbot
🌐 <b>Web Portal:</b> https://airutestrip.web.id

━━━━━━━━━━━━━━━━━━━━

⚡ <b>Fitur Unggulan Siap Pakai:</b>
🔹 <b>Rekomendasi Jalur & SBERT:</b> <code>/rekomendasi</code> — Rekomendasi gunung sesuai kebugaran & preferensi.
🔹 <b>Prakiraan Cuaca Realtime:</b> <code>/cuaca</code> — Data akurat Open-Meteo per ketinggian pos.
🔹 <b>Kalkulator Itinerary & Naismith:</b> <code>/itinerary</code> — Estimasi waktu tempuh & beban logistik.
🔹 <b>Database GPX Jalur:</b> <code>/gpx</code> — Unduh peta rute resmi 55+ jalur gunung di Jawa.
🔹 <b>Panduan Survival:</b> <code>/survival</code> — Mitigasi risiko, hipotermia, & navigasi darurat.
🔹 <b>Split Bill Logistik:</b> <code>/splitbill</code> — Hitung patungan grup otomatis.

━━━━━━━━━━━━━━━━━━━━
👉 <b>Mulai chat sekarang:</b> <a href="https://t.me/rutestrip_hikingbot">@rutestrip_hikingbot</a>

<i>Salam Lestari & Selamat Menjelajah!</i> 🌲⛰️"""

def send_message(chat_id: str, text: str) -> bool:
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            res = json.loads(resp.read().decode())
            return res.get("ok", False)
    except urllib.error.HTTPError as e:
        print(f"[-] Gagal kirim ke {chat_id}: {e.code} - {e.read().decode()}")
        return False
    except Exception as e:
        print(f"[-] Gagal kirim ke {chat_id}: {e}")
        return False

def main():
    with open("/home/ubuntu/rutestrip-bot/subscribers.json", "r") as f:
        subs = json.load(f)

    print(f"[*] Memulai broadcast re-aktivasi ke {len(subs)} target via @rutestrip_hikingbot...")
    
    success_count = 0
    fail_count = 0

    for target in subs:
        print(f"[>] Mengirim ke {target}...")
        ok = send_message(target, MESSAGE)
        if ok:
            print(f"    [+] Berhasil terkirim ke {target}")
            success_count += 1
        else:
            fail_count += 1
        time.sleep(0.4)

    # Kirim ke grup dan channel resmi
    official_targets = ["@rutestrip", "@rutestrip_group"]
    for t in official_targets:
        if t not in subs:
            print(f"[>] Mengirim ke target resmi {t}...")
            ok = send_message(t, MESSAGE)
            if ok:
                print(f"    [+] Berhasil terkirim ke {t}")
                success_count += 1
            else:
                fail_count += 1
            time.sleep(0.4)

    print(f"\n[✓] Broadcast selesai! Sukses: {success_count}, Gagal: {fail_count}")

if __name__ == "__main__":
    main()
