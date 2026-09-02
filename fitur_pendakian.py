import sys
import os
import glob
import math
import json
import urllib.request
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt

def get_weather(lat: float, lon: float) -> dict:
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&hourly=precipitation,temperature_2m,windspeed_10m"
    req = urllib.request.Request(url, headers={'User-Agent': 'HermesPendakianBot/1.0'})
    try:
        with urllib.request.urlopen(req, timeout=5) as res:
            data = json.loads(res.read().decode('utf-8'))
            cw = data.get('current_weather', {})
            return {
                'temp': cw.get('temperature'),
                'windspeed': cw.get('windspeed'),
                'weathercode': cw.get('weathercode'),
                'status': 'OK'
            }
    except Exception as e:
        return {'status': 'ERROR', 'error': str(e)}

def parse_gpx_points(gpx_path):
    tree = ET.parse(gpx_path)
    root = tree.getroot()
    pts = []
    for el in root.iter():
        if el.tag.split('}')[-1] == 'trkpt':
            lat = float(el.attrib['lat'])
            lon = float(el.attrib['lon'])
            ele = 0.0
            for c in el:
                if c.tag.split('}')[-1] == 'ele':
                    ele = float(c.text)
            pts.append((lat, lon, ele))
    return pts

def haversine(p1, p2):
    R = 6371000
    phi1, phi2 = math.radians(p1[0]), math.radians(p2[0])
    dphi = math.radians(p2[0] - p1[0])
    dlambda = math.radians(p2[1] - p1[1])
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1-a))

def generate_elevation_chart(gpx_path: str, output_img="/tmp/elevation_profile.png") -> str:
    pts = parse_gpx_points(gpx_path)
    if not pts:
        raise ValueError("No points found in GPX")
    
    dists = [0.0]
    eles = [pts[0][2]]
    cum_d = 0.0
    for i in range(1, len(pts)):
        cum_d += haversine(pts[i-1], pts[i]) / 1000.0
        dists.append(cum_d)
        eles.append(pts[i][2])
    
    plt.figure(figsize=(10, 4), dpi=120)
    plt.plot(dists, eles, color='#2c3e50', linewidth=2, label='Elevation (m)')
    plt.fill_between(dists, eles, min(eles), color='#3498db', alpha=0.3)
    
    name = os.path.basename(gpx_path).replace('.gpx', '')
    plt.title(f"Profil Elevasi - {name}", fontsize=12, fontweight='bold')
    plt.xlabel("Jarak (km)")
    plt.ylabel("Elevasi (mdpl)")
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig(output_img)
    plt.close()
    return output_img

if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else "all"
    if action == "weather":
        lat = float(sys.argv[2]) if len(sys.argv) > 2 else -7.384
        lon = float(sys.argv[3]) if len(sys.argv) > 3 else 110.037
        print(json.dumps(get_weather(lat, lon)))
    elif action == "chart":
        gpx_f = sys.argv[2]
        print(generate_elevation_chart(gpx_f))
