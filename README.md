<div align="center">
  <img src="rutestrip_logo.png" alt="RuteStrip Pendakian Bot Logo" width="220"/>
  <h1>🏔️ RuteStrip Pendakian Bot</h1>
  <p><b>Asisten Pintar & Engine Rekomendasi Pendakian Gunung berbasis AI (SBERT), Analisis GPX, Peta Satelit, Topografi Kontur, Forecast Cuaca Realtime, & Audio Voice Briefing.</b></p>

  [![GitLab](https://img.shields.io/badge/GitLab-RuteStrip--Bot-orange?logo=gitlab)](https://gitlab.com/RamsNotes31/rutestrip-bot)
  [![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)](https://python.org)
  [![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
</div>

---

## 🖥️ Live Realtime Monitoring Dashboard & REST API

RuteStrip dilengkapi dengan **Realtime Infrastructure Dashboard** dan **REST API Service** untuk memantau performa VPS, status bot, serta mengintegrasikan data pendakian ke Web/Mobile App:

* 📊 **Realtime Status & AI Token Dashboard:** `http://188.166.224.148:9000` *(atau `https://airutestrip.web.id/monitoring`)*
* 🌐 **REST API Interactive Docs:** `http://188.166.224.148:8000/docs`
* 🌐 **Website Utama:** [https://rutestrip.web.id](https://rutestrip.web.id)
* 🤖 **AI Chat Assistant:** [https://airutestrip.web.id](https://airutestrip.web.id)
* 💬 **Grup Telegram Komunitas:** [@rutestrip_group](https://t.me/rutestrip_group)
* 📢 **Channel Telegram Resmi:** [@rutestrip](https://t.me/rutestrip)

---

## ⚡ Quickstart: One-Click Automated Installer (VPS Ubuntu Baru)

Untuk menginstall seluruh sistem RuteStrip Bot di VPS Ubuntu baru, cukup jalankan **1 baris perintah** di terminal:

```bash
curl -fsSL https://gitlab.com/RamsNotes31/rutestrip-bot/-/raw/main/install.sh | bash
```

### 📦 Yang Otomatis Terinstall & Konfigurasi Otomatis:
1. **Paket Sistem & Dependency Python:** `git`, `ffmpeg`, `python3`, `uv`, PyTorch CPU, SBERT, Matplotlib, Contextily, Psutil, & Edge-TTS.
2. **Framework Hermes & Custom Skill:** Skill `pendakian-jawa` otomatis dipasang ke `~/.hermes/skills/` lengkap dengan kebijakan Telegram DM (`dm_policy: open`) dan penataan cron response (`cron.wrap_response: false`).
3. **Database & Peta Offline:** 55 file trek GPX/KML, database ulasan `reviews.json`, info komunitas `info_rutestrip.json`, serta riwayat broadcast dinamis.
4. **Otomatisasi Cronjob & Daemon:** Registrasi otomatis 8 cronjob broadcast (cuaca, buletin channel, rekomendasi harian, tips survival, laporan admin) + peluncuran otomatis REST API (`Port 8000`) & Dashboard (`Port 9000`).

---

## 🔌 Setup 9Router AI Token Pool (Di VPS Baru)

Karena **OAuth Token / API Key akun Google/Antigravity** bersifat rahasia dan tidak disimpan di repositori Git demi keamanan:

1. Setelah menjalankan `install.sh`, jalankan 9Router di VPS baru.
2. Lakukan login ulang akun Google AI sekali saja via CLI/Web 9Router:
   ```bash
   9router auth login
   ```
3. Setelah login, 9Router akan otomatis meng-generate database token lokal baru di `/root/.9router/db/data.sqlite` dan terhubung kembali ke Hermes Agent serta Dashboard Monitoring.

---

## 🌟 Fitur Utama & Arsitektur Sistem

1. **🔒 Keamanan Lapis Ganda & Sandbox:**
   - **Public Open Policy (`dm_policy: open`):** Pengguna umum di Telegram dapat langsung menggunakan bot tanpa perlu kode verifikasi/pairing.
   - **Strict Input Sanitizer Sandbox:** Pengguna umum terisolasi 100% dari sistem VPS. Perintah modifikasi file/sistem otomatis ditolak. Hanya Pemilik/Admin Bot yang berhak menambah/mengedit fitur.

2. **🤖 Rekomendasi Rute AI (SBERT + Cosine Similarity):**
   - Menggunakan model `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (384 dimensi).
   - Fitur GPX (Jarak 3D, Elevation Gain, Grade %, Naismith Duration) + Deskripsi Manual.
   - High-speed JSON Caching (< 0.05 detik per query).

3. **🗺️ Visualisasi Peta Satelit & Topografi Kontur:**
   - **Peta Citra Satelit:** `Esri.WorldImagery` resolusi tinggi via Web Mercator EPSG:3857 (`satelit <gunung>`).
   - **Peta Topografi (Kontur):** Peta fisik topografi OpenTopoMap / Esri WorldTopo (`topografi <gunung>` atau `topo <gunung>`).
   - **Informasi Telemetri Otomatis:** Setiap peta dilengkapi data **Jarak Rute (`km`)**, **Total Elevation Gain (`+m`)**, dan **Rata-Rata Kemiringan (`%`)**.
   - **Smart Peak & Pos Markers:** Indikator nama-nama puncak spesifik & Waypoint Pos resmi.
   - **Trail Heatmap:** Kepadatan rute pendakian Pulau Jawa (`heatmap`).

4. **🎙️ Audio Voice & Text Briefing (Indonesian Ranger Tone):**
   - Sintesis suara pemandu ranger lokal Indonesia (`id-ID-ArdiNeural` via Edge-TTS & Opus).
   - Format ganda: Teks Markdown + Bubble Voice Note Telegram (`briefing <gunung>`).

5. **📡 Monitoring Cuaca Realtime (Open-Meteo API & Cronjob):**
   - Update cuaca berkala 25+ gunung utama Pulau Jawa & Bali.
   - Alert otomatis jika terjadi cuaca ekstrem di kawasan pendakian.

6. **⏱️ Itinerary & Kalkulator Pendakian:**
   - **Naismith Itinerary Generator:** Estimasi jam per pos (2D1N vs Tek-tok).
   - **Kalkulator Logistik & Air:** Estimasi konsumsi air (3L/orang/hari), tenda, gas kaleng, P3K (`logistik <orang> <hari>`).
   - **Kalkulator Biaya Pendakian:** Estimasi total budget simaksi, ojek, parkir, & konsumsi (`biaya <gunung> <orang> <hari>`).

7. **🗺️ Export Peta Offline (.gpx & .kml):**
   - Download file track `.gpx` & `.kml` langsung untuk OsmAnd, Maps.me, Locus Map, atau Garmin (`gpx <gunung>` / `kml <gunung>`).

8. **🧳 Kontak Porter & Basecamp Directory:**
   - Database telepon basecamp, ojek lokal, & estimasi tarif porter (`porter <gunung>`).

9. **🚑 First Aid & Survival Guide Offline:**
   - Panduan darurat penanganan Hipotermia, AMS, Tersesat (STOP Rule), & Gigitan Ular (`survival <topik>`).

---

## 🚀 Perintah Navigasi (Command CLI)

Bot mendukung kata kunci langsung tanpa tanda `/` untuk menghindari bentrok framework internal:

| Perintah | Deskripsi | Contoh |
|---|---|---|
| `help` / `menu` | Menampilkan menu panduan & daftar navigasi | `help` |
| `info` / `komunitas` | Informasi link website, AI chat, & grup komunitas | `info` |
| `rekomendasi <query>` | Rekomendasi rute AI SBERT + Cosine Sim | `rekomendasi jalur landai pemula` |
| `gpx <gunung>` | Export track file `.gpx` | `gpx sumbing` |
| `kml <gunung>` | Export track file `.kml` | `kml merbabu` |
| `heatmap [gunung]` | Grafik kontur topografi & heatmap rute | `heatmap sumbing` |
| `satelit [gunung]` | Peta citra satelit Esri World Imagery + Telemetri | `satelit sumbing` |
| `topografi [gunung]` | Peta topografi OpenTopoMap + Telemetri | `topografi slamet` |
| `briefing <gunung>` | Dual briefing (Teks + Voice Note Ranger) | `briefing merbabu` |
| `cuaca <gunung>` | Forecast cuaca realtime basecamp/puncak | `cuaca prau` |
| `itinerary <gunung> <mode>`| Timeline Naismith jam per pos | `itinerary sumbing 2d1n` |
| `logistik <orang> <hari>` | Kalkulator air & kebutuhan perlengkapan | `logistik 4 2` |
| `biaya <gunung> <orang> <hari>` | Estimasi total budget pendakian | `biaya sumbing 4 2` |
| `survival <topik>` | Panduan first aid darurat | `survival hipotermia` |
| `porter <gunung>` | Kontak basecamp, ojek, & tarif porter | `porter sumbing` |

---

## 📄 Lisensi

MIT License © 2026 RuteStrip Pendakian Bot Team.


<!-- AUTO_SYNC_START -->
> 🔄 *Last Automated Status Check: 2026-09-05 07:50:46 WIB*
<!-- AUTO_SYNC_END -->