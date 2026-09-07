# 📚 Dokumentasi Lengkap REST API RuteStrip Pendakian & WebChat AI

Selamat datang di dokumentasi resmi **RuteStrip Pendakian REST API (v1.7.0)**. API ini menyediakan layanan kecerdasan buatan untuk pendakian gunung di Indonesia (khususnya Pulau Jawa & Bali), prakiraan cuaca realtime, analisis data GPX/KML, kalkulator logistik Naismith, sistem autentikasi pengguna, serta manajemen riwayat obrolan multi-sesi dengan arsitektur penyimpanan **PostgreSQL & Dual-Write JSON Fallback**.

---

## 📌 Informasi Dasar & Base URL

* **Base URL Production:** `https://airutestrip.web.id`
* **Direct VPS Endpoint:** `http://188.166.224.148:8000`
* **Interactive Swagger UI:** `http://188.166.224.148:8000/docs`
* **OpenAPI Specification:** `http://188.166.224.148:8000/openapi.json`
* **Content-Type:** `application/json` (kecuali endpoint file/peta: `image/png`, `application/gpx+xml`, `application/vnd.google-earth.kml+xml`)

---

## 🗄️ Arsitektur Database: PostgreSQL & High-Availability Fallback

Sistem backend RuteStrip mengimplementasikan arsitektur database bertingkat untuk menjamin ketersediaan data 100% (*High Availability & Fault Tolerance*):

1. **Primary Storage (PostgreSQL):**
   * **Database Name:** `rutestrip`
   * **Tabel Utama:**
     * `users`: Menyimpan profil pengguna, hash password SHA-256, email, dan token sesi.
     * `chat_sessions`: Menyimpan riwayat percakapan per session ID dan pesan interaktif antara pengguna dan asisten AI.
     * `subscribers`: Data pelanggan aktif Telegram Bot (DM dan Komunitas).
     * `reviews`: Ulasan, rating kesulitan jalur, estimasi waktu, dan sumber air dari para pendaki.
2. **Fallback & Dual-Write Local JSON:**
   * Jika terjadi gangguan koneksi database (`[PG ERROR]`), sistem secara otomatis beralih (*graceful fallback*) ke berkas JSON lokal (`users_auth.json`, `users_chat_sessions.json`, `subscribers.json`, `reviews.json`).
   * Operasi baca dan tulis tetap berjalan tanpa membuat pengguna mengalami *downtime* atau *internal server error*.

---

## 🔐 Autentikasi & Otorisasi

Sebagian besar endpoint chat dan profil pengguna memerlukan otentikasi berbasis **Bearer Token**:

```http
Authorization: Bearer rutestrip_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

Token ini diperoleh dari endpoint `/api/auth/login` atau `/api/auth/register`.

---

## 📑 Daftar Endpoint REST API

### 1. Layanan Autentikasi & Akun Pengguna

#### a. Registrasi Akun Baru
* **Endpoint:** `POST /api/auth/register`
* **Deskripsi:** Mendaftarkan pengguna baru ke database WebChat AI.
* **Request Body:**
  ```json
  {
    "username": "pendakigunung",
    "email": "pendaki@example.com",
    "password": "PasswordKuat123!",
    "full_name": "Pendaki Sejati"
  }
  ```
* **Response (200 OK):**
  ```json
  {
    "status": "success",
    "message": "Registrasi berhasil!",
    "user": {
      "user_id": "b6dcdb66-44c5-41a6-8405-b8717f28e774",
      "username": "pendakigunung",
      "email": "pendaki@example.com",
      "full_name": "Pendaki Sejati",
      "token": "rutestrip_ecb6fda31b0daff8939e252705558a88"
    }
  }
  ```

#### b. Login Pengguna
* **Endpoint:** `POST /api/auth/login`
* **Deskripsi:** Masuk menggunakan username atau email untuk mendapatkan token autentikasi.
* **Request Body:**
  ```json
  {
    "username_or_email": "pendakigunung",
    "password": "PasswordKuat123!"
  }
  ```
* **Response (200 OK):**
  ```json
  {
    "status": "success",
    "message": "Login berhasil!",
    "user": {
      "user_id": "b6dcdb66-44c5-41a6-8405-b8717f28e774",
      "username": "pendakigunung",
      "email": "pendaki@example.com",
      "full_name": "Pendaki Sejati",
      "token": "rutestrip_a139a44787765b244d9a22f91298fdca"
    }
  }
  ```

#### c. Reset Password
* **Endpoint:** `POST /api/auth/reset-password`
* **Deskripsi:** Memperbarui password akun terdaftar.
* **Request Body:**
  ```json
  {
    "username_or_email": "pendaki@example.com",
    "new_password": "PasswordBaru456!"
  }
  ```
* **Response (200 OK):**
  ```json
  {
    "status": "success",
    "message": "Password berhasil diperbarui."
  }
  ```

#### d. Verifikasi Token & Profil (`/me`)
* **Endpoint:** `GET /api/auth/me`
* **Headers:** `Authorization: Bearer <token>`
* **Response (200 OK):**
  ```json
  {
    "status": "success",
    "valid": true,
    "user": {
      "user_id": "b6dcdb66-44c5-41a6-8405-b8717f28e774",
      "username": "pendakigunung",
      "email": "pendaki@example.com",
      "full_name": "Pendaki Sejati"
    }
  }
  ```

---

### 2. Layanan WebChat AI & Multi-Session Chat History

#### a. Kirim Prompt AI (Guardrail + SBERT Routing)
* **Endpoint:** `POST /api/chat/query`
* **Headers:** `Authorization: Bearer <token>` *(opsional, untuk mengikat chat ke user ID)*
* **Request Body:**
  ```json
  {
    "prompt": "Rekomendasi gunung di Jawa Tengah untuk pemula dengan pemandangan sabana indah",
    "session_id": "optional-uuid-v4-session-id"
  }
  ```
* **Response (200 OK):**
  ```json
  {
    "status": "success",
    "guardrail_passed": true,
    "session_id": "c76a911e-085e-4b68-b7ce-737609204fa6",
    "query": "Rekomendasi gunung di Jawa Tengah untuk pemula dengan pemandangan sabana indah",
    "recommendations": [
      {
        "mountain_route": "Gunung Merbabu via Selo",
        "stats": { "distance_km": 11.2, "elevation_gain_m": 1280, "est_time_hours": "6-8 jam" },
        "narrative": "Jalur Selo menyajikan pemandangan padang sabana luas dan pos camping yang tertata rapi..."
      }
    ],
    "response": "Berikut adalah informasi pendakian terbaik berdasarkan kriteria..."
  }
  ```

#### b. Ambil Daftar Sesi Chat Pengguna
* **Endpoint:** `GET /api/chat/sessions`
* **Headers:** `Authorization: Bearer <token>`
* **Response (200 OK):**
  ```json
  {
    "status": "success",
    "user_id": "b6dcdb66-44c5-41a6-8405-b8717f28e774",
    "total_sessions": 2,
    "sessions": [
      {
        "session_id": "c76a911e-085e-4b68-b7ce-737609204fa6",
        "title": "Rekomendasi gunung di Jawa Tengah...",
        "created_at": "2026-09-07T10:15:00Z",
        "updated_at": "2026-09-07T10:18:22Z",
        "message_count": 4
      }
    ]
  }
  ```

#### c. Ambil Riwayat Percakapan dalam Satu Sesi
* **Endpoint:** `GET /api/chat/sessions/{session_id}`
* **Headers:** `Authorization: Bearer <token>`
* **Response (200 OK):**
  ```json
  {
    "status": "success",
    "user_id": "b6dcdb66-44c5-41a6-8405-b8717f28e774",
    "session_id": "c76a911e-085e-4b68-b7ce-737609204fa6",
    "total_messages": 2,
    "messages": [
      { "sender": "user", "text": "Rekomendasi gunung...", "timestamp": "2026-09-07T10:15:00Z" },
      { "sender": "bot", "text": "Berikut rekomendasi...", "timestamp": "2026-09-07T10:15:02Z" }
    ]
  }
  ```

#### d. Hapus Satu Sesi Chat Spesifik
* **Endpoint:** `DELETE /api/chat/sessions/{session_id}`
* **Headers:** `Authorization: Bearer <token>`
* **Response (200 OK):**
  ```json
  {
    "status": "success",
    "message": "Sesi percakapan c76a911e-085e-4b68-b7ce-737609204fa6 berhasil dihapus."
  }
  ```

#### e. Bersihkan Seluruh Riwayat Chat Pengguna
* **Endpoint:** `DELETE /api/chat/history`
* **Headers:** `Authorization: Bearer <token>`
* **Response (200 OK):**
  ```json
  {
    "status": "success",
    "message": "Seluruh riwayat percakapan berhasil dibersihkan."
  }
  ```

---

### 3. Layanan Rekomendasi Rute & Navigasi Gunung

#### a. Rekomendasi AI Semantik (SBERT Embeddings)
* **Endpoint:** `GET /api/rekomendasi`
* **Query Parameters:**
  * `query` (string, wajib): Kata kunci preferensi pendakian (contoh: `tektok pemula pemandangan indah`)
  * `limit` (int, opsional, default: 5): Jumlah hasil maksimal
* **Response (200 OK):**
  ```json
  {
    "query": "tektok pemula",
    "total": 3,
    "results": [
      {
        "mountain_route": "Andong via Sawit",
        "similarity_score": 0.8912,
        "stats": { "elevation_masl": 1726, "distance_km": 4.5, "est_time_hours": "2-3 jam" },
        "narrative": "Sangat ideal untuk pemula dan tektok santai dengan jalur yang jelas..."
      }
    ]
  }
  ```

#### b. Prakiraan Cuaca Live Real-Time (Open-Meteo Integration)
* **Endpoint:** `GET /api/cuaca`
* **Query Parameters:**
  * `mountain` (string, opsional): Nama gunung tertentu (contoh: `merbabu`, `prau`, `semeru`). Kosongkan untuk seluruh gunung.
* **Response (200 OK):**
  ```json
  {
    "mountain": "merbabu",
    "weather_info": [
      "• Merbabu (Selo): ☀️ Cerah | 🌡️ 14.1°C | 💨 2.8 km/h"
    ]
  }
  ```

#### c. Export File Peta Satelit & Topografi (PNG)
* **Endpoint:** `GET /api/map/satellite`
* **Query Parameters:**
  * `mountain` (string, opsional, default: `merbabu`): Nama gunung
  * `map_type` (string, opsional, default: `satelit`): `satelit` atau `topografi`
* **Response:** File gambar berformat `image/png` dengan plot kontur elevasi.

#### d. Download GPX & KML Track Offline
* **Endpoint:** `GET /api/gpx`
* **Query Parameters:**
  * `mountain` (string, opsional, default: `merbabu`): Nama gunung
  * `format` (string, opsional, default: `gpx`): `gpx` atau `kml`
* **Response:** Berkas unduhan GPX/KML siap impor ke Garmin, Avenza Maps, Locus Map, atau Google Earth.

---

### 4. Layanan Logistik, Itinerary & Survival

#### a. Naismith Rule Itinerary Generator
* **Endpoint:** `GET /api/itinerary`
* **Query Parameters:**
  * `mountain` (string, default: `merbabu`): Nama gunung
  * `mode` (string, default: `2d1n`): `tektok` atau `2d1n`
* **Response (200 OK):**
  ```json
  {
    "mountain": "merbabu",
    "mode": "2d1n",
    "itinerary": "Rencana Pendakian Merbabu (2D1N):\nHari 1: Basecamp Selo ke Pos 3/Sabana 1...\nHari 2: Summit Attack jam 04:00..."
  }
  ```

#### b. Kalkulator Ransum Air & Makanan
* **Endpoint:** `GET /api/logistik`
* **Query Parameters:**
  * `people` (int, default: 3): Jumlah anggota tim
  * `days` (int, default: 2): Durasi pendakian (hari)
* **Response (200 OK):**
  ```json
  {
    "people": 3,
    "days": 2,
    "logistics": "Estimasi Kebutuhan Logistik (3 orang, 2 hari):\n• Air Minum: 18 Liter (3L/orang/hari)\n• Beras: 1.8 kg..."
  }
  ```

#### c. Kalkulator Estimasi Biaya
* **Endpoint:** `GET /api/biaya`
* **Query Parameters:**
  * `mountain` (string, default: `sumbing`)
  * `people` (int, default: 3)
  * `days` (int, default: 2)
* **Response (200 OK):**
  ```json
  {
    "mountain": "sumbing",
    "people": 3,
    "days": 2,
    "budget_info": "Estimasi Rincian Biaya Pendakian Sumbing:\n• Tiket Simaksi: Rp 35.000 x 3\n• Ojek Basecamp: Rp 30.000 x 3..."
  }
  ```

#### d. Panduan Penanganan Darurat (Survival & First Aid)
* **Endpoint:** `GET /api/survival`
* **Query Parameters:**
  * `topic` (string, default: `hipotermia`): `hipotermia`, `ams`, `tersesat`, `patah_tulang`, `dehidrasi`, dll.
* **Response (200 OK):**
  ```json
  {
    "topic": "hipotermia",
    "guide": "Protokol Penanganan Hipotermia di Lapangan:\n1. Lindungi korban dari angin dan hujan\n2. Ganti pakaian basah dengan pakaian kering..."
  }
  ```

#### e. Kontak Porter, Transportasi & Basecamp
* **Endpoint:** `GET /api/porter`
* **Query Parameters:**
  * `mountain` (string, default: `sumbing`): Nama gunung
* **Response (200 OK):**
  ```json
  {
    "mountain": "sumbing",
    "porter_info": "Informasi Basecamp & Layanan Porter Gunung Sumbing:\n• Basecamp Garung: 0812-xxxx-xxxx\n• Basecamp Bowongso: 0813-xxxx-xxxx..."
  }
  ```

---

### 5. Informasi Komunitas & Statistik

* **`GET /api/info`**: Link resmi website, WebChat, channel, dan grup komunitas.
* **`GET /api/news/bulletin`**: Buletin ringkasan berita gunung harian.
* **`GET /api/getaway`**: Ide liburan dan pendakian santai akhir pekan.
* **`GET /api/survival/tips`**: Tips edukasi outdoor dan etika pendakian.
* **`GET /api/stats/subscribers`**: Data metrik jumlah pelanggan Telegram Bot & WebChat terdaftar.

---

## 💻 Contoh Penggunaan via cURL

### 1. Registrasi & Login
```bash
# Registrasi Akun
curl -X POST "https://airutestrip.web.id/api/auth/register" \
     -H "Content-Type: application/json" \
     -d '{"username": "arief", "email": "arief@rutestrip.web.id", "password": "securepassword"}'

# Login Akun
curl -X POST "https://airutestrip.web.id/api/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"username_or_email": "arief", "password": "securepassword"}'
```

### 2. Mengirim Prompt ke WebChat AI
```bash
curl -X POST "https://airutestrip.web.id/api/chat/query" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer rutestrip_YOUR_TOKEN_HERE" \
     -d '{"prompt": "Gunung apa yang cocok untuk pemula di Jawa Barat?"}'
```

### 3. Mengambil Prakiraan Cuaca
```bash
curl -X GET "https://airutestrip.web.id/api/cuaca?mountain=merbabu"
```

---

## 🛡️ Response Codes & Error Handling

* **`200 OK`**: Permintaan berhasil diproses.
* **`400 Bad Request`**: Parameter tidak valid atau kolom wajib belum diisi.
* **`401 Unauthorized`**: Token autentikasi tidak valid, kedaluwarsa, atau header tidak disertakan.
* **`404 Not Found`**: Jalur gunung atau berkas tidak ditemukan di sistem.
* **`500 Internal Server Error`**: Gangguan server (otomatis memicu dual-write backup fallback).
