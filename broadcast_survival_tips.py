#!/usr/bin/env python3
import random

SURVIVAL_TIPS = [
    {
        "judul": "Pertolongan Pertama Penanganan Hipotermia di Gunung 🥶",
        "poin": [
            "Ganti segera pakaian basah/kemeringat dengan pakaian kering tebal.",
            "Masudkan korban ke dalam Sleeping Bag (SB) dan alas matras tebal.",
            "Berikan minuman manis hangat (teh/gula merah), hindari memberi kopi/alkohol.",
            "Lakukan kontak fisik hangat (*skin-to-skin*) jika tingkat hipotermia parah."
        ]
    },
    {
        "judul": "Prinsip S.T.O.P Saat Tersesat di Hutan/Gunung 🌲🧭",
        "poin": [
            "**S (Stop):** Berhenti melangkah, jangan panik, dan tenangkan diri.",
            "**T (Think):** Berpikir jernih tentang rute terakhir yang diingat.",
            "**O (Observe):** Amati sekitar (arah mata angin, sumber air, jejak kaki, patok jalur).",
            "**P (Plan):** Buat rencana: buka camp/perlindungan atau tiup peluit darurat."
        ]
    },
    {
        "judul": "7 Prinsip Utama Leave No Trace (Etika Kelestarian Alam) 🌿",
        "poin": [
            "Perencanakan pendakian dengan matang & pahami SOP lokasi.",
            "Mendaki dan berkemah di atas permukaan yang tahan lama (jalur resmi).",
            "Buang sampah pada tempatnya — Bawa turun seluruh sampah pribadi!",
            "Biarkan apa yang Anda temukan (jangan memetik edelweiss/merusak fasilitas).",
            "Minimalkan dampak api unggun & selalu hormati sesama pendaki."
        ]
    },
    {
        "judul": "Pertolongan Pertama Penanganan AMS (Mountain Sickness) 🏔️😷",
        "poin": [
            "**Gejala:** Pusing hebat, mual, lemas, dan nafas pendek di ketinggian.",
            "**Tindakan 1:** Berhenti melakukan elevasi/tanjakan lebih tinggi.",
            "**Tindakan 2:** Istirahat total, minum air putih cukup, dan hirup oksigen kaleng jika ada.",
            "**Tindakan Utama:** Jika kondisi tidak membaik dalam 1-2 jam, segera TURUN ke elevasi lebih rendah!"
        ]
    },
    {
        "judul": "Manajemen Air & Hidrasi Saat Pendakian 💧🎒",
        "poin": [
            "Kebutuhan standar: Minim 3-4 Liter air per orang per 2 hari 1 malam.",
            "Minum secara berkala dalam tegukan kecil (jangan menunggu terdesak haus parah).",
            "Gunakan penyaring air (water filter) atau rebus air jika mengambil dari mata air alam."
        ]
    }
]

item = random.choice(SURVIVAL_TIPS)

output = f"""🦺 **EDUKASI SURVIVAL & ETIKA PENDAKI RUTESTRIP** 🎒
*(Tips Keselamatan & Kelestarian Alam)*

📌 **{item['judul']}**

"""
for p in item['poin']:
    output += f"• {p}\n"

output += """
---
🚨 *Ketik `survival <topik>` (cth: `survival hipotermia`) untuk panduan darurat offline lengkap!*
🌐 **Website:** https://rutestrip.web.id | 💬 **Grup:** @rutestrip_group"""

print(output)
