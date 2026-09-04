#!/usr/bin/env python3
import subprocess

res = subprocess.run(["python3", "/root/rutestrip-bot/cek_cuaca_gunung.py"], capture_output=True, text=True)
cuaca_text = res.stdout.strip()

# Bersihkan markdown formatting yang kaku
cuaca_text = cuaca_text.replace("**", "").replace("🚨 ", "").replace("⚠️ ", "").replace("📡 ", "")

output = f"""LAPORAN LIVE CUACA GUNUNG UTAMA PULAU JAWA
(Update Otomatis Komunitas RuteStrip)

{cuaca_text}

Selalu siapkan perlengkapan sesuai kondisi cuaca di atas (windbreaker, ponco, atau goggles).
Website: https://rutestrip.web.id | Grup: @rutestrip_group"""

print(output)
