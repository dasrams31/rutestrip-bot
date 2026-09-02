import os
import sys
import glob
import math
import re
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
        matched = [f for f in gpx_files if q in os.path.basename(f).lower()]
        if matched:
            gpx_files = matched
        else:
            # If query not found in GPX DB, raise explicit error rather than showing ALL mountains
            print(f"TRACK_NOT_FOUND:{query}")
            sys.exit(1)
    
    lats = []
    lons = []
    tracks = []
    seen_names = set()
    
    # Real Pos Data Knowledge Base for Sumbing Routes
    SUMBING_POS_MAP = {
        'garung': [
            ('Basecamp Garung', -7.3439),
            ('Pos 1 Malim', -7.3551),
            ('Pos 2 Genik', -7.3638),
            ('Pos 3 Pestan', -7.3725),
            ('Pasar Watu', -7.3789),
            ('Puncak Rajawali', -7.3793)
        ],
        'bowongso': [
            ('Basecamp Bowongso', -7.3763),
            ('Pos 1 Bogani', -7.3800),
            ('Pos 2 Gajahan', -7.3817),
            ('Pos 3 Sapuran', -7.3822),
            ('Puncak Bowongso', -7.3834)
        ],
        'gajah mungkur': [
            ('Basecamp Gajah Mungkur', -7.3897),
            ('Pos 1', -7.3856),
            ('Pos 2', -7.3838),
            ('Pos 3 Plawangan', -7.3832),
            ('Puncak Buntu', -7.3837)
        ],
        'batursari': [
            ('Basecamp Batursari', -7.3421),
            ('Pos 1', -7.3550),
            ('Pos 2', -7.3680),
            ('Pos 3', -7.3780),
            ('Puncak Batursari', -7.3832)
        ],
        'butuh kaliangkrik': [
            ('Basecamp Nepal Van Java', -7.4175),
            ('Pos 1 Payung', -7.4080),
            ('Pos 2 Kethekan', -7.3988),
            ('Pos 3 Camp Area', -7.3895),
            ('Puncak Sejati', -7.3844)
        ]
    }
    
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
            f_eles = []
            for el in root.iter():
                if el.tag.split('}')[-1] == 'trkpt':
                    f_lats.append(float(el.attrib['lat']))
                    f_lons.append(float(el.attrib['lon']))
                    ele_val = 0.0
                    for c in el:
                        if c.tag.split('}')[-1] == 'ele' and c.text:
                            try: ele_val = float(c.text)
                            except: pass
                    f_eles.append(ele_val)
            
            if f_lats:
                lats.extend(f_lats)
                lons.extend(f_lons)
                tracks.append((clean, f_lats, f_lons, f_eles, f))
        except Exception:
            pass

    if not lats:
        raise ValueError("No GPX trackpoints found")

    fig, ax = plt.subplots(figsize=(12, 8), dpi=200)

    colors = ['#00e676', '#ffea00', '#ff1744', '#00e5ff', '#d500f9', '#ff9100']
    
    all_x = []
    all_y = []
    
    for idx, (name, t_lats, t_lons, t_eles, filepath) in enumerate(tracks):
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
        
        # Check if file has explicit waypoints
        tree = ET.parse(filepath)
        wpts = tree.getroot().findall('.//{*}wpt')
        has_wpts = False
        for w in wpts:
            name_el = w.find('{*}name')
            w_name = name_el.text.strip() if name_el is not None and name_el.text else ''
            if w_name and not re.match(r'^(ACTIVE LOG|AGUNG DOWN|jangyudi|\d+$)', w_name, re.I) and len(w_name) <= 30:
                has_wpts = True
                break
                
        # If no explicit waypoints, show Basecamp and Puncak markers on actual GPX track
        if not has_wpts and t_lats:
            max_e_idx = 0
            max_e = -9999
            for i, ele in enumerate(t_eles):
                if ele > max_e:
                    max_e = ele
                    max_e_idx = i
            
            puncak_lat, puncak_lon = t_lats[max_e_idx], t_lons[max_e_idx]
            bc_lat, bc_lon = t_lats[0], t_lons[0]
            
            # Determine specific peak name based on route file
            fn_low = os.path.basename(filepath).lower()
            peak_title = "Puncak"
            offset = (5, 5)
            if "garung" in fn_low: 
                peak_title = "Puncak Rajawali"
                offset = (6, 12)
            elif "bowongso" in fn_low: 
                peak_title = "Puncak Bowongso"
                offset = (-85, -14)
            elif "gajah" in fn_low: 
                peak_title = "Puncak Buntu"
                offset = (-75, 10)
            elif "batursari" in fn_low: 
                peak_title = "Puncak Batursari"
                offset = (8, -12)
            elif "butuh" in fn_low or "kaliangkrik" in fn_low or "adipura" in fn_low: 
                peak_title = "Puncak Sejati"
                offset = (10, 4)
            
            # Basecamp marker
            bc_x, bc_y = latlon_to_mercator(bc_lat, bc_lon)
            ax.scatter(bc_x, bc_y, color='#ffffff', edgecolor='#000000', s=50, zorder=5, marker='o')
            
            # Puncak marker & annotation
            p_x, p_y = latlon_to_mercator(puncak_lat, puncak_lon)
            ax.scatter(p_x, p_y, color='#ffea00', edgecolor='#000000', s=90, zorder=6, marker='^')
            ax.annotate(peak_title, (p_x, p_y), textcoords="offset points", xytext=offset,
                        fontsize=7, color='#ffffff', weight='bold',
                        bbox=dict(boxstyle="round,pad=0.2", fc="#000000", ec=color, alpha=0.85),
                        arrowprops=dict(arrowstyle="->", color=color, lw=1.2),
                        zorder=7)

    # Parse and plot explicit Waypoints (Pos & Spot) from GPX files if available
    for f in sorted(gpx_files):
        try:
            tree = ET.parse(f)
            root = tree.getroot()
            for w in root.findall('.//{*}wpt'):
                lat = float(w.attrib['lat'])
                lon = float(w.attrib['lon'])
                name_el = w.find('{*}name')
                w_name = name_el.text.strip() if name_el is not None and name_el.text else ''
                # Filter out noisy waypoint logs
                if w_name and not re.match(r'^(ACTIVE LOG|AGUNG DOWN|jangyudi|\d+$)', w_name, re.I) and len(w_name) <= 30:
                    wx, wy = latlon_to_mercator(lat, lon)
                    ax.scatter(wx, wy, color='#ff1744', edgecolor='#ffffff', s=45, zorder=6, marker='s')
                    ax.annotate(w_name, (wx, wy), textcoords="offset points", xytext=(4, 4),
                                fontsize=7, color='#ffffff', weight='bold',
                                bbox=dict(boxstyle="round,pad=0.2", fc="#000000", ec="#ffea00", alpha=0.85),
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
