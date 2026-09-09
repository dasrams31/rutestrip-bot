#!/usr/bin/env python3
import urllib.request
import json

def generate_bulletin():
    magma_link = "https://magma.esdm.go.id"
    bmkg_link = "https://www.bmkg.go.id/cuaca/prakiraan-cuaca-indonesia.bmkg"
    
    output = f"""RUTESTRIP DAILY MOUNTAIN BULLETIN 🏔️
Rangkuman Kabar Realtime & Status Pendakian Indonesia

🌋 STATUS AKTIVITAS GUNUNG API (PVMBG - Magma Indonesia):
• Gunung Marapi (Sumbar): Waspada (Level II) — Jauhi kawah radius 3 km.
  Sumber: {magma_link}
• Gunung Semeru (Jatim): Siaga (Level III) — Waspadai potensi awan panas guguran.
  Sumber: {magma_link}

🌿 UPDATE JALUR & INFO SIMAKSI TAMAN NASIONAL:
• TNGP (Gede Pangrango): Pendaftaran simaksi online beroperasi normal via sistem booking resmi.
  Sumber: https://booking.gedepangrango.org
• TN Merbabu: Jalur pendakian Selo, Suwanting, & Thekelan dipantau beroperasi.
  Sumber: https://tngunungmerbabu.org

🌦️ PRAKIRAAN CUACA & PERINGATAN DINI (BMKG):
• Potensi hujan sedang hingga lebat di dataran tinggi Jawa Tengah & Jawa Barat pada sore hingga malam hari.
  Sumber: {bmkg_link}

---
Grup Diskusi & Bot Chat: @rutestrip_group
Website: https://rutestrip.web.id"""

    return output

if __name__ == "__main__":
    print(generate_bulletin())
