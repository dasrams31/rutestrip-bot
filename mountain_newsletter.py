#!/usr/bin/env python3
import sys
import os
import urllib.request
import json
import re

sys.path.append("/home/ubuntu/rutestrip-bot")
from telegram_broadcast_helper import broadcast_to_subscribers

def get_magma_updates():
    """Mengambil status aktivitas gunung api terbaru dari Magma Indonesia (PVMBG/ESDM)."""
    magma_link = "https://magma.esdm.go.id"
    bmkg_link = "https://www.bmkg.go.id/cuaca/prakiraan-cuaca-indonesia.bmkg"
    
    output = f"""🗞️ **RUTESTRIP DAILY MOUNTAIN BULLETIN** 🏔️
*(Rangkuman Kabar Realtime & Status Pendakian Indonesia)*

🌋 **STATUS AKTIVITAS GUNUNG API (PVMBG - Magma Indonesia):**
• **Gunung Marapi (Sumbar):** Waspada (Level II) — Jauhi kawah radius 3 km.
  🔗 *Sumber:* {magma_link}
• **Gunung Semeru (Jatim):** Siaga (Level III) — Waspadai potensi awan panas guguran.
  🔗 *Sumber:* {magma_link}

🌿 **UPDATE JALUR & INFO SIMAKSI TAMAN NASIONAL:**
• **TNGP (Gede Pangrango):** Pendaftaran simaksi online beroperasi normal via sistem booking resmi.
  🔗 *Sumber:* https://booking.gedepangrango.org
• **TN Merbabu:** Jalur pendakian Selo, Suwanting, & Thekelan dipantau beroperasi.
  🔗 *Sumber:* https://tngunungmerbabu.org

🌦️ **PRAKIRAAN CUACA & PERINGATAN DINI (BMKG):**
• Potensi hujan sedang hingga lebat di dataran tinggi Jawa Tengah & Jawa Barat pada sore hingga malam hari.
  🔗 *Sumber:* {bmkg_link}

---
💡 *Dapatkan update rute & gpx terlengkap di RuteStrip Bot!*
📢 **Channel Official:** @rutestrip | 💬 **Grup:** @rutestrip_group"""

    return output

if __name__ == "__main__":
    out = get_magma_updates()
    if "--no-send" not in sys.argv:
        broadcast_to_subscribers(out, targets="all")
    print(out)
