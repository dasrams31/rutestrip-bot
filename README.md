# 🏔️ RuteStrip Pendakian Bot & REST API Engine

RuteStrip Pendakian Bot adalah asisten AI pintar, visualizer peta satelit/topografi, serta kalkulator pendakian gunung profesional untuk kawasan pendakian gunung di Indonesia (khususnya Pulau Jawa).

---

## 🌟 Informasi Resmi RuteStrip Platform

- 🌐 **Website Utama:** https://rutestrip.web.id
- 🤖 **Web Chat AI:** https://airutestrip.web.id
- 💬 **Telegram Bot:** https://t.me/rutestrip_bot
- 📢 **Channel Resmi Telegram:** https://t.me/rutestrip

---

## ⚡ Fitur Utama System

1. **🤖 Rekomendasi Rute AI (SBERT + Cosine Similarity):**
   - Engine rekomendasi berbasis AI SBERT (`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`) 384-dimensi.
   - Pengecekan elevasi, Naismith duration, & skor relevansi query.

2. **🗺️ Visualisasi Peta Satelit & Topografi Kontur:**
   - Citra Satelit Esri WorldImagery resolusi tinggi & Peta fisik topografi kontur.
   - Dilengkapi garis rute trek GPX, waypoint pos, & telemetri elevasi.

3. **📡 Monitoring Cuaca Realtime (Open-Meteo API):**
   - Forecast cuaca realtime basecamp & puncak gunung (Suhu, Angin, Peringatan Cuaca Ekstrem).

4. **⏱️ Itinerary & Kalkulator Pendakian:**
   - Naismith Itinerary Generator (2D1N vs Tek-tok).
   - Kalkulator Logistik Air (3L/orang/hari) & Estimasi Budget Biaya Pendakian.

5. **🧳 Kontak Porter & Basecamp Directory:**
   - Database nomor kontak basecamp pendakian & tarif porter lokal.

6. **🚑 First Aid & Survival Guide:**
   - Panduan darurat penanganan Hipotermia, AMS, & STOP Rule di alam bebas.

7. **📥 Export Peta Offline (.gpx & .kml):**
   - Download file rute `.gpx` & `.kml` untuk OsmAnd, Maps.me, Locus Map, atau Garmin.

---

## 🚀 Perintah Navigasi Telegram Bot

Pengguna dapat mengetik kata kunci langsung di Telegram Bot tanpa tanda `/`:

- `help` / `menu` : Menampilkan menu utama & panduan
- `rekomendasi <query>` : Rekomendasi rute AI SBERT
- `satelit <gunung>` : Peta citra satelit Esri + telemetri
- `topografi <gunung>` : Peta topografi kontur + telemetri
- `cuaca <gunung>` : Prakiraan cuaca realtime
- `itinerary <gunung> <mode>` : Timeline Naismith 2D1N/Tek-tok
- `biaya <gunung> <orang> <hari>` : Estimasi total budget
- `logistik <orang> <hari>` : Kalkulator kebutuhan air & bahan
- `gpx <gunung>` : Export track file `.gpx` / `.kml`
- `porter <gunung>` : Kontak basecamp & ojek lokal
- `survival <topik>` : Panduan first-aid darurat

---

## 📄 Lisensi

MIT License © 2026 RuteStrip Pendakian Team.


<!-- AUTO_SYNC_START -->
> 🔄 *Last Automated Status Check: 2026-09-03 22:13:01 WIB*
<!-- AUTO_SYNC_END -->