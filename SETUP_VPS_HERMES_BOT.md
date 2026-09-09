# 🛠️ Panduan Lengkap Install RuteStrip Bot dari VPS Ubuntu s.d. Berjalan

Panduan step-by-step dari nol untuk menginstal **Hermes Agent** di VPS Linux (Ubuntu), mengonfigurasi Bot Telegram, serta mengaktifkan seluruh fitur AI, SBERT, Peta Satelit, Cronjob Cuaca, dan Audio Briefing **RuteStrip Pendakian Bot**.

---

## 📋 DAFTAR ISI
1. [Prasyarat & Spesifikasi VPS](#1-prasyarat--spesifikasi-vps)
2. [Langkah 1: Update & Install Dependensi System (Linux & Python)](#langkah-1-update--install-dependensi-system-linux--python)
3. [Langkah 2: Install Hermes Agent](#langkah-2-install-hermes-agent)
4. [Langkah 3: Konfigurasi Bot Telegram di Hermes](#langkah-3-konfigurasi-bot-telegram-di-hermes)
5. [Langkah 4: Clone Repository & Setup Virtual Environment (uv)](#langkah-4-clone-repository--setup-virtual-environment-uv)
6. [Langkah 5: Pemasangan Custom Skill & Backend Routing](#langkah-5-pemasangan-custom-skill--backend-routing)
7. [Langkah 6: Aktifkan Automated Weather Monitoring (Cronjob)](#langkah-6-aktifkan-automated-weather-monitoring-cronjob)
8. [Langkah 7: Pengujian & Verifikasi Fitur](#langkah-7-pengujian--verifikasi-fitur)

---

## 1. Prasyarat & Spesifikasi VPS

* **OS Recommended:** Ubuntu 22.04 LTS atau 24.04 LTS (64-bit).
* **Minimal Specs:** 1 vCPU, 2 GB RAM, 10 GB Disk Space.
* **Recommended Specs:** 2 vCPU, 4 GB RAM (agar pemrosesan SBERT & Peta Satelit lebih kencang).
* **Akses:** Akses `root` atau `sudo` via SSH.

---

## Langkah 1: Update & Install Dependensi System (Linux & Python)

Jalankan perintah berikut di terminal VPS untuk menginstall `git`, `ffmpeg` (untuk audio voice note), `curl`, dan package builder:

```bash
# Update package list & upgrade system
sudo apt update && sudo apt upgrade -y

# Install dependensi sistem dasar & ffmpeg
sudo apt install -y git curl wget ffmpeg build-essential python3 python3-pip python3-venv

# Install `uv` (Fast Python Package Installer)
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.cargo/env
```

Verifikasi installasi `uv` dan `ffmpeg`:
```bash
uv --version
ffmpeg -version
```

---

## Langkah 2: Install Hermes Agent

Hermes Agent adalah framework AI agentic yang mendasari bot ini.

```bash
# Install Hermes Agent secara global
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash

# Atau via python pip/uv jika menggunakan venv
pip install hermes-agent
```

Verifikasi Hermes Agent:
```bash
hermes --version
```

---

## Langkah 3: Konfigurasi Bot Telegram di Hermes

1. Dapatkan Bot Token dari **@BotFather** di Telegram:
   - Ketik `/newbot` di Telegram @BotFather.
   - Beri nama bot: `RuteStrip Pendakian Bot`.
   - Simpan Token HTTP API yang diberikan (misal: `123456789:ABCdefGHIjklMNO...`).

2. Buka dan edit file konfigurasi Hermes (`~/.hermes/config.yaml`):

```bash
nano ~/.hermes/config.yaml
```

3. Isikan token Telegram & Provider AI pilihan Anda:

```yaml
telegram:
  bot_token: "123456789:ABCdefGHIjklMNO..."  # Ganti dengan token dari @BotFather
  enabled: true

# Konfigurasi Provider Model AI (OpenAI / Anthropic / Custom API)
custom_providers:
  name: "DasRams"
  base_url: "https://omni.peenjeee.tech/v1"
  key_env: "HERMES_CUSTOM_API_KEY"
  model: "antigravity/gemini-3.6-flash-medium"
```

---

## Langkah 4: Clone Repository & Setup Virtual Environment (uv)

```bash
# Clone repository project dari GitLab
cd /root
git clone https://gitlab.com/[REDACTED]/rutestrip-bot.git
cd rutestrip-bot

# Buat virtual environment bernama `pendakian_env`
uv venv pendakian_env

# Install seluruh dependensi AI & PyTorch (CPU)
uv pip install --python pendakian_env torch torchaudio --index-url https://download.pytorch.org/whl/cpu
uv pip install --python pendakian_env -r requirements.txt
```

---

## Langkah 5: Pemasangan Custom Skill & Backend Routing

Bot menggunakan Custom Skill `pendakian-jawa` agar Hermes mengetahui prosedur pengolahan perintah tanpa memerlukan tanda `/`.

```bash
# Buat direktori skills di Hermes
mkdir -p ~/.hermes/skills/pendakian-jawa

# Copy file SKILL.md ke folder skills Hermes
cp /root/rutestrip-bot/skills/pendakian-jawa/SKILL.md ~/.hermes/skills/pendakian-jawa/SKILL.md

# Copy script cuaca ke direktori script Hermes (untuk Cronjob)
mkdir -p ~/.hermes/scripts
cp /root/rutestrip-bot/cek_cuaca_gunung.py ~/.hermes/scripts/cek_cuaca_gunung.py
```

---

## Langkah 6: Aktifkan Automated Weather Monitoring (Cronjob)

Bot dilengkapi pemantau cuaca otomatis yang mengecek 7 gunung utama Pulau Jawa setiap 3 jam sekali dan mengirimkan peringatan dini jika terjadi hujan/badai:

```bash
# Buat scheduled job di Hermes
hermes cronjob create \
  --name "monitoring-cuaca-gunung" \
  --schedule "every 3h" \
  --script "cek_cuaca_gunung.py" \
  --prompt "Laporkan hasil update cuaca dari script ke chat ini secara ringkas." \
  --deliver "origin"
```

---

## Langkah 7: Pengujian & Verifikasi Fitur

Jalankan Hermes Gateway / Telegram Daemon:

```bash
hermes start
```

### 📱 Tes Kata Kunci di Chat Telegram:

1. **Onboarding / Help:**
   Ketik `help` atau `start` ➔ Bot menampilkan menu 11 Navigasi Utama.
2. **Rekomendasi Rute AI:**
   Ketik `rekomendasi jalur landai pemula` ➔ Bot mengeksekusi SBERT Cosine Sim & memberikan rute terbaik.
3. **Peta Citra Satelit:**
   Ketik `satelit sumbing` ➔ Bot mengirimkan gambar peta citra satelit `Esri World Imagery` + jalur GPX.
4. **Export GPX / KML:**
   Ketik `gpx sumbing` / `kml merbabu` ➔ Bot mengirimkan file track peta offline.
5. **Dual Briefing (Teks + Voice Note):**
   Ketik `briefing merbabu` ➔ Bot mengirimkan teks rangkuman & voice note berlogat Ranger Indonesia (`id-ID-ArdiNeural`).
6. **Cuaca Realtime:**
   Ketik `cuaca prau` ➔ Bot menampilkan suhu, kecepatan angin, & status BMKG/Open-Meteo.
7. **Itinerary Naismith:**
   Ketik `itinerary sumbing 2d1n` ➔ Bot menampilkan timeline estimasi jam per pos.
8. **Kalkulator Logistik & Biaya:**
   Ketik `logistik 4 2` atau `biaya sumbing 4 2` ➔ Bot menampilkan estimasi kebutuhan & budget.
9. **Survival & Porter Directory:**
   Ketik `survival hipotermia` atau `porter sumbing` ➔ Bot menampilkan panduan darurat & kontak basecamp.

---

🎉 **Selamat! RuteStrip Pendakian Bot telah 100% aktif dan siap digunakan di VPS Anda!**
