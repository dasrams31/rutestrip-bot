import sys
import re
import subprocess

# Owner User ID Check
OWNER_USER_ID = "606533609"

VENV_PYTHON = "/root/rutestrip-bot/pendakian_env/bin/python"
PYTHON3 = "python3"
ALLOWED_COMMANDS = {
    "start", "help", "menu", "halo", "hi", "p",
    "info", "rekomendasi", "rekomendasi_rute", "gpx", "kml",
    "satelit", "satellite", "heatmap", "cuaca", "itinerary",
    "logistik", "biaya", "survival", "porter", "briefing", "voice"
}

# Forbidden System & Feature Manipulation Patterns for Public Users
BLOCKED_PATTERNS = [
    r'\.\./', r'/etc/', r'/var/', r'/proc/', r'/sys/', r'/root',
    r'sudo', r'rm\s', r'cat\s', r'chmod', r'chown', r'exec', r'eval',
    r'system', r'bash', r'sh\s', r'python', r'ls\s', r'pwd',
    r'tambah', r'edit', r'buat', r'modifikasi', r'update', r'bikin', r'install'
]

WELCOME_GUIDE = """Halo! Selamat datang di **RuteStrip Pendakian Bot** 🏔️
Saya adalah asisten pintar pendakian gunung yang siap membantu perencanaan dan panduan jalur pendakian Anda.

---

### 🗺️ **DAFTAR PERINTAH & FITUR BOT**

1. 🗺️ **Rekomendasi & Pencarian Gunung**
   * `rekomendasi <kriteria>` (cth: `rekomendasi pemula jawa tengah`)
   * Mencari gunung sesuai preferensi Anda menggunakan sistem AI (SBERT engine).

2. 🎙️ **Briefing Suara Ranger (TTS)**
   * `briefing <nama_gunung>` (cth: `briefing prau`)
   * Memberikan pengarahan jalur dalam bentuk teks sekaligus pesan suara (*voice note*).

3. 📍 **Peta & File Navigasi (GPX / KML)**
   * `gpx <nama_gunung>` / `kml <nama_gunung>` ➔ Download trek peta offline (OsmAnd/Garmin).
   * `chart <nama_gunung>` ➔ Grafik profil elevasi jalur.
   * `satelit <nama_gunung>` / `heatmap <nama_gunung>` ➔ Citra satelit asli & peta kepadatan trek.

4. ☀️ **Prakiraan Cuaca Live**
   * `cuaca <nama_gunung>` ➔ Info suhu, cuaca, dan angin terkini.

5. 🧮 **Logistik, Itinerary & Anggaran**
   * `itinerary <nama_gunung> <santai/normal/cepat>` ➔ Estimasi waktu Naismith per pos.
   * `logistik <jumlah_orang> <jumlah_hari>` ➔ Kalkulator konsumsi air & bahan makanan.
   * `biaya <nama_gunung> <jumlah_orang> <jumlah_hari>` ➔ Estimasi rincian biaya pendakian.

6. 🦺 **Porter, Transportasi & Tips Survival**
   * `porter <nama_gunung>` ➔ Info kontak porter & transportasi basecamp.
   * `survival <topik>` (cth: `survival hipotermia`) ➔ Panduan penanganan darurat.

7. ⭐️ **Ulasan & Rating Jalur**
   * `review <nama_gunung>` ➔ Lihat ulasan pendaki lain.
   * `review <nama_gunung> <1-5> <komentar>` ➔ Tambahkan ulasan Anda.

---
💡 *Ketik perintah tanpa tanda `/`. Ketik `help` atau `/start` kapan saja untuk menampilkan menu ini.*"""

def sanitize_input(text: str) -> bool:
    for pat in BLOCKED_PATTERNS:
        if re.search(pat, text, re.IGNORECASE):
            return False
    return True

def handle_command(cmd_str: str):
    raw = cmd_str.strip()
    
    # 1. System Access & Feature Tampering Block
    if not sanitize_input(raw):
        return "⚠️ Akses Terbatas: Hanya Pemilik/Admin Bot (Rama) yang berhak menambah, mengedit, atau memodifikasi fitur bot. Ketik `help` untuk daftar menu pendakian."
        
    clean = raw[1:] if raw.startswith('/') else raw
    parts = clean.split()
    if not parts:
        return WELCOME_GUIDE
    
    cmd = parts[0].lower()
    args = parts[1:]
    
    # 2. Strict Whitelist Enforcement for Public Users
    if cmd not in ALLOWED_COMMANDS:
        return f"⚠️ Perintah `{cmd}` tidak diizinkan. Pengguna umum hanya dapat menggunakan fitur pendakian yang tersedia. Ketik `help` untuk daftar menu."

    if cmd in ["start", "help", "menu", "halo", "hi", "p"]:
        return WELCOME_GUIDE
    elif cmd in ["briefing", "voice"]:
        m = args[0] if args else "merbabu"
        res = subprocess.run([VENV_PYTHON, "/root/briefing_audio.py", m], capture_output=True, text=True)
        txt = res.stdout.strip()
        return f"🎙️ **AUDIO & TEKS BRIEFING PENDAKIAN ({m.upper()})**\n\n📝 **Teks Briefing Ranger:**\n\"{txt}\"\n\n[[audio_as_voice]]\nMEDIA:/tmp/briefing_indonesia.ogg"
    elif cmd in ["satelit", "satellite"]:
        q = args[0] if args else "sumbing"
        subprocess.run([VENV_PYTHON, "/root/satellite_map.py", q], capture_output=True, text=True)
        return "MEDIA:/tmp/satellite_map.png"
    elif cmd == "heatmap":
        q = args[0] if args else ""
        subprocess.run([VENV_PYTHON, "/root/gpx_heatmap.py", q], capture_output=True, text=True)
        return "MEDIA:/tmp/gpx_heatmap.png"
    elif cmd in ["gpx", "kml"]:
        q = " ".join(args) if args else "sumbing kaliangkrik"
        fmt = "kml" if cmd == "kml" else "gpx"
        res = subprocess.run([PYTHON3, "/root/rutestrip-bot/gpx_exporter.py", q, fmt], capture_output=True, text=True)
        out = res.stdout.strip()
        if out.startswith("GPX:") or out.startswith("KML:"):
            fpath = out.split(":", 1)[1]
            return f"MEDIA:{fpath}"
        return out
    elif cmd in ["rekomendasi", "rekomendasi_rute"]:
        query = " ".join(args) if args else "jalur landai ramah pemula"
        res = subprocess.run([VENV_PYTHON, "/root/rekomendasi_pendakian.py", query], capture_output=True, text=True)
        return res.stdout
    elif cmd == "cuaca":
        res = subprocess.run([PYTHON3, "/root/cek_cuaca_gunung.py"], capture_output=True, text=True)
        return res.stdout
    elif cmd == "itinerary":
        m = args[0] if args else "sumbing"
        mode = args[1] if len(args) > 1 else "2d1n"
        res = subprocess.run([PYTHON3, "/root/itinerary_logistics.py", "itinerary", m, mode], capture_output=True, text=True)
        return res.stdout
    elif cmd == "logistik":
        people = args[0] if args else "3"
        days = args[1] if len(args) > 1 else "2"
        res = subprocess.run([PYTHON3, "/root/itinerary_logistics.py", "logistics", people, days], capture_output=True, text=True)
        return res.stdout
    elif cmd == "survival":
        top = args[0] if args else "hipotermia"
        res = subprocess.run([PYTHON3, "/root/survival_budget.py", "survival", top], capture_output=True, text=True)
        return res.stdout
    elif cmd == "biaya":
        m = args[0] if args else "sumbing"
        g = args[1] if len(args) > 1 else "3"
        d = args[2] if len(args) > 2 else "2"
        res = subprocess.run([PYTHON3, "/root/survival_budget.py", "budget", m, g, d], capture_output=True, text=True)
        return res.stdout
    elif cmd == "porter":
        m = args[0] if args else "sumbing"
        res = subprocess.run([PYTHON3, "/root/porter_transport.py", m], capture_output=True, text=True)
        return res.stdout

if __name__ == "__main__":
    c = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "help"
    print(handle_command(c))
