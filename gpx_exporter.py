import os
import glob
import re
import xml.etree.ElementTree as ET

DOCS_DIR = "/home/ubuntu/.hermes/cache/documents"

GPX_DB_DIR = "/home/ubuntu/rutestrip-bot/gpx_db"

def find_gpx(mountain_query: str) -> str:
    query = mountain_query.lower()
    files = glob.glob(os.path.join(GPX_DB_DIR, "*.gpx")) + glob.glob(os.path.join(DOCS_DIR, "*.gpx"))
    
    matches = []
    for f in files:
        fname = os.path.basename(f).lower()
        if all(q in fname for q in query.split()):
            matches.append(f)
            
    if not matches:
        # Fallback partial search
        for f in files:
            fname = os.path.basename(f).lower()
            if any(q in fname for q in query.split()):
                matches.append(f)
                
    return matches[0] if matches else None

def gpx_to_kml(gpx_path: str, output_kml="/tmp/track.kml") -> str:
    tree = ET.parse(gpx_path)
    root = tree.getroot()
    
    pts = []
    for el in root.iter():
        if el.tag.split('}')[-1] == 'trkpt':
            lat = el.attrib['lat']
            lon = el.attrib['lon']
            ele = "0"
            for c in el:
                if c.tag.split('}')[-1] == 'ele':
                    ele = c.text
            pts.append(f"{lon},{lat},{ele}")
            
    coords_str = " ".join(pts)
    name = os.path.basename(gpx_path).replace('.gpx', '')
    
    kml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>{name}</name>
    <Placemark>
      <name>{name} Track</name>
      <LineString>
        <coordinates>{coords_str}</coordinates>
      </LineString>
    </Placemark>
  </Document>
</kml>"""

    with open(output_kml, "w", encoding="utf-8") as f:
        f.write(kml_content)
        
    return output_kml

if __name__ == "__main__":
    import sys
    query = sys.argv[1] if len(sys.argv) > 1 else "sumbing kaliangkrik"
    fmt = sys.argv[2] if len(sys.argv) > 2 else "gpx"
    
    gpx_path = find_gpx(query)
    if not gpx_path:
        print("ERROR: Track tidak ditemukan")
        sys.exit(1)
        
    if fmt == "kml":
        out = gpx_to_kml(gpx_path)
        print(f"KML:{out}")
    else:
        print(f"GPX:{gpx_path}")
