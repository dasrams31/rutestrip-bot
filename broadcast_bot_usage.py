#!/usr/bin/env python3

output = """PANDUAN LENGKAP PENGGUNAAN RUTESTRIP BOT 🏔️✨
(Kelola Rencana Pendakianmu Langsung dari Chat)

Halo Sobat Pendaki! Gunakan kata kunci langsung (tanpa tanda `/`) untuk navigasi:

1. 🗺️ Informasi & Rekomendasi Jalur AI
   • `info <nama_gunung>` ➔ Contoh: `info merbabu`
   • `rekomendasi <kriteria>` ➔ Contoh: `rekomendasi pemula sabana`
   • `briefing <nama_gunung>` ➔ Teks & Voice Note pengarahan ranger
   • `guidebook <nama_gunung>` / `pdf <nama_gunung>` ➔ Download E-Guidebook PDF siap cetak

2. 🌦️ Prakiraan Cuaca, Wind Chill & Peta
   • `cuaca <nama_gunung>` ➔ Contoh: `cuaca slamet` (suhu terasa wind chill & level hipotermia)
   • `satelit <nama_gunung>` ➔ Citra satelit asli + rute trek
   • `heatmap <nama_gunung>` ➔ Peta kontur topografi elevasi 3D
   • `gpx <nama_gunung>` / `kml <nama_gunung>` ➔ Download file navigasi GPS offline

3. ⏱️ Itinerary, Logistik & Patungan (Split Bill)
   • `itinerary <gunung> [mode]` ➔ Contoh: `itinerary sumbing 2d1n`
   • `logistik <orang> <hari>` ➔ Contoh: `logistik 4 2` (kalkulator ransum & air)
   • `biaya <gunung> <orang> <hari>` ➔ Contoh: `biaya prau 3 2`
   • `patungan <gunung> <orang> <hari>` ➔ Split bill & kas darurat tim

4. 🆘 Survival, Porter & Infografis Story
   • `survival <topik>` ➔ Contoh: `survival hipotermia`
   • `porter <nama_gunung>` ➔ Info kontak ojek & porter basecamp
   • `story <nama_gunung>` / `infografis <nama_gunung>` ➔ Poster visual profil elevasi 9:16
   • `komunitas` ➔ Link channel info & grup diskusi pendaki

---
🌐 Website: https://rutestrip.web.id | 💬 Grup: @rutestrip_group | 📢 Channel: @rutestrip"""

if __name__ == "__main__":
    print(output)
