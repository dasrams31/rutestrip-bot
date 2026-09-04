#!/usr/bin/env python3

output = """🤖 **PANDUAN LENGKAP PENGGUNAAN RUTESTRIP BOT** 🏔️✨
*(Kelola Rencana Pendakianmu Langsung dari Chat)*

Halo Sobat Pendaki! Bingung cari rute, cek cuaca, atau hitung logistik? Gunakan kata kunci di bawah ini (tanpa tanda `/`):

1. 🔍 **Rekomendasi Rute AI (SBERT Engine)**
   * `rekomendasi <kriteria>` ➔ *Contoh: `rekomendasi gunung 3000 mdpl landai pemula`*

2. ☀️ **Prakiraan Cuaca Live Realtime**
   * `cuaca <nama_gunung>` ➔ *Contoh: `cuaca merbabu`*

3. 📍 **Peta Satelit, Topografi & GPX Offline**
   * `satelit <nama_gunung>` ➔ Citra satelit asli + telemetri trek.
   * `topografi <nama_gunung>` ➔ Peta fisik garis kontur.
   * `gpx <nama_gunung>` / `kml <nama_gunung>` ➔ Download file trek offline (OsmAnd/Garmin).

4. 🧮 **Kalkulator Itinerary, Logistik & Anggaran**
   * `itinerary <nama_gunung> <mode>` ➔ *Contoh: `itinerary sumbing 2d1n`*
   * `logistik <jumlah_orang> <jumlah_hari>` ➔ *Contoh: `logistik 4 2`*
   * `biaya <nama_gunung> <orang> <hari>` ➔ *Contoh: `biaya prau 3 2`*

5. 🎙️ **Audio Briefing Ranger (Voice Note)**
   * `briefing <nama_gunung>` ➔ Pengarahan jalur dalam teks + voice note.

6. 🦺 **Porter, Transportasi Basecamp & Survival**
   * `porter <nama_gunung>` ➔ Info kontak ojek & porter basecamp.
   * `survival <topik>` ➔ *Contoh: `survival hipotermia`*

7. 🌐 **Informasi Komunitas & Platform**
   * `info` / `komunitas` ➔ Akses website utama & AI chat.

---
💡 *Coba ketik salah satu perintah di atas sekarang!*
🌐 **Website:** https://rutestrip.web.id | 💬 **Grup:** @rutestrip_group"""

print(output)
