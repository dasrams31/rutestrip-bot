import sys
import subprocess

WELCOME_GUIDE = """Selamat datang di **RuteStrip Pendakian Bot** 🏔️

Gunakan kata kunci langsung (tanpa tanda `/`) untuk navigasi fitur:

---

### 🗺️ **NAVIGASI UTAMA**

1. **Info Gunung & Simaksi**
   • Format: `info <nama_gunung>`
   • Contoh: `info gede`, `info ciremai`, `info merbabu`

2. **Rekomendasi Rute (SBERT AI)**
   • Format: `rekomendasi <preferensi>`
   • Contoh: `rekomendasi jalur landai pemula`, `rekomendasi sabana luas`

3. **Export Peta Offline (GPX / KML)**
   • Format: `gpx <nama_gunung>` / `kml <nama_gunung>`
   • Contoh: `gpx sumbing`, `kml merbabu`

4. **Visualisasi Peta Satelit & Topografi**
   • Format: `satelit [nama_gunung]` / `heatmap [nama_gunung]`
   • Contoh: `satelit sumbing`, `heatmap merbabu`

5. **Audio Voice & Text Briefing (Dual Format)**
   • Format: `briefing <nama_gunung>`
   • Contoh: `briefing merbabu`, `briefing sumbing`

6. **Prakiraan Cuaca Live**
   • Format: `cuaca <nama_gunung>`
   • Contoh: `cuaca prau`, `cuaca slamet`

7. **Itinerary Naismith (Timeline Jam)**
   • Format: `itinerary <nama_gunung> <2d1n|tektok>`
   • Contoh: `itinerary sumbing 2d1n`

8. **Kalkulator Logistik & Air**
   • Format: `logistik <jumlah_orang> <jumlah_hari>`
   • Contoh: `logistik 4 2`

9. **Estimasi Biaya Pendakian**
   • Format: `biaya <nama_gunung> <jumlah_orang> <jumlah_hari>`
   • Contoh: `biaya sumbing 4 2`

10. **Panduan Darurat (First Aid & Survival)**
   • Format: `survival <topik>`
   • Contoh: `survival hipotermia`

11. **Kontak Porter & Transport Basecamp**
   • Format: `porter <nama_gunung>`
   • Contoh: `porter sumbing`, `porter merbabu`

---

💡 *Ketik `help` atau `menu` kapan saja untuk menampilkan navigasi ini.*"""

def handle_command(cmd_str: str):
    raw = cmd_str.strip()
    clean = raw[1:] if raw.startswith('/') else raw
    parts = clean.split()
    if not parts:
        return WELCOME_GUIDE
    
    cmd = parts[0].lower()
    args = parts[1:]
    
    if cmd in ["start", "help", "menu", "halo", "hi", "p"]:
        return WELCOME_GUIDE
    elif cmd in ["briefing", "voice"]:
        m = args[0] if args else "merbabu"
        res = subprocess.run(["/home/ubuntu/pendakian_env/bin/python", "/home/ubuntu/briefing_audio.py", m], capture_output=True, text=True)
        txt = res.stdout.strip()
        out_msg = f"🎙️ **AUDIO & TEKS BRIEFING PENDAKIAN ({m.upper()})**\n\n📝 **Teks Briefing Ranger:**\n\"{txt}\"\n\n[[audio_as_voice]]\nMEDIA:/tmp/briefing_indonesia.ogg"
        return out_msg
    elif cmd in ["satelit", "satellite"]:
        q = args[0] if args else "sumbing"
        res = subprocess.run(["/home/ubuntu/pendakian_env/bin/python", "/home/ubuntu/satellite_map.py", q], capture_output=True, text=True)
        return "MEDIA:/tmp/satellite_map.png"
    elif cmd == "heatmap":
        q = args[0] if args else ""
        res = subprocess.run(["/home/ubuntu/pendakian_env/bin/python", "/home/ubuntu/gpx_heatmap.py", q], capture_output=True, text=True)
        return "MEDIA:/tmp/gpx_heatmap.png"
    elif cmd in ["gpx", "kml"]:
        q = " ".join(args) if args else "sumbing kaliangkrik"
        fmt = "kml" if cmd == "kml" else "gpx"
        res = subprocess.run(["python3", "/home/ubuntu/gpx_exporter.py", q, fmt], capture_output=True, text=True)
        out = res.stdout.strip()
        if out.startswith("GPX:") or out.startswith("KML:"):
            fpath = out.split(":", 1)[1]
            return f"MEDIA:{fpath}"
        return out
    elif cmd in ["rekomendasi", "rekomendasi_rute"]:
        query = " ".join(args) if args else "jalur landai ramah pemula"
        res = subprocess.run(["/home/ubuntu/pendakian_env/bin/python", "/home/ubuntu/rekomendasi_pendakian.py", query], capture_output=True, text=True)
        return res.stdout
    elif cmd == "cuaca":
        m = args[0] if args else "sumbing"
        res = subprocess.run(["python3", "/home/ubuntu/cek_cuaca_gunung.py"], capture_output=True, text=True)
        return res.stdout
    elif cmd == "itinerary":
        m = args[0] if args else "sumbing"
        mode = args[1] if len(args) > 1 else "2d1n"
        res = subprocess.run(["python3", "/home/ubuntu/itinerary_logistics.py", "itinerary", m, mode], capture_output=True, text=True)
        return res.stdout
    elif cmd == "logistik":
        people = args[0] if args else "3"
        days = args[1] if len(args) > 1 else "2"
        res = subprocess.run(["python3", "/home/ubuntu/itinerary_logistics.py", "logistics", people, days], capture_output=True, text=True)
        return res.stdout
    elif cmd == "survival":
        top = args[0] if args else "hipotermia"
        res = subprocess.run(["python3", "/home/ubuntu/survival_budget.py", "survival", top], capture_output=True, text=True)
        return res.stdout
    elif cmd == "biaya":
        m = args[0] if args else "sumbing"
        g = args[1] if len(args) > 1 else "3"
        d = args[2] if len(args) > 2 else "2"
        res = subprocess.run(["python3", "/home/ubuntu/survival_budget.py", "budget", m, g, d], capture_output=True, text=True)
        return res.stdout
    elif cmd == "porter":
        m = args[0] if args else "sumbing"
        res = subprocess.run(["python3", "/home/ubuntu/porter_transport.py", m], capture_output=True, text=True)
        return res.stdout
    else:
        return f"Perintah `{cmd}` tidak dikenal. Ketik `help` untuk menampilkan menu."

if __name__ == "__main__":
    c = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "help"
    print(handle_command(c))
