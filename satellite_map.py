import os
import sys
import glob
import math
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import contextily as cx

DOCS_DIR = "/root/.hermes/cache/documents"
GPX_DB_DIR = "/root/rutestrip-bot/gpx_db"

def latlon_to_mercator(lat, lon):
    r_major = 6378137.0
    x = r_major * math.radians(lon)
    scale = math.sin(math.radians(lat))
    y = 3189068.5 * math.log((1.0 + scale) / (1.0 - scale))
    return x, y

def generate_satellite_map(query=None, output_img="/tmp/satellite_map.png"):
    # Target gpx_db only to avoid duplicates from cache
    gpx_files = glob.glob(os.path.join(GPX_DB_DIR, "*.gpx"))
    
    if query:
        q = query.lower()
        gpx_files = [f for f in gpx_files if q in os.path.basename(f).lower()]
        
    if not gpx_files:
        gpx_files = glob.glob(os.path.join(GPX_DB_DIR, "*.gpx"))
    
    lats = []
    lons = []
    tracks = []
    seen_names = set()
    
    for f in sorted(gpx_files):
        try:
            tree = ET.parse(f)
            root = tree.getroot()
            fname = os.path.basename(f).replace('.gpx', '')
            clean = fname.split('_')[-1]
            
            if clean in seen_names:
                continue
            seen_names.add(clean)
            
            f_lats = []
            f_lons = []
            for el in root.iter():
                if el.tag.split('}')[-1] == 'trkpt':
                    f_lats.append(float(el.attrib['lat']))
                    f_lons.append(float(el.attrib['lon']))
            
            if f_lats:
                lats.extend(f_lats)
                lons.extend(f_lons)
                tracks.append((clean, f_lats, f_lons))
        except Exception:
            pass

    if not lats:
        raise ValueError("No GPX trackpoints found")

    fig, ax = plt.subplots(figsize=(12, 8), dpi=200)

    colors = ['#00e676', '#ffea00', '#ff1744', '#00e5ff', '#d500f9', '#ff9100']
    
    all_x = []
    all_y = []
    
    for idx, (name, t_lats, t_lons) in enumerate(tracks):
        color = colors[idx % len(colors)]
        m_xs = []
        m_ys = []
        for la, lo in zip(t_lats, t_lons):
            mx, my = latlon_to_mercator(la, lo)
            m_xs.append(mx)
            m_ys.append(my)
            all_x.append(mx)
            all_y.append(my)
            
        ax.plot(m_xs, m_ys, color=color, linewidth=2.8, label=name, alpha=0.95, zorder=3)
        # Basecamp & Peak markers
        ax.scatter(m_xs[0], m_ys[0], color='#ffffff', edgecolor='#000000', s=50, zorder=5, marker='o')
        ax.scatter(m_xs[-1], m_ys[-1], color='#ffea00', edgecolor='#000000', s=90, zorder=5, marker='^')

    # Parse and plot Waypoints (Pos & Spot) from GPX files if available
    for f in sorted(gpx_files):
        try:
            tree = ET.parse(f)
            root = tree.getroot()
            for w in root.findall('.//{*}wpt'):
                lat = float(w.attrib['lat'])
                lon = float(w.attrib['lon'])
                name_el = w.find('{*}name')
                w_name = name_el.text if name_el is not None else ''
                if w_name:
                    wx, wy = latlon_to_mercator(lat, lon)
                    ax.scatter(wx, wy, color='#ff1744', edgecolor='#ffffff', s=40, zorder=6, marker='s')
                    ax.annotate(w_name, (wx, wy), textcoords="offset points", xytext=(4, 4),
                                fontsize=6.5, color='#ffffff', weight='bold',
                                bbox=dict(boxstyle="round,pad=0.15", fc="#000000", ec="#ffea00", alpha=0.75),
                                zorder=7)
        except Exception:
            pass

    # Calculate Mercator Bounding Box
    min_x, max_x = min(all_x), max(all_x)
    min_y, max_y = min(all_y), max(all_y)
    
    pad_x = (max_x - min_x) * 0.15 or 2000
    pad_y = (max_y - min_y) * 0.15 or 2000
    
    ax.set_xlim(min_x - pad_x, max_x + pad_x)
    ax.set_ylim(min_y - pad_y, max_y + pad_y)
    
    # Add Esri World Imagery Satellite basemap
    cx.add_basemap(ax, source=cx.providers.Esri.WorldImagery, zorder=1)

    title_str = f"🛰️ PETA CITRA SATELIT & RUTE - {query.upper() if query else 'GUNUNG JAWA'}"
    ax.set_title(title_str, fontsize=13, pad=12, weight='bold', color='#ffffff', bbox=dict(boxstyle="round,pad=0.3", fc="#000000", alpha=0.7))
    ax.axis('off')
    ax.legend(fontsize=8, loc='upper left', framealpha=0.85, facecolor='#000000', labelcolor='#ffffff', edgecolor='#ffea00')
    
    plt.tight_layout()
    plt.savefig(output_img, facecolor='#000000')
    plt.close()
    
    return output_img

if __name__ == "__main__":
    q = sys.argv[1] if len(sys.argv) > 1 else "sumbing"
    print(generate_satellite_map(q))
