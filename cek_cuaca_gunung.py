import urllib.request
import json

MOUNTAINS = [
    {"name": "Sumbing (Kaliangkrik)", "lat": -7.384, "lon": 110.037},
    {"name": "Gede (Cibodas)", "lat": -6.790, "lon": 106.984},
    {"name": "Merbabu (Selo)", "lat": -7.454, "lon": 110.439},
    {"name": "Prau (Dieng)", "lat": -7.186, "lon": 109.923},
    {"name": "Ciremai (Apuy)", "lat": -6.892, "lon": 108.406},
    {"name": "Slamet (Bambangan)", "lat": -7.242, "lon": 109.208},
    {"name": "Semeru (Ranu Pane)", "lat": -8.108, "lon": 112.922},
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

                line = f"• **{m['name']}**: {status_txt} | 🌡️ {temp}°C | 💨 {wind} km/h"
                reports.append(line)
                
                # Check alert condition (rain/thunderstorm/high wind > 30km/h)
                if code >= 51 or wind >= 30:
                    alerts.append(f"⚠️ **PERINGATAN {m['name']}**: {status_txt}, Angin {wind} km/h!")
        except Exception as e:
            reports.append(f"• **{m['name']}**: Gagal load ({e})")
            
    out = "📡 **UPDATE CUACA GUNUNG (TIAP 3 JAM)**\n\n" + "\n".join(reports)
    if alerts:
        out += "\n\n🚨 **PERINGATAN CUACA EKSTREM / HUJAN:**\n" + "\n".join(alerts)
    return out

if __name__ == "__main__":
    print(check_all_weather())
