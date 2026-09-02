# 🏔️ RuteStrip Pendakian Bot

Bot Asisten Pintar & Rekomendasi Pendakian Gunung berbasis AI, SBERT (Sentence-Transformers), Analisis GPX, Forecast Cuaca Realtime, Visualisasi Peta Satelit / Topografi, dan Audio Voice Briefing.

---

## 🌟 Fitur Utama & Keamanan

1. **Akses Publik Tanpa Verifikasi (`dm_policy: open`):**
   - Pengguna umum di Telegram dapat langsung menggunakan bot tanpa perlu kode verifikasi/pairing.
   - Terintegrasi dengan **Strict Input Sanitizer Sandbox** untuk memastikan pengguna umum hanya dapat mengakses fitur pendakian dan **terisolasi 100% dari sistem VPS**.

2. **Rekomendasi Rute AI (SBERT + Cosine Similarity):**
   - Menggunakan model `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (384 dimensi).
   - Ekstraksi fitur GPX (Jarak 3D, Elevation Gain, Grade %, Durasi Rumus Naismith) + Deskripsi Manual.
   - Peringkatan kecocokan natural language query dengan JSON Caching instant (< 0.05s).

3. **Visualisasi Peta Satelit & Topografi (Contour & Esri World Imagery):**
   - Peta Citra Satelit Resolusi Tinggi (`Esri.WorldImagery` via Contextily & Web Mercator).
   - Peta Kontur Elevasi Topografi Matplotlib (Garis Kontur mdpl + Interpolasi Cubic DEM).
   - Trail Heatmap kepadatan rute pendakian Pulau Jawa per gunung / kawasan.

4. **Audio Voice & Text Briefing (Indonesian Ranger Accent):**
   - Sintesis suara pemandu ranger lokal Indonesia (`id-ID-ArdiNeural` via Edge-TTS & Opus).
   - Format ganda: Teks Markdown + Bubble Voice Note Telegram (`[[audio_as_voice]]`).

5. **Monitoring Cuaca Realtime (Open-Meteo API & Cronjob):**
   - Update cuaca berkala tiap 3 jam (Suhu, Angin, Peringatan Hujan/Badai).
   - Peringatan dini otomatis untuk cuaca ekstrem.

6. **Itinerary & Kalkulator Pendakian:**
   - **Naismith Itinerary Generator:** Estimasi jam per pos (2D1N vs Tek-tok).
   - **Kalkulator Logistik & Air:** Estimasi konsumsi air (3L/orang/hari), tenda, gas kaleng, P3K.
   - **Kalkulator Biaya Pendakian:** Estimasi total budget simaksi, ojek, parkir, & konsumsi.

7. **Export Peta Offline (.gpx & .kml):**
   - Download file track `.gpx` & `.kml` langsung untuk OsmAnd, Maps.me, Locus Map, atau Garmin.

8. **Kontak Porter & Basecamp Directory:**
   - Database telepon basecamp, ojek lokal, & estimasi tarif porter terverifikasi.

9. **First Aid & Survival Guide Offline:**
   - Panduan darurat penanganan Hipotermia, AMS, Tersesat (STOP Rule), & Gigitan Ular.

---

## 🚀 Perintah Navigasi (Command CLI)

Bot mendukung kata kunci tanpa tanda `/` untuk menghindari bentrok framework:

| Perintah | Deskripsi | Contoh |
|---|---|---|
| `help` / `menu` | Menampilkan menu panduan & daftar navigasi | `help` |
| `info <gunung>` | Detail rute, ketinggian, & simaksi resmi | `info gede` |
| `rekomendasi <query>` | Rekomendasi rute AI SBERT + Cosine Sim | `rekomendasi jalur landai pemula` |
| `gpx <gunung>` | Export track file `.gpx` | `gpx sumbing` |
| `kml <gunung>` | Export track file `.kml` | `kml merbabu` |
| `heatmap [gunung]` | Grafik kontur topografi & heatmap rute | `heatmap sumbing` |
| `satelit [gunung]` | Peta citra satelit Esri World Imagery | `satelit merbabu` |
| `briefing <gunung>` | Dual briefing (Teks + Voice Note Ranger) | `briefing merbabu` |
| `cuaca <gunung>` | Forecast cuaca realtime basecamp/puncak | `cuaca prau` |
| `itinerary <gunung> <mode>`| Timeline Naismith jam per pos | `itinerary sumbing 2d1n` |
| `logistik <orang> <hari>` | Kalkulator air & kebutuhan perlengkapan | `logistik 4 2` |
| `biaya <gunung> <orang> <hari>` | Estimasi total budget pendakian | `biaya sumbing 4 2` |
| `survival <topik>` | Panduan first aid darurat | `survival hipotermia` |
| `porter <gunung>` | Kontak basecamp, ojek, & tarif porter | `porter sumbing` |

---

## 🛠️ Instalasi & Cara Jalankan

```bash
# Clone repository
git clone https://gitlab.com/RamsNotes31/rutestrip-bot.git
cd rutestrip-bot

# Buat virtual environment & install dependensi
uv venv pendakian_env
uv pip install --python pendakian_env -r requirements.txt

# Set Telegram Public DM Access
hermes config set telegram.dm_policy open

# Jalankan CLI Router
python3 pendakian_cli.py help
```

---

## 📂 Struktur Project

```text
rutestrip-bot/
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
├── auto_readme_commit.py    # Automated Randomized Commit Script
├── cek_cuaca_gunung.py      # Automated Weather Cronjob Script
├── requirements.txt         # Package Dependencies
├── SETUP_VPS_HERMES_BOT.md  # Panduan Instalasi VPS & Configuration
├── skills/
│   └── pendakian-jawa/
│       └── SKILL.md         # Skill Spec & Backend Routing Protocol
└── README.md                # Dokumentasi Project
```

---

## 📄 Lisensi

MIT License © 2026 RuteStrip Pendakian Bot Team.
