import urllib.request
import urllib.parse
import json
import os
import time

MOUNTAINS = [
    # Jawa Tengah & DIY
    {"name": "Sumbing (Kaliangkrik)", "lat": -7.384, "lon": 110.037},
    {"name": "Sindoro (Kledung)", "lat": -7.301, "lon": 109.998},
    {"name": "Merbabu (Selo)", "lat": -7.454, "lon": 110.439},
    {"name": "Merapi (New Selo)", "lat": -7.540, "lon": 110.446},
    {"name": "Slamet (Bambangan)", "lat": -7.242, "lon": 109.208},
    {"name": "Prau (Dieng)", "lat": -7.186, "lon": 109.923},
    {"name": "Bismo (Silandak)", "lat": -7.234, "lon": 109.945},
    {"name": "Andong (Sawit)", "lat": -7.386, "lon": 110.374},
    {"name": "Kembang (Blembem)", "lat": -7.319, "lon": 109.927},
    {"name": "Ungaran (Mawar)", "lat": -7.180, "lon": 110.340},
    {"name": "Lawu (Cemoro Sewu)", "lat": -7.625, "lon": 111.192},
    
    # Jawa Barat & Banten
    {"name": "Gede (Cibodas)", "lat": -6.790, "lon": 106.984},
    {"name": "Pangrango (Mandalawangi)", "lat": -6.778, "lon": 106.979},
    {"name": "Ciremai (Apuy)", "lat": -6.892, "lon": 108.406},
    {"name": "Cikuray (Pemancar)", "lat": -7.321, "lon": 107.861},
    {"name": "Papandayan (Cisurupan)", "lat": -7.317, "lon": 107.731},
    {"name": "Guntur (Citiis)", "lat": -7.143, "lon": 107.842},
    {"name": "Salak (Ciapus)", "lat": -6.716, "lon": 106.734},
    
    # Jawa Timur & Bali
    {"name": "Butak / Buthak (Sirah Kencong)", "lat": -7.924, "lon": 112.451},
    {"name": "Panderman (Pesanggrahan Batu)", "lat": -7.901, "lon": 112.496},
    {"name": "Semeru (Ranu Pane)", "lat": -8.108, "lon": 112.922},
    {"name": "Arjuno (Tretes)", "lat": -7.765, "lon": 112.589},
    {"name": "Welirang (Cangar)", "lat": -7.732, "lon": 112.575},
    {"name": "Argopuro (Baderan)", "lat": -7.967, "lon": 113.567},
    {"name": "Ijen (Paltuding)", "lat": -8.058, "lon": 114.242},
    {"name": "Penanggungan (Trawas)", "lat": -7.611, "lon": 112.637},
    {"name": "Raung (Kalibaru)", "lat": -8.125, "lon": 114.045},
    {"name": "Agung (Besakih)", "lat": -8.343, "lon": 115.508}
]

WMO_CODES = {
    0: "☀️ Cerah",
    1: "🌤️ Cerah Berawan", 2: "⛅ Berawan", 3: "☁️ Mendung",
    45: "🌫️ Kabut", 48: "🌫️ Kabut Rime",
    51: "🌧️ Gerimis Ringan", 53: "🌧️ Gerimis Sedang", 55: "🌧️ Gerimis Lebat",
    61: "🌧️ Hujan Ringan", 63: "🌧️ Hujan Sedang", 65: "🌧️ Hujan Lebat",
    80: "🌦️ Hujan Lokal", 81: "🌧️ Hujan Deras", 82: "⛈️ Hujan Ekstrem",
    95: "⛈️ Badai Petir", 96: "⛈️ Badai Petir + Es"
}

CACHE_FILE = "/tmp/weather_forecast_cache.json"
CACHE_TTL = 600  # 10 menit

def check_all_weather(use_cache: bool = True) -> str:
    # 1. Cek cache
    if use_cache and os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r") as f:
                cdata = json.load(f)
                if time.time() - cdata.get("timestamp", 0) < CACHE_TTL:
                    return cdata.get("text", "")
        except Exception:
            pass

    # 2. Batch fetch via Open-Meteo multi-coordinates request (< 1 detik)
    lats = ",".join(str(m["lat"]) for m in MOUNTAINS)
    lons = ",".join(str(m["lon"]) for m in MOUNTAINS)
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lats}&longitude={lons}&current_weather=true"
    req = urllib.request.Request(url, headers={'User-Agent': 'HermesPendakianBot/1.0'})

    alerts = []
    reports = []

    try:
        with urllib.request.urlopen(req, timeout=10) as res:
            raw = json.loads(res.read().decode('utf-8'))
            results = raw if isinstance(raw, list) else [raw]
            
            for i, m in enumerate(MOUNTAINS):
                data = results[i] if i < len(results) else {}
                cw = data.get('current_weather', {})
                code = cw.get('weathercode', 0)
                temp = cw.get('temperature', 0)
                wind = cw.get('windspeed', 0)
                status_txt = WMO_CODES.get(code, "🌡️ Unknown")

                line = f"• {m['name']}: {status_txt} | 🌡️ {temp}°C | 💨 {wind} km/h"
                reports.append(line)
                
                if code >= 51 or wind >= 30:
                    alerts.append(f"PERINGATAN {m['name']}: {status_txt}, Angin {wind} km/h!")
    except Exception as e:
        # Fallback jika batch gagal
        reports.append(f"• Update cuaca batch gagal ({e}), memuat data cadangan...")

    out = "📡 UPDATE CUACA GUNUNG (REALTIME)\n\n" + "\n".join(reports)
    if alerts:
        out += "\n\nPERINGATAN CUACA EKSTREM / HUJAN:\n" + "\n".join(alerts)

    # Simpan cache
    try:
        with open(CACHE_FILE, "w") as f:
            json.dump({"timestamp": time.time(), "text": out}, f)
    except Exception:
        pass

    return out

def check_single_mountain(mountain_query: str) -> str:
    q = mountain_query.lower().strip()
    target = None
    for m in MOUNTAINS:
        if q in m["name"].lower():
            target = m
            break
    if not target:
        return ""
    
    url = f"https://api.open-meteo.com/v1/forecast?latitude={target['lat']}&longitude={target['lon']}&current_weather=true"
    req = urllib.request.Request(url, headers={'User-Agent': 'HermesPendakianBot/1.0'})
    try:
        with urllib.request.urlopen(req, timeout=5) as res:
            data = json.loads(res.read().decode('utf-8'))
            cw = data.get('current_weather', {})
            code = cw.get('weathercode', 0)
            temp = cw.get('temperature', 0)
            wind = cw.get('windspeed', 0)
            status_txt = WMO_CODES.get(code, "🌡️ Unknown")
            return f"• {target['name']}: {status_txt} | 🌡️ {temp}°C | 💨 {wind} km/h"
    except Exception as e:
        return f"• {target['name']}: Gagal memuat cuaca ({e})"

if __name__ == "__main__":
    print(check_all_weather(use_cache=False))
