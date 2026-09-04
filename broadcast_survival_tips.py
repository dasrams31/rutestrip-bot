#!/usr/bin/env python3
import random

SURVIVAL_TIPS = [
    {
        "judul": "Pertolongan Pertama Penanganan Hipotermia di Gunung 🥶",
        "poin": [
            "Ganti segera pakaian basah atau berkeringat dengan pakaian kering dan tebal.",
            "Masukkan korban ke dalam Sleeping Bag (SB) dengan alas matras tebal.",
            "Berikan minuman manis hangat (teh hangat atau air gula merah), hindari memberi kopi atau alkohol.",
            "Lakukan kontak fisik hangat (skin-to-skin) jika tingkat hipotermia parah."
        ]
    },
    {
        "judul": "Prinsip S.T.O.P Saat Tersesat di Hutan atau Gunung 🌲🧭",
        "poin": [
            "Stop: Berhenti melangkah, jangan panik, dan tenangkan diri.",
            "Think: Berpikir jernih tentang rute terakhir yang diingat.",
            "Observe: Amati sekitar (arah mata angin, sumber air, jejak kaki, patok jalur).",
            "Plan: Buat rencana, buka tempat perlindungan/tenda atau tiup peluit darurat."
        ]
    },
    {
        "judul": "7 Prinsip Utama Leave No Trace (Etika Kelestarian Alam) 🌿",
        "poin": [
            "Rencanakan pendakian dengan matang dan pahami SOP lokasi.",
            "Mendaki dan berkemah di jalur resmi yang sudah ditentukan.",
            "Bawa turun seluruh sampah pribadi tanpa terkecuali.",
            "Biarkan apa yang Anda temukan di alam (jangan memetik edelweiss).",
            "Minimalkan dampak api unggun dan selalu hormati sesama pendaki."
        ]
    },
    {
        "judul": "Pertolongan Pertama Penanganan AMS (Mountain Sickness) 🏔️",
        "poin": [
            "Gejala: Pusing hebat, mual, lemas, dan nafas pendek di ketinggian.",
            "Tindakan 1: Berhenti naik ke lokasi yang lebih tinggi.",
            "Tindakan 2: Istirahat total, minum air putih cukup, dan hirup oksigen kaleng jika ada.",
            "Tindakan Utama: Jika kondisi tidak membaik dalam 1-2 jam, segera TURUN ke elevasi lebih rendah!"
        ]
    },
    {
        "judul": "Manajemen Air & Hidrasi Saat Pendakian 💧",
        "poin": [
            "Kebutuhan standar: Minimal 3-4 Liter air per orang untuk 2 hari 1 malam.",
            "Minum secara berkala dalam tegukan kecil, jangan menunggu sampai terlalu haus.",
            "Gunakan penyaring air (water filter) atau rebus air jika mengambil dari mata air alam."
        ]
    }
]

item = random.choice(SURVIVAL_TIPS)

output = f"""EDUKASI SURVIVAL & ETIKA PENDAKI RUTESTRIP 🦺
Tips Keselamatan & Kelestarian Alam

📌 {item['judul']}

"""
for p in item['poin']:
    output += f"• {p}\n"

output += """
---
Ketik `survival <topik>` (contoh: `survival hipotermia`) untuk panduan darurat offline lengkap.
Website: https://rutestrip.web.id | Grup: @rutestrip_group"""

print(output)
