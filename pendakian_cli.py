import sys
import re
import os
import subprocess
import os

# Owner User ID Check
OWNER_USER_ID = "606533609"
BOT_DIR = "/home/ubuntu/rutestrip-bot"
PYTHON_VENV = "/home/ubuntu/pendakian_env/bin/python"

VENV_PYTHON = "/home/ubuntu/rutestrip-bot/pendakian_env/bin/python"
PYTHON3 = "python3"
ALLOWED_COMMANDS = {
    "start", "help", "menu", "halo", "hi", "p",
    "info", "komunitas", "rekomendasi", "rekomendasi_rute", "gpx", "kml",
    "satelit", "satellite", "heatmap", "cuaca", "itinerary",
    "logistik", "biaya", "patungan", "split", "splitbill",
    "survival", "porter", "briefing", "voice",
    "infografis", "story", "card", "guidebook", "pdf"
}

# Blocked Sensitive / System Access Keywords & Commands for Public Users
BLOCKED_PATTERNS = [
    r'\.\./', r'/etc/', r'/var/', r'/proc/', r'/sys/', r'/root',
    r'sudo', r'rm\s', r'cat\s', r'chmod', r'chown', r'exec', r'eval',
    r'system', r'bash', r'sh\s', r'python', r'ls\s', r'pwd', r'docker', r'9router',
    r'tambah', r'edit', r'buat', r'modifikasi', r'update', r'bikin', r'install'
]

WELCOME_GUIDE = """🏔️ **MENU PANDUAN PENDAKIAN RUTESTRIP BOT** 🎒
*Asisten Pintar & Panduan Jalur Gunung di Pulau Jawa*

Silakan ketik kata kunci langsung (tanpa tanda `/`) untuk mengakses fitur:

---
### 🗺️ 1. INFORMASI & JALUR GUNUNG
• `info <nama_gunung>` ➔ Detail pos, rute & simaksi *(contoh: `info merbabu`)*
• `rekomendasi <kriteria>` ➔ Cari jalur via AI *(contoh: `rekomendasi pemula sabana`)*
• `briefing <nama_gunung>` ➔ Teks & Voice Note briefing ranger *(contoh: `briefing sumbing`)*
• `guidebook <nama_gunung>` / `pdf <nama_gunung>` ➔ Download E-Guidebook PDF resmi *(contoh: `pdf sumbing`)*

---
### 🌦️ 2. CUACA, NAVIGASI & PETA
• `cuaca [nama_gunung]` ➔ Live suhu, angin, hujan & indeks wind chill *(contoh: `cuaca slamet`)*
• `satelit [nama_gunung]` ➔ Peta citra satelit rute & pos *(contoh: `satelit arjuno`)*
• `heatmap [nama_gunung]` ➔ Peta kontur topografi elevasi 3D *(contoh: `heatmap merbabu`)*
• `gpx <nama_gunung>` / `kml <nama_gunung>` ➔ Download file navigasi GPS offline

---
### ⏱️ 3. ITINERARY & MANAJEMEN LOGISTIK
• `itinerary <gunung> [mode]` ➔ Estimasi waktu Naismith *(contoh: `itinerary sumbing 2d1n`)*
• `logistik <jumlah_orang> <jumlah_hari>` ➔ Kalkulator ransum & air *(contoh: `logistik 4 2`)*
• `biaya <gunung> <orang> <hari>` ➔ Estimasi total budget pendakian *(contoh: `biaya merbabu 3 2`)*
• `patungan <gunung> <orang> <hari>` ➔ Split bill & kas darurat tim

---
### 🆘 4. SURVIVAL & KONTAK BASECAMP
• `survival <topik>` ➔ Mitigasi hipotermia, AMS, & panduan darurat *(contoh: `survival hipotermia`)*
• `porter <nama_gunung>` ➔ Kontak basecamp, ojek & jasa porter resmi *(contoh: `porter sindoro`)*
• `story <nama_gunung>` / `infografis <nama_gunung>` ➔ Poster visual profil elevasi 9:16
• `komunitas` ➔ Link channel resmi & grup diskusi pendaki

---
💡 *Ketik `help` atau `menu` kapan saja untuk menampilkan kembali daftar ini.*"""

def sanitize_input(text: str) -> bool:
    for pat in BLOCKED_PATTERNS:
        if re.search(pat, text, re.IGNORECASE):
            return False
    return True

def handle_command(cmd_str: str):
    raw = cmd_str.strip()
    
    # 1. System Access & Sensitive Keyword Block
    if not sanitize_input(raw):
        return "⚠️ Akses Terbatas: Bot ini khusus melayani konsultasi informasi pendakian gunung di Pulau Jawa. Ketik `help` untuk daftar menu pendakian."
        
    clean = raw[1:] if raw.startswith('/') else raw
    parts = clean.split()
    if not parts:
        return WELCOME_GUIDE
    
    cmd = parts[0].lower()
    args = parts[1:]
    
    # 2. Strict Whitelist Enforcement for Public Users
    if cmd not in ALLOWED_COMMANDS:
        return f"⚠️ Perintah `{cmd}` tidak dikenali. Pengguna umum hanya dapat menggunakan fitur pendakian yang tersedia. Ketik `help` untuk daftar menu."

    if cmd in ["start", "help", "menu", "halo", "hi", "p"]:
        return WELCOME_GUIDE
    elif cmd in ["info", "komunitas"]:
        if args and cmd == "info":
            # Jika user meminta info spesifik gunung (misal: info merbabu)
            m = " ".join(args)
            res = subprocess.run([PYTHON_VENV if os.path.exists(PYTHON_VENV) else "python3", os.path.join(BOT_DIR, "rekomendasi_pendakian.py"), m], capture_output=True, text=True)
            if res.stdout.strip():
                return res.stdout.strip()
        res = subprocess.run(["python3", os.path.join(BOT_DIR, "info_rutestrip.py")], capture_output=True, text=True)
        return res.stdout.strip()
    elif cmd in ["briefing", "voice"]:
        m = args[0] if args else "merbabu"
        res = subprocess.run([PYTHON_VENV, os.path.join(BOT_DIR, "briefing_audio.py"), m], capture_output=True, text=True)
        txt = res.stdout.strip()
        return f"🎙️ **AUDIO & TEKS BRIEFING PENDAKIAN ({m.upper()})**\n\n📝 **Teks Briefing Ranger:**\n\"{txt}\"\n\n[[audio_as_voice]]\nMEDIA:/tmp/briefing_indonesia.ogg"
    elif cmd in ["satelit", "satellite", "topografi", "topo"]:
        q = args[0] if args else "sumbing"
        subprocess.run([PYTHON_VENV, os.path.join(BOT_DIR, "satellite_map.py"), q], capture_output=True, text=True)
        return "MEDIA:/tmp/satellite_map.png"
    elif cmd == "heatmap":
        q = args[0] if args else ""
        subprocess.run([PYTHON_VENV, os.path.join(BOT_DIR, "gpx_heatmap.py"), q], capture_output=True, text=True)
        return "MEDIA:/tmp/gpx_heatmap.png"
    elif cmd in ["gpx", "kml"]:
        q = " ".join(args) if args else "sumbing kaliangkrik"
        fmt = "kml" if cmd == "kml" else "gpx"
        res = subprocess.run(["python3", os.path.join(BOT_DIR, "gpx_exporter.py"), q, fmt], capture_output=True, text=True)
        out = res.stdout.strip()
        if out.startswith("GPX:") or out.startswith("KML:"):
            fpath = out.split(":", 1)[1]
            return f"MEDIA:{fpath}"
        return out
    elif cmd in ["rekomendasi", "rekomendasi_rute"]:
        query = " ".join(args) if args else "jalur landai ramah pemula"
        res = subprocess.run([PYTHON_VENV, os.path.join(BOT_DIR, "rekomendasi_pendakian.py"), query], capture_output=True, text=True)
        return res.stdout
    elif cmd == "cuaca":
        cmd_args = ["python3", os.path.join(BOT_DIR, "cek_cuaca_gunung.py")] + args
        res = subprocess.run(cmd_args, capture_output=True, text=True)
        return res.stdout
    elif cmd == "itinerary":
        m = args[0] if args else "sumbing"
        mode = args[1] if len(args) > 1 else "2d1n"
        res = subprocess.run(["python3", os.path.join(BOT_DIR, "itinerary_logistics.py"), "itinerary", m, mode], capture_output=True, text=True)
        return res.stdout
    elif cmd == "logistik":
        people = args[0] if args else "3"
        days = args[1] if len(args) > 1 else "2"
        res = subprocess.run(["python3", os.path.join(BOT_DIR, "itinerary_logistics.py"), "logistics", people, days], capture_output=True, text=True)
        return res.stdout
    elif cmd == "biaya":
        m = args[0] if args else "sumbing"
        g = args[1] if len(args) > 1 else "3"
        d = args[2] if len(args) > 2 else "2"
        res = subprocess.run(["python3", os.path.join(BOT_DIR, "survival_budget.py"), "budget", m, g, d], capture_output=True, text=True)
        return res.stdout
    elif cmd in ["patungan", "split", "splitbill"]:
        cmd_args = ["python3", os.path.join(BOT_DIR, "split_bill.py")] + args
        res = subprocess.run(cmd_args, capture_output=True, text=True)
        return res.stdout
    elif cmd in ["guidebook", "pdf"]:
        q = " ".join(args) if args else "sumbing"
        res = subprocess.run([PYTHON_VENV, os.path.join(BOT_DIR, "guidebook_pdf.py"), q], capture_output=True, text=True)
        out = res.stdout.strip()
        if out.startswith("GUIDEBOOK:"):
            fpath = out.split(":", 1)[1]
            return f"MEDIA:{fpath}"
        return out
    elif cmd == "survival":
        top = args[0] if args else "hipotermia"
        res = subprocess.run(["python3", os.path.join(BOT_DIR, "survival_budget.py"), "survival", top], capture_output=True, text=True)
        return res.stdout
    elif cmd == "porter":
        m = args[0] if args else "sumbing"
        res = subprocess.run(["python3", os.path.join(BOT_DIR, "porter_transport.py"), m], capture_output=True, text=True)
        return res.stdout
    elif cmd in ["infografis", "story", "card"]:
        q = " ".join(args) if args else "sumbing"
        res = subprocess.run([PYTHON_VENV, os.path.join(BOT_DIR, "story_infografis.py"), q], capture_output=True, text=True)
        out = res.stdout.strip()
        if out.startswith("STORY:"):
            fpath = out.split(":", 1)[1]
            return f"MEDIA:{fpath}"
        return out

if __name__ == "__main__":
    c = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "help"
    print(handle_command(c))
