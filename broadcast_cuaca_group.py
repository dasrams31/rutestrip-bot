#!/usr/bin/env python3
import subprocess
import sys

# Panggil script cek_cuaca_gunung.py
res = subprocess.run(["python3", "/root/rutestrip-bot/cek_cuaca_gunung.py"], capture_output=True, text=True)
cuaca_text = res.stdout.strip()

output = f"""🏔️ **LAPORAN LIVE CUACA GUNUNG UTAMA PULAU JAWA**
*(Update Otomatis Komunitas RuteStrip)*

{cuaca_text}

📍 *Selalu siapkan perlengkapan sesuai kondisi cuaca di atas (Windbreaker/Ponco/Goggles)!*
🌐 **Website:** https://rutestrip.web.id | 💬 **Grup:** @rutestrip_group"""

print(output)
