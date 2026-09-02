import sys
import re
import subprocess

# Strict Whitelist Commands
ALLOWED_COMMANDS = {
    "start", "help", "menu", "halo", "hi", "p",
    "info", "rekomendasi", "rekomendasi_rute", "gpx", "kml",
    "satelit", "satellite", "heatmap", "cuaca", "itinerary",
    "logistik", "biaya", "survival", "porter", "briefing", "voice"
}

# Forbidden System Probing Patterns
BLOCKED_PATTERNS = [
    r'\.\./', r'/etc/', r'/var/', r'/proc/', r'/sys/', r'/root',
    r'sudo', r'rm\s', r'cat\s', r'chmod', r'chown', r'exec', r'eval',
    r'system', r'bash', r'sh\s', r'python', r'ls\s', r'pwd'
]

WELCOME_GUIDE = """Selamat datang di **RuteStrip Pendakian Bot** 🏔️

Gunakan kata kunci langsung (tanpa tanda `/`) untuk navigasi fitur:

---

### 🗺️ **NAVIGASI UTAMA**

1. **Info Gunung & Simaksi** ➔ `info <nama_gunung>`
2. **Rekomendasi Rute (SBERT AI)** ➔ `rekomendasi <preferensi>`
3. **Export Peta Offline** ➔ `gpx <nama_gunung>` / `kml <nama_gunung>`
4. **Peta Satelit & Heatmap** ➔ `satelit [gunung]` / `heatmap [gunung]`
5. **Briefing Ranger (Dual Format)** ➔ `briefing <nama_gunung>`
6. **Prakiraan Cuaca Live** ➔ `cuaca <nama_gunung>`
7. **Itinerary Naismith** ➔ `itinerary <nama_gunung> <2d1n|tektok>`
8. **Kalkulator Logistik & Air** ➔ `logistik <jumlah_orang> <jumlah_hari>`
9. **Estimasi Biaya Pendakian** ➔ `biaya <nama_gunung> <jumlah_orang> <jumlah_hari>`
10. **Panduan Darurat Survival** ➔ `survival <topik>`
11. **Kontak Porter & Transport** ➔ `porter <nama_gunung>`

---
💡 *Ketik `help` kapan saja untuk menampilkan menu ini.*"""

def sanitize_input(text: str) -> bool:
    for pat in BLOCKED_PATTERNS:
        if re.search(pat, text, re.IGNORECASE):
            return False
    return True

def handle_command(cmd_str: str):
    raw = cmd_str.strip()
    
    # 1. System Access Probe Protection
    if not sanitize_input(raw):
        return "⚠️ Akses ditolak. Perintah sistem tidak diizinkan. Ketik `help` untuk daftar menu pendakian."
        
    clean = raw[1:] if raw.startswith('/') else raw
    parts = clean.split()
    if not parts:
        return WELCOME_GUIDE
    
    cmd = parts[0].lower()
    args = parts[1:]
    
    # 2. Strict Whitelist Enforcement
    if cmd not in ALLOWED_COMMANDS:
        return f"⚠️ Perintah `{cmd}` tidak dikenal. Anda hanya memiliki akses ke fitur pendakian RuteStrip. Ketik `help` untuk daftar menu."

    if cmd in ["start", "help", "menu", "halo", "hi", "p"]:
        return WELCOME_GUIDE
    elif cmd in ["briefing", "voice"]:
        m = args[0] if args else "merbabu"
        res = subprocess.run(["/home/ubuntu/pendakian_env/bin/python", "/home/ubuntu/briefing_audio.py", m], capture_output=True, text=True)
        txt = res.stdout.strip()
        return f"🎙️ **AUDIO & TEKS BRIEFING PENDAKIAN ({m.upper()})**\n\n📝 **Teks Briefing Ranger:**\n\"{txt}\"\n\n[[audio_as_voice]]\nMEDIA:/tmp/briefing_indonesia.ogg"
    elif cmd in ["satelit", "satellite"]:
        q = args[0] if args else "sumbing"
        subprocess.run(["/home/ubuntu/pendakian_env/bin/python", "/home/ubuntu/satellite_map.py", q], capture_output=True, text=True)
        return "MEDIA:/tmp/satellite_map.png"
    elif cmd == "heatmap":
        q = args[0] if args else ""
        subprocess.run(["/home/ubuntu/pendakian_env/bin/python", "/home/ubuntu/gpx_heatmap.py", q], capture_output=True, text=True)
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

if __name__ == "__main__":
    c = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "help"
    print(handle_command(c))
