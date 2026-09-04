import urllib.request
import json

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

def check_all_weather():
    alerts = []
    reports = []
    
    for m in MOUNTAINS:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={m['lat']}&longitude={m['lon']}&current_weather=true"
        req = urllib.request.Request(url, headers={'User-Agent': 'HermesPendakianBot/1.0'})
        try:
            with urllib.request.urlopen(req, timeout=5) as res:
                data = json.loads(res.read().decode('utf-8'))
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
            reports.append(f"• {m['name']}: Gagal load ({e})")
            
    out = "📡 UPDATE CUACA GUNUNG (REALTIME)\n\n" + "\n".join(reports)
    if alerts:
        out += "\n\nPERINGATAN CUACA EKSTREM / HUJAN:\n" + "\n".join(alerts)
    return out

if __name__ == "__main__":
    print(check_all_weather())
