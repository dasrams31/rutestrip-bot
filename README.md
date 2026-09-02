<div align="center">
  <img src="rutestrip_logo.png" alt="RuteStrip Pendakian Bot Logo" width="220"/>
  <h1>🏔️ RuteStrip Pendakian Bot</h1>
  <p><b>Asisten Pintar & Engine Rekomendasi Pendakian Gunung berbasis AI (SBERT), Analisis GPX, Peta Satelit, Topografi Kontur, Forecast Cuaca Realtime, & Audio Voice Briefing.</b></p>

  [![GitLab](https://img.shields.io/badge/GitLab-RuteStrip--Bot-orange?logo=gitlab)](https://gitlab.com/RamsNotes31/rutestrip-bot)
  [![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)](https://python.org)
  [![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
</div>

---

## 🌐 REST API Service & Web Chatbot Integration

RuteStrip Bot dilengkapi dengan **REST API Service (FastAPI)** berkecepatan tinggi yang dapat langsung dihubungkan ke Frontend Web Chatbot, React, Vue, maupun Mobile App.

* **Base Domain API (HTTPS):** `https://cement-affiliation-firm-jesus.trycloudflare.com`
* **Dokumentasi Interactive Swagger:** `https://cement-affiliation-firm-jesus.trycloudflare.com/docs`

### 📌 Endpoint Utama REST API:

| Method | Endpoint | Deskripsi & Parameter Contoh |
|---|---|---|
| `GET` | `/api/rekomendasi` | **AI SBERT Recommendation.** `https://cement-affiliation-firm-jesus.trycloudflare.com/api/rekomendasi?query=gunung%203000%20mdpl%20landai%20pemula` |
| `GET` | `/api/cuaca` | **Forecast Cuaca Live.** `https://cement-affiliation-firm-jesus.trycloudflare.com/api/cuaca?mountain=sumbing` |
| `GET` | `/api/map/satellite` | **Peta Satelit / Topografi (PNG).** `https://cement-affiliation-firm-jesus.trycloudflare.com/api/map/satellite?mountain=slamet&map_type=topografi` |
| `GET` | `/api/gpx` | **Download File GPX/KML.** `https://cement-affiliation-firm-jesus.trycloudflare.com/api/gpx?mountain=cikuray&format=gpx` |
| `GET` | `/api/itinerary` | **Naismith Itinerary Generator.** `https://cement-affiliation-firm-jesus.trycloudflare.com/api/itinerary?mountain=sumbing&mode=2d1n` |
| `GET` | `/api/logistik` | **Kalkulator Logistik & Air.** `https://cement-affiliation-firm-jesus.trycloudflare.com/api/logistik?people=4&days=2` |
| `GET` | `/api/biaya` | **Estimasi Biaya Pendakian.** `https://cement-affiliation-firm-jesus.trycloudflare.com/api/biaya?mountain=sumbing&people=3&days=2` |
| `GET` | `/api/survival` | **Panduan Survival First Aid.** `https://cement-affiliation-firm-jesus.trycloudflare.com/api/survival?topic=hipotermia` |
| `GET` | `/api/porter` | **Kontak Porter & Basecamp.** `https://cement-affiliation-firm-jesus.trycloudflare.com/api/porter?mountain=sumbing` |

### 💻 Contoh Integrasi Web Chatbot (JavaScript):
```javascript
// Contoh pemanggilan REST API dari Web Chatbot Frontend
fetch('https://cement-affiliation-firm-jesus.trycloudflare.com/api/rekomendasi?query=gunung%20landai%20pemula')
  .then(res => res.json())
  .then(data => console.log("Hasil Rekomendasi:", data.results));
```

---

## ⚡ Quickstart: One-Click Automated Installer (VPS Ubuntu)

Untuk menginstall seluruh sistem RuteStrip Bot di VPS Ubuntu baru, cukup jalankan **1 baris perintah** di terminal:

```bash
curl -fsSL https://gitlab.com/RamsNotes31/rutestrip-bot/-/raw/main/install.sh | bash
```

Perintah di atas otomatis:
- Mengunduh & menginstall paket sistem Linux (`git`, `ffmpeg`, `curl`, `python3`).
- Menyiapkan environment Python via `uv` & menginstall dependensi PyTorch CPU, SBERT, Matplotlib, Contextily, & Edge-TTS.
- Memasang Custom Skill `pendakian-jawa`, script backend, & konfigurasi Telegram DM Open Policy (`dm_policy: open`).
- Mengaktifkan cronjob pemantauan cuaca otomatis 7 gunung utama Pulau Jawa & auto-commit harian.

---

## 🌟 Fitur Utama & Arsitektur Sistem

1. **🔒 Keamanan Lapis Ganda & Sandbox:**
   - **Public Open Policy (`dm_policy: open`):** Pengguna umum di Telegram dapat langsung menggunakan bot tanpa perlu kode verifikasi/pairing.
   - **Strict Input Sanitizer Sandbox:** Pengguna umum terisolasi 100% dari sistem VPS. Perintah modifikasi file/sistem otomatis ditolak. Hanya Pemilik/Admin Bot (**Rama**) yang berhak menambah/mengedit fitur.

2. **🤖 Rekomendasi Rute AI (SBERT + Cosine Similarity):**
   - Menggunakan model `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (384 dimensi).
   - Fitur GPX (Jarak 3D, Elevation Gain, Grade %, Naismith Duration) + Deskripsi Manual.
   - High-speed JSON Caching (< 0.05 detik per query).

3. **🗺️ Visualisasi Peta Satelit & Topografi Kontur:**
   - **Peta Citra Satelit:** `Esri.WorldImagery` resolusi tinggi via Web Mercator EPSG:3857 (`satelit <gunung>`).
   - **Peta Topografi (Kontur):** Peta fisik topografi OpenTopoMap / Esri WorldTopo (`topografi <gunung>` atau `topo <gunung>`).
   - **Informasi Telemetri Otomatis:** Setiap peta dilengkapi data **Jarak Rute (`km`)**, **Total Elevation Gain (`+m`)**, dan **Rata-Rata Kemiringan (`%`)**.
   - **Smart Peak & Pos Markers:** Indikator nama-nama puncak spesifik (*Puncak Rajawali, Puncak Sejati, Puncak Buntu, Puncak Bowongso, dll*) & Waypoint Pos resmi.
   - **Trail Heatmap:** Kepadatan rute pendakian Pulau Jawa (`heatmap`).

4. **🎙️ Audio Voice & Text Briefing (Indonesian Ranger Tone):**
   - Sintesis suara pemandu ranger lokal Indonesia (`id-ID-ArdiNeural` via Edge-TTS & Opus).
   - Format ganda: Teks Markdown + Bubble Voice Note Telegram (`briefing <gunung>`).

5. **📡 Monitoring Cuaca Realtime (Open-Meteo API & Cronjob):**
   - Update cuaca berkala tiap 3 jam (Suhu, Angin, Peringatan Hujan/Badai).
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
| `info <gunung>` | Detail rute, ketinggian, & simaksi resmi | `info gede` |
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

## 📂 Struktur Project

```text
rutestrip-bot/
├── install.sh               # One-Click Automated VPS Installer Script
├── rekomendasi_pendakian.py  # Engine SBERT & Cosine Similarity + GPX Extractor
├── fitur_pendakian.py        # Weather Forecast (Open-Meteo) & Elevation Profile Chart
├── itinerary_logistics.py    # Naismith Itinerary Generator & Logistics Calculator
├── survival_budget.py       # Survival First-Aid Guide & Budget Calculator
├── porter_transport.py      # Basecamp & Porter Contact Directory
├── gpx_exporter.py          # GPX to KML Converter & Track Exporter
├── gpx_heatmap.py           # Topographic Contour Map & Heatmap Generator
├── satellite_map.py         # Esri World Imagery Satellite Map Generator
├── briefing_audio.py        # Voice Note Synthesis (Edge-TTS id-ID-ArdiNeural)
├── pendakian_cli.py         # Master CLI Command Router & Strict Input Sanitizer
├── generate_logo.py         # Official Vector & PNG Logo Generator
├── auto_readme_commit.py    # Automated Randomized Commit Script
├── cek_cuaca_gunung.py      # Automated Weather Cronjob Script
├── requirements.txt         # Package Dependencies
├── SETUP_VPS_HERMES_BOT.md  # Panduan Instalasi Manual VPS & Configuration
├── rutestrip_logo.png       # Official PNG Logo
├── rutestrip_logo.svg       # Official Vector SVG Logo
├── skills/
│   └── pendakian-jawa/
│       └── SKILL.md         # Skill Spec & Backend Routing Protocol
└── README.md                # Dokumentasi Utama Project
```

---

## 📄 Lisensi

MIT License © 2026 RuteStrip Pendakian Bot Team.


<!-- AUTO_SYNC_START -->
> 🔄 *Last Automated Status Check: 2026-09-02 15:58:08 WIB*
<!-- AUTO_SYNC_END -->