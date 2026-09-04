#!/usr/bin/env python3
import random
import datetime

# Daftar Gunung & Bukit Mini untuk Rekomendasi Pendakian Harian / Weekend Getaway
RECOMMENDATIONS = [
    {
        "nama": "Gunung Prau via Dieng / Patakbanteng",
        "tinggi": "2.565 mdpl",
        "level": "Pemula - Menengah",
        "estimasi": "3 - 4 Jam",
        "highlight": "Golden Sunrise terbaik se-Jawa Tengah, hamparan bukit Teletubbies, dan pemandangan megah Gunung Sindoro-Sumbing.",
        "tips": "Suhu puncak bisa sangat dingin (di bawah 10°C), siapkan jaket tebal dan sleeping bag hangat."
    },
    {
        "nama": "Gunung Andong via Sawit / Pendem",
        "tinggi": "1.726 mdpl",
        "level": "Sangat Ramah Pemula",
        "estimasi": "1,5 - 2 Jam",
        "highlight": "Jalur santai dengan bonus pemandangan 360 derajat Gunung Merbabu, Merapi, Telomoyo, dan Ungaran.",
        "tips": "Cocok untuk tektok (naik-turun sehari) atau camping ceria keluarga di akhir pekan."
    },
    {
        "nama": "Bukit Sikendil via Sibajag",
        "tinggi": "1.800 mdpl",
        "level": "Pemula (Tektok Santai)",
        "estimasi": "45 - 60 Menit",
        "highlight": "Trek singkat namun menyajikan panorama Gunung Sindoro yang sangat dekat dan megah dari puncaknya.",
        "tips": "Bawa air secukupnya dan gunakan sepatu/sandal gunung ber-grip karena ada beberapa tanjakan tanah."
    },
    {
        "nama": "Gunung Kembang via Blembem",
        "tinggi": "2.340 mdpl",
        "level": "Menengah (Jalur Bersih)",
        "estimasi": "3 - 4 Jam",
        "highlight": "Kawasan kebun teh yang sangat asri, aturan pengelolaan sampah yang sangat ketat, serta pemandangan kawah di puncak.",
        "tips": "Patuhi SOP cek barang bawaan di basecamp, pastikan tidak meninggalkan sampah sekecil apa pun."
    },
    {
        "nama": "Bukit Bismo via Silandak / Hasunegara",
        "tinggi": "2.365 mdpl",
        "level": "Pemula - Menengah",
        "estimasi": "2 - 3 Jam",
        "highlight": "Panorama tebing kawah purba yang memukau dan pemandangan lanskap Pegunungan Dieng.",
        "tips": "Hati-hati saat berfoto di area tebing puncak, selalu utamakan keselamatan."
    },
    {
        "nama": "Gunung Gede via Gunung Putri / Cibodas",
        "tinggi": "2.958 mdpl",
        "level": "Menengah",
        "estimasi": "6 - 8 Jam",
        "highlight": "Alun-Alun Suryakencana dengan hamparan bunga Bunga Abadi (Edelweiss), Kawah Gede, dan Telaga Biru.",
        "tips": "Pastikan sudah mendaftar simaksi online jauh-jauh hari dan bawa ponco/jas hujan."
    },
    {
        "nama": "Gunung Cikuray via Pemancar",
        "tinggi": "2.821 mdpl",
        "level": "Menengah - Fisik Fit",
        "estimasi": "6 - 7 Jam",
        "highlight": "Negeri di atas awan dengan samudra awan tebal di pagi hari dan trek menanjak tanpa bonus.",
        "tips": "Latih fisik kaki sebelum mendaki dan pastikan pasokan air minum mencukupi."
    }
]

# Pilih rekomendasi acak berdasarkan hari
item = random.choice(RECOMMENDATIONS)

output = f"""🏞️ **REKOMENDASI PENDAKIAN HARIAN & WEEKEND GETAWAY** 🎒
*(Inspirasi Rute Pendakian RuteStrip)*

📍 **{item['nama']}**
• **Ketinggian:** {item['tinggi']}
• **Tingkat Kesulitan:** {item['level']}
• **Estimasi Waktu:** {item['estimasi']}

✨ **Highlight & Pesona Jalur:**
{item['highlight']}

💡 **Tips Ranger RuteStrip:**
{item['tips']}

---
🔎 *Cek rute & gpx gunung lainnya dengan ketik `rekomendasi <kriteria>` atau `gpx <nama_gunung>`!*
🌐 **Website:** https://rutestrip.web.id | 💬 **Grup:** @rutestrip_group"""

print(output)
