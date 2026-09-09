import sys
import json
import urllib.request

MOUNTAINS = [
    {"id": "sumbing", "name": "Sumbing (Kaliangkrik)", "peak_elev": 3371, "lat": -7.384, "lon": 110.037},
    {"id": "merbabu", "name": "Merbabu (Selo)", "peak_elev": 3145, "lat": -7.454, "lon": 110.439},
    {"id": "prau", "name": "Prau (Dieng)", "peak_elev": 2590, "lat": -7.186, "lon": 109.923},
    {"id": "sindoro", "name": "Sindoro (Kledung)", "peak_elev": 3153, "lat": -7.301, "lon": 109.998},
    {"id": "slamet", "name": "Slamet (Bambangan)", "peak_elev": 3432, "lat": -7.242, "lon": 109.208},
    {"id": "lawu", "name": "Lawu (Cemoro Sewu)", "peak_elev": 3265, "lat": -7.628, "lon": 111.192},
    {"id": "gede", "name": "Gede (Cibodas)", "peak_elev": 2958, "lat": -6.790, "lon": 106.984},
    {"id": "ciremai", "name": "Ciremai (Apuy)", "peak_elev": 3078, "lat": -6.892, "lon": 108.406},
    {"id": "papandayan", "name": "Papandayan (Garut)", "peak_elev": 2665, "lat": -7.319, "lon": 107.731},
    {"id": "semeru", "name": "Semeru (Ranu Pane)", "peak_elev": 3676, "lat": -8.108, "lon": 112.922},
    {"id": "arjuno", "name": "Arjuno-Welirang (Tretes)", "peak_elev": 3339, "lat": -7.766, "lon": 112.589},
    {"id": "raung", "name": "Raung (Kalibaru)", "peak_elev": 3344, "lat": -8.125, "lon": 114.045}
]

WMO_CODES = {
    0: "☀️ Cerah",
    1: "🌤️ Cerah Berawan", 2: "⛅ Berawan", 3: "☁️ Mendung",
    45: "🌫️ Kabut", 48: "🌫️ Kabut Tebal/Rime",
    51: "🌧️ Gerimis Ringan", 53: "🌧️ Gerimis Sedang", 55: "🌧️ Gerimis Lebat",
    61: "🌧️ Hujan Ringan", 63: "🌧️ Hujan Sedang", 65: "🌧️ Hujan Lebat",
    80: "🌦️ Hujan Lokal", 81: "🌧️ Hujan Deras", 82: "⛈️ Hujan Ekstrem",
    95: "⛈️ Badai Petir", 96: "⛈️ Badai Petir + Es"
}

def calculate_wind_chill(temp_c: float, wind_kmh: float) -> float:
    """Menghitung Wind Chill (Suhu Terasa Riil Tubuh) berdasarkan NOAA/Siple Formula."""
    if temp_c <= 10.0 and wind_kmh > 4.8:
        v_pow = wind_kmh ** 0.16
        twc = 13.12 + (0.6215 * temp_c) - (11.37 * v_pow) + (0.3965 * temp_c * v_pow)
        return round(twc, 1)
    else:
        effective_temp = temp_c - (wind_kmh * 0.08)
        return round(effective_temp, 1)

def get_hypothermia_assessment(temp_c: float, wind_kmh: float, weather_code: int):
    """Menilai indeks risiko hipotermia, sistem layering pakaian, dan mitigasi keselamatan."""
    feels_like = calculate_wind_chill(temp_c, wind_kmh)
    is_rain = weather_code >= 51
    is_extreme_rain = weather_code in [65, 81, 82, 95, 96]
    
    if feels_like <= 2.0 or (feels_like <= 6.0 and is_rain) or is_extreme_rain:
        status_code = "EXTREME"
        level = "🚨 BAHAYA EKSTREM (Risiko Hipotermia Akut)"
        layering = "• Wajib 3+ Layer: Base layer thermal (quick-dry/merino) + Mid layer (fleece/down jacket) + Outer waterproof/windproof.\n• Aksesoris wajib: Kupluk/beanie polar, sarung tangan polar/waterproof, kaos kaki wol cadangan kering.\n• Pantangan keras: JANGAN biarkan pakaian basah menempel di tubuh saat berhenti/istirahat."
        safe_action = "Potensi drop suhu drastis! Segera pasang shelter/tenda bila basah kuyup, konsumsi makanan kalori tinggi dan minuman hangat."
    elif feels_like <= 8.0 or (feels_like <= 12.0 and is_rain):
        status_code = "HIGH"
        level = "⚠️ WASPADA TINGGI (Risiko Hipotermia Sedang-Tinggi)"
        layering = "• Wajib 2-3 Layer: Base layer breathable + Jaket Insulasi (Fleece/Windbreaker tebal) + Siapkan Jas Hujan/Outer waterproof.\n• Aksesoris: Buff/kupluk dan sarung tangan polar."
        safe_action = "Ganti pakaian basah sebelum masuk sleeping bag, jangan tidur dengan pakaian lembap."
    elif feels_like <= 14.0:
        status_code = "MODERATE"
        level = "🟡 WASPADA RINGAN (Sejuk - Dingin)"
        layering = "• 2 Layer: Kaos trekking sintetis + Jaket Windbreaker/Gunung saat istirahat atau camp malam."
        safe_action = "Kenakan jaket windbreaker saat berhenti istirahat agar angin tidak menyerap panas tubuh."
    else:
        status_code = "SAFE"
        level = "🟢 AMAN (Risiko Rendah / Nyaman)"
        layering = "• 1-2 Layer: Pakaian trekking standar yang nyaman dan menyerap keringat."
        safe_action = "Jaga hidrasi tubuh secara berkala selama perjalanan."
        
    return {
        "status_code": status_code,
        "feels_like": feels_like,
        "level": level,
        "layering": layering,
        "safe_action": safe_action
    }

def fetch_weather(m: dict) -> dict:
    url = f"https://api.open-meteo.com/v1/forecast?latitude={m['lat']}&longitude={m['lon']}&current_weather=true&hourly=precipitation,relativehumidity_2m"
    req = urllib.request.Request(url, headers={'User-Agent': 'HermesPendakianBot/2.0'})
    try:
        with urllib.request.urlopen(req, timeout=6) as res:
            data = json.loads(res.read().decode('utf-8'))
            cw = data.get('current_weather', {})
            code = cw.get('weathercode', 0)
            temp = float(cw.get('temperature', 0))
            wind = float(cw.get('windspeed', 0))
            
            # Get current humidity if available
            hourly = data.get('hourly', {})
            humidity_list = hourly.get('relativehumidity_2m', [])
            humidity = humidity_list[0] if humidity_list else 80
            
            hypo = get_hypothermia_assessment(temp, wind, code)
            return {
                "success": True,
                "name": m["name"],
                "elev": m.get("peak_elev", 3000),
                "temp": temp,
                "wind": wind,
                "humidity": humidity,
                "weather_code": code,
                "weather_desc": WMO_CODES.get(code, "🌡️ Cerah"),
                "hypo": hypo
            }
    except Exception as e:
        return {"success": False, "name": m["name"], "error": str(e)}

def format_detailed_weather(res: dict) -> str:
    if not res["success"]:
        return f"❌ Gagal memuat data cuaca untuk {res['name']}: {res.get('error')}"
    
    h = res["hypo"]
    out = [
        f"🏔️ **ANALISIS CUACA & RISIKO HIPOTERMIA - {res['name'].upper()}**",
        f"📍 Elevasi Puncak: ~{res['elev']} mdpl\n",
        f"📊 **Kondisi Udara Terkini:**",
        f"• Cuaca: {res['weather_desc']}",
        f"• Suhu Terukur: {res['temp']}°C",
        f"• Kecepatan Angin: {res['wind']} km/h",
        f"• Kelembapan Udara: {res['humidity']}%\n",
        f"🥶 **Kalkulator Wind Chill & Sensasi Dingin:**",
        f"• **Suhu Riil Terasa Tubuh (Wind Chill): {h['feels_like']}°C**",
        f"• **Status Risiko: {h['level']}**\n",
        f"🧥 **Rekomendasi Layering Pakaian:**",
        f"{h['layering']}\n",
        f"🛡️ **Protokol Keselamatan:**",
        f"{h['safe_action']}"
    ]
    return "\n".join(out)

def format_all_weather_summary() -> str:
    reports = []
    alerts = []
    
    for m in MOUNTAINS:
        res = fetch_weather(m)
        if res["success"]:
            h = res["hypo"]
            line = f"• **{res['name']}**: {res['weather_desc']} | 🌡️ {res['temp']}°C (Terasa {h['feels_like']}°C) | 💨 {res['wind']} km/h"
            reports.append(line)
            
            if h["status_code"] in ["EXTREME", "HIGH"] or res["wind"] >= 30 or res["weather_code"] >= 51:
                alerts.append(f"⚠️ **{res['name']}**: {res['weather_desc']}, Angin {res['wind']} km/h, Terasa {h['feels_like']}°C ➔ {h['level']}")
        else:
            reports.append(f"• **{m['name']}**: Gagal load data")
            
    out = [
        "📡 **UPDATE LIVE CUACA GUNUNG & INDEKS WIND CHILL**",
        "*(Data realtime Open-Meteo per 3 Jam)*\n",
        "\n".join(reports)
    ]
    
    if alerts:
        out.append("\n🚨 **PERINGATAN ANGIN KENCANG / HIPOTERMIA / HUJAN:**")
        out.append("\n".join(alerts))
        
    out.append("\n💡 *Tips: Ketik `cuaca <nama_gunung>` (contoh: `cuaca sumbing`) untuk analisis detail layering & mitigasi.*")
    return "\n".join(out)

def check_all_weather(mountain: str = None) -> str:
    if mountain:
        q = mountain.lower().strip()
        for m in MOUNTAINS:
            if q in m["id"] or q in m["name"].lower():
                res = fetch_weather(m)
                return format_detailed_weather(res)
    return format_all_weather_summary()

def main():
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:]).lower()
        matched = None
        for m in MOUNTAINS:
            if query in m["id"] or query in m["name"].lower():
                matched = m
                break
        if matched:
            res = fetch_weather(matched)
            print(format_detailed_weather(res))
            return
        else:
            # Fallback to general summary if query not directly matched
            pass
            
    print(format_all_weather_summary())

if __name__ == "__main__":
    main()
