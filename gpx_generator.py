import os

GPX_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" creator="Hermes Pendakian Bot" xmlns="http://www.topografix.com/GPX/1/1">
  <metadata>
    <name>{name} - Jalur {jalur}</name>
    <desc>Track GPX Pendakian {name}</desc>
  </metadata>
  <wpt lat="{start_lat}" lon="{start_lon}">
    <ele>{start_ele}</ele>
    <name>Basecamp {name}</name>
  </wpt>
  <wpt lat="{end_lat}" lon="{end_lon}">
    <ele>{end_ele}</ele>
    <name>Puncak {name}</name>
  </wpt>
  <trk>
    <name>Jalur {jalur}</name>
    <trkseg>
      <trkpt lat="{start_lat}" lon="{start_lon}"><ele>{start_ele}</ele></trkpt>
      <trkpt lat="{end_lat}" lon="{end_lon}"><ele>{end_ele}</ele></trkpt>
    </trkseg>
  </trk>
</gpx>
"""

ROUTES = {
    "prau": {"name": "Gunung Prau", "jalur": "Patak Banteng", "start_lat": -7.214, "start_lon": 109.928, "start_ele": 1800, "end_lat": -7.186, "end_lon": 109.923, "end_ele": 2590},
    "andong": {"name": "Gunung Andong", "jalur": "Sawit", "start_lat": -7.387, "start_lon": 110.373, "start_ele": 1300, "end_lat": -7.384, "end_lon": 110.376, "end_ele": 1726},
    "gede": {"name": "Gunung Gede", "jalur": "Cibodas", "start_lat": -6.740, "start_lon": 106.996, "start_ele": 1420, "end_lat": -6.790, "end_lon": 106.984, "end_ele": 2958},
}

def generate_gpx(mountain_key: str, output_dir="/tmp") -> str:
    key = mountain_key.lower()
    data = ROUTES.get(key)
    if not data:
        raise ValueError(f"Gunung {mountain_key} tidak ditemukan")
    path = os.path.join(output_dir, f"{key}_track.gpx")
    xml = GPX_TEMPLATE.format(**data)
    with open(path, "w") as f:
        f.write(xml)
    return path

if __name__ == "__main__":
    import sys
    m = sys.argv[1] if len(sys.argv) > 1 else "prau"
    print(generate_gpx(m))
