---
name: pendakian-jawa
description: Use when asked for Java mountain routes. RuteStrip DB.
---

# RuteStrip Pendakian Bot Engine & Database

Database jalur, estimasi waktu, tingkat kesulitan, dan fitur pintar pendakian gunung di Pulau Jawa (Banten, Jabar, Jateng, Jatim).

## Aturan Komunikasi (User-Facing)
- DILARANG KERAS menampilkan path sistem (`/home/ubuntu/...`), log terminal, atau nama file internal ke pengguna.
- Perintah dipanggil tanpa tanda `/` untuk menghindari konflik framework (cth: `rekomendasi`, `cuaca`, `gpx`).
- Saat pengguna baru pertama kali datang / menyapa (`start`, `halo`, `help`), wajib berikan Onboarding & Navigasi Utama RuteStrip Pendakian Bot.

## Fitur & Engine Backend

1. **SBERT Recommendation System (Content-Based Filtering)**
   - Engine: `/home/ubuntu/pendakian_env/bin/python /home/ubuntu/rekomendasi_pendakian.py "<query>"`
   - Model: `paraphrase-multilingual-MiniLM-L12-v2` (384-dim) + JSON Caching + Cosine Sim.

2. **Weather Forecast Engine**
   - Engine: `/home/ubuntu/pendakian_env/bin/python /home/ubuntu/fitur_pendakian.py weather <lat> <lon>`
   - Open-Meteo API live forecast (suhu, kecepatan angin, cuaca ekstrim).

3. **Elevation Profile Chart Engine**
   - Engine: `/home/ubuntu/pendakian_env/bin/python /home/ubuntu/fitur_pendakian.py chart "<path_gpx>"`
   - Output: Grafik profil elevasi Matplotlib (`MEDIA:/tmp/elevation_profile.png`).

4. **Offline Map Exporter (GPX & KML)**
   - Engine: `python3 /home/ubuntu/gpx_exporter.py "<gunung>" <gpx|kml>`
   - Konversi & pengiriman track offline OsmAnd / Maps.me / Garmin.

5. **Itinerary Naismith & Logistics Calculator**
   - Engine: `python3 /home/ubuntu/itinerary_logistics.py itinerary <gunung> <mode>`
   - Engine Logistik: `python3 /home/ubuntu/itinerary_logistics.py logistics <orang> <hari>`

6. **Survival & Budget Calculator**
   - Engine: `python3 /home/ubuntu/survival_budget.py survival <topik>`
   - Engine Budget: `python3 /home/ubuntu/survival_budget.py budget <gunung> <orang> <hari>`

7. **Porter Transport Basecamp Directory**
 Engine:`python3 /home/ubuntu/porter_transport.py "<gunung>"`

8. **GPX Trail Heatmap Engine**
 Engine:`/home/ubuntu/pendakian_env/bin/python /home/ubuntu/gpx_heatmap.py [gunung]`
 Output: Visualisasi peta kepadatan rute pendakian per gunung / seluruh Jawa (`MEDIA:/tmp/gpx_heatmap.png`).


9. **Satellite Map Engine**
 Engine:`/home/ubuntu/pendakian_env/bin/python /home/ubuntu/satellite_map.py [gunung]`
 Output: Visualisasi peta citra satelit asli (Esri World Imagery + GPX overlay) (`MEDIA:/tmp/satellite_map.png`).

10. **Dual Format Briefing Engine (Text + Voice)**
 Engine:`python3 /home/ubuntu/pendakian_cli.py briefing <gunung>`
 Menghasilkan teks deskripsi ranger sekaligus voice note bubble secara bersamaan.



11. **Master CLI Router**
 Entry point:`python3 /home/ubuntu/pendakian_cli.py "<input>"`



