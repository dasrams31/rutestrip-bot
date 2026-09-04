#!/usr/bin/env python3
import os
import json
import random

STATE_FILE = "/root/rutestrip-bot/recommendation_history.json"

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
    },
    {
        "nama": "Gunung Merbabu via Selo",
        "tinggi": "3.145 mdpl",
        "level": "Menengah",
        "estimasi": "6 - 7 Jam",
        "highlight": "Hamparan sabana luas nan hijau, pemandangan Gunung Merapi dari dekat, dan sunset memukau di Pos 4 / Sabana 1.",
        "tips": "Bawa stok air minum yang cukup karena mata air hanya ada di bagian bawah jalur."
    },
    {
        "nama": "Gunung Sumbing via Kaliangkrik / Adipura",
        "tinggi": "3.371 mdpl",
        "level": "Menengah - Tantangan",
        "estimasi": "7 - 8 Jam",
        "highlight": "Desa Nepal van Java yang ikonik di kaki gunung, lautan awan menakjubkan, dan kawah aktif Sumbing.",
        "tips": "Jalur cukup terik di bagian awal, disarankan memakai topi atau balaclava serta sunscreen."
    },
    {
        "nama": "Gunung Papandayan via Cisurupan",
        "tinggi": "2.665 mdpl",
        "level": "Sangat Ramah Pemula",
        "estimasi": "2 - 3 Jam",
        "highlight": "Kawasan kawah aktif yang spektakuler, Hutan Mati yang eksotis, dan padang Edelweiss Tegal Panjang.",
        "tips": "Jalur sangat bersahabat bagi pendaki pemula maupun keluarga."
    },
    {
        "nama": "Gunung Slamet via Bambangan",
        "tinggi": "3.428 mdpl",
        "level": "Menengah - Berat",
        "estimasi": "9 - 11 Jam",
        "highlight": "Atap tertinggi Jawa Tengah, medan batuan vulkanik puncak yang menantang, dan pemandangan pulau Jawa yang luas.",
        "tips": "Gunakan gaiter dan alas kaki ber-grip kuat untuk melewati tanjakan pasir dan batuan puncak."
    },
    {
        "nama": "Gunung Sindoro via Kledung",
        "tinggi": "3.153 mdpl",
        "level": "Menengah",
        "estimasi": "6 - 7 Jam",
        "highlight": "Sabana edelweiss di Pos 3, pemandangan Gunung Sumbing di seberang, dan kawah pasir luas di puncak.",
        "tips": "Waspadai bau belerang di sekitar puncak jika angin berhembus ke arah jalur."
    }
]

def get_next_recommendation():
    used = []
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                used = json.load(f)
        except Exception:
            used = []

    available = [item for item in RECOMMENDATIONS if item["nama"] not in used]
    if not available:
        used = []
        available = RECOMMENDATIONS

    selected = random.choice(available)
    used.append(selected["nama"])

    try:
        with open(STATE_FILE, "w") as f:
            json.dump(used, f, indent=2)
    except Exception:
        pass

    return selected

item = get_next_recommendation()

output = f"""REKOMENDASI PENDAKIAN HARIAN & WEEKEND GETAWAY 🌄
Inspirasi Rute Pendakian RuteStrip

📍 {item['nama']}
• Ketinggian: {item['tinggi']}
• Tingkat Kesulitan: {item['level']}
• Estimasi Waktu: {item['estimasi']}

Pesona Jalur:
{item['highlight']}

Tips Ranger RuteStrip:
{item['tips']}

---
Cek rute & gpx gunung lainnya dengan ketik `rekomendasi <kriteria>` atau `gpx <nama_gunung>`!
Website: https://rutestrip.web.id | Grup: @rutestrip_group"""

print(output)
