import sys
import os
import math
import glob
import json
import xml.etree.ElementTree as ET
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GPX_DB_DIR = os.path.join(BASE_DIR, "gpx_db")
if not os.path.exists(GPX_DB_DIR):
    GPX_DB_DIR = "/home/ubuntu/rutestrip-bot/gpx_db"

def find_gpx(mountain_query: str) -> str:
    query = mountain_query.lower()
    files = glob.glob(os.path.join(GPX_DB_DIR, "*.gpx"))
    matches = [f for f in files if all(q in os.path.basename(f).lower() for q in query.split())]
    if not matches:
        matches = [f for f in files if any(q in os.path.basename(f).lower() for q in query.split())]
    return matches[0] if matches else (files[0] if files else None)

def haversine(p1, p2):
    R = 6371000
    phi1, phi2 = math.radians(p1[0]), math.radians(p2[0])
    dphi = math.radians(p2[0] - p1[0])
    dlambda = math.radians(p2[1] - p1[1])
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1-a))

def parse_gpx(gpx_path):
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
                    try:
                        ele = float(c.text)
                    except:
                        pass
            pts.append((lat, lon, ele))
            
    if not pts:
        return None
        
    dists = [0.0]
    eles = [pts[0][2]]
    total_gain = 0.0
    cum_d = 0.0
    for i in range(1, len(pts)):
        d = haversine(pts[i-1], pts[i]) / 1000.0
        cum_d += d
        dists.append(cum_d)
        eles.append(pts[i][2])
        gain = pts[i][2] - pts[i-1][2]
        if gain > 0:
            total_gain += gain
            
    return {
        "distances": dists,
        "elevations": eles,
        "total_dist": cum_d,
        "total_gain": total_gain,
        "min_ele": min(eles),
        "max_ele": max(eles)
    }

def get_difficulty(gain, dist):
    if gain > 1600 or dist > 14:
        return "HARD / SANGAT MENANTANG", "#e74c3c"
    elif gain > 900 or dist > 8:
        return "MODERATE / SEDANG", "#f39c12"
    else:
        return "EASY / RAMAH PEMULA", "#2ecc71"

def generate_story_card(mountain_query: str, output_path: str = "/tmp/story_card.png") -> str:
    gpx_file = find_gpx(mountain_query)
    if not gpx_file:
        raise ValueError(f"File GPX tidak ditemukan untuk query: {mountain_query}")
        
    raw_name = os.path.basename(gpx_file).replace('.gpx', '').replace('Mt. ', 'Gunung ').replace('_', ' ')
    data = parse_gpx(gpx_file)
    if not data or len(data["distances"]) < 2:
        raise ValueError("Data elevasi GPX kosong atau tidak valid.")
        
    naismith_hours = (data["total_dist"] / 4.0) + (data["total_gain"] / 600.0)
    diff_text, diff_color = get_difficulty(data["total_gain"], data["total_dist"])
    
    # 9:16 vertical ratio (1080 x 1920)
    fig = plt.figure(figsize=(9, 16), dpi=120)
    fig.patch.set_facecolor('#0d1117')
    
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor('#0d1117')
    ax.set_xlim(0, 9)
    ax.set_ylim(0, 16)
    ax.axis('off')
    
    # Top Header Card
    header_box = FancyBboxPatch((0.5, 13.6), 8.0, 1.8, boxstyle="round,pad=0.2,rounding_size=0.3",
                               facecolor="#161b22", edgecolor="#30363d", linewidth=1.5)
    ax.add_patch(header_box)
    
    ax.text(4.5, 14.8, "RUTESTRIP HIKING COPILOT", color="#58a6ff", fontsize=13, fontweight='bold', ha='center', va='center')
    display_title = raw_name[:36] + ('...' if len(raw_name) > 36 else '')
    ax.text(4.5, 14.15, display_title, color="#ffffff", fontsize=18, fontweight='bold', ha='center', va='center')
    
    # Difficulty Badge
    badge_box = FancyBboxPatch((4.5 - 2.2, 13.25), 4.4, 0.5, boxstyle="round,pad=0.1,rounding_size=0.2",
                              facecolor=diff_color, edgecolor="none", alpha=0.9)
    ax.add_patch(badge_box)
    ax.text(4.5, 13.5, f"TINGKAT: {diff_text}", color="#ffffff", fontsize=10, fontweight='bold', ha='center', va='center')
    
    # Stats 4-Grid Cards
    stats = [
        ("PUNCAK MAKSIMAL", f"{int(data['max_ele']):,} mdpl".replace(',', '.'), "#58a6ff"),
        ("TOTAL ELEV GAIN", f"+{int(data['total_gain']):,} m".replace(',', '.'), "#3fb950"),
        ("JARAK TREK", f"{data['total_dist']:.1f} km", "#d29922"),
        ("EST. WAKTU NAISMITH", f"~{naismith_hours:.1f} Jam", "#f778ba")
    ]
    
    positions = [(0.5, 11.5), (4.7, 11.5), (0.5, 10.0), (4.7, 10.0)]
    for (label, val, col), (x, y) in zip(stats, positions):
        box = FancyBboxPatch((x, y), 3.8, 1.2, boxstyle="round,pad=0.15,rounding_size=0.2",
                             facecolor="#161b22", edgecolor="#30363d", linewidth=1.2)
        ax.add_patch(box)
        ax.text(x + 0.3, y + 0.85, label, color="#8b949e", fontsize=10, fontweight='bold', va='center')
        ax.text(x + 0.3, y + 0.35, val, color=col, fontsize=16, fontweight='bold', va='center')
        
    # Center Elevation Chart Axis
    chart_ax = fig.add_axes([0.10, 0.33, 0.80, 0.25])
    chart_ax.set_facecolor('#161b22')
    chart_ax.plot(data["distances"], data["elevations"], color='#58a6ff', linewidth=2.5)
    chart_ax.fill_between(data["distances"], data["elevations"], min(data["elevations"]), color='#1f6feb', alpha=0.35)
    
    chart_ax.set_title("PROFIL ELEVASI JALUR (GPX TRACK)", color='#ffffff', fontsize=11, fontweight='bold', pad=10)
    chart_ax.set_xlabel("Jarak Trek Kumulatif (km)", color='#8b949e', fontsize=9)
    chart_ax.set_ylabel("Ketinggian (mdpl)", color='#8b949e', fontsize=9)
    chart_ax.tick_params(colors='#8b949e', labelsize=8)
    for spine in chart_ax.spines.values():
        spine.set_color('#30363d')
    chart_ax.grid(True, linestyle='--', alpha=0.25, color='#ffffff')
    
    # Peak point marker
    max_idx = np.argmax(data["elevations"])
    chart_ax.scatter([data["distances"][max_idx]], [data["elevations"][max_idx]], color='#f778ba', s=60, zorder=5)
    chart_ax.annotate(f"Puncak {int(data['max_ele'])}m", 
                      (data["distances"][max_idx], data["elevations"][max_idx]),
                      textcoords="offset points", xytext=(0, 8), ha='center',
                      color='#ffffff', fontsize=8, fontweight='bold')

    # Safety & Layering Box
    safety_box = FancyBboxPatch((0.5, 1.4), 8.0, 3.2, boxstyle="round,pad=0.2,rounding_size=0.3",
                               facecolor="#161b22", edgecolor="#30363d", linewidth=1.5)
    ax.add_patch(safety_box)
    
    ax.text(4.5, 4.2, "REKOMENDASI PERSIAPAN & KESELAMATAN", color="#e3b341", fontsize=11, fontweight='bold', ha='center', va='center')
    
    tips = [
        "- Sistem Layering: Base layer (quick-dry) + Mid (fleece/down) + Windbreaker.",
        "- Manajemen Air: Minimal 2.5 - 3.5 Liter/orang untuk jalur camp 2D1N.",
        "- Waktu Start Ideal: 07:00 - 08:30 WIB (hindari mendaki saat terik siang).",
        "- Perlengkapan Wajib: Headlamp + baterai cadangan, jas hujan, P3K & survival kit.",
        "- Etika Pendaki: Bawa turun sampahmu, hormati alam & kearifan lokal."
    ]
    
    start_y = 3.65
    for tip in tips:
        ax.text(0.8, start_y, tip, color="#c9d1d9", fontsize=9.2, va='center')
        start_y -= 0.46
        
    # Footer Branding
    ax.text(4.5, 0.7, "RuteStrip ID - Portal Navigasi & Komunitas Pendaki Jawa", color="#8b949e", fontsize=10, ha='center', va='center')
    ax.text(4.5, 0.35, "Generated automatically by RuteStrip AI Engine", color="#484f58", fontsize=8, ha='center', va='center')
    
    plt.savefig(output_path, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight', pad_inches=0.1)
    plt.close(fig)
    return output_path

if __name__ == "__main__":
    q = sys.argv[1] if len(sys.argv) > 1 else "sumbing"
    out = sys.argv[2] if len(sys.argv) > 2 else f"/tmp/story_{q}.png"
    try:
        res = generate_story_card(q, out)
        print(f"STORY:{res}")
    except Exception as e:
        print(f"ERROR:{e}")
