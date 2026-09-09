import os
import sys
import glob
import math
import xml.etree.ElementTree as ET
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import griddata

DOCS_DIR = "/home/ubuntu/rutestrip-bot/gpx_db"

def generate_heatmap(query=None, output_img="/tmp/gpx_heatmap.png"):
    gpx_files = glob.glob(os.path.join(DOCS_DIR, "*.gpx"))
    
    if query:
        q = query.lower()
        gpx_files = [f for f in gpx_files if q in os.path.basename(f).lower()]
        
    if not gpx_files:
        gpx_files = glob.glob(os.path.join(DOCS_DIR, "*.gpx"))
    
    lats = []
    lons = []
    eles = []
    tracks = []
    
    for f in gpx_files:
        try:
            tree = ET.parse(f)
            root = tree.getroot()
            fname = os.path.basename(f).replace('.gpx', '')
            clean = fname.split('_')[-1]
            
            f_lats = []
            f_lons = []
            f_eles = []
            for el in root.iter():
                if el.tag.split('}')[-1] == 'trkpt':
                    lat = float(el.attrib['lat'])
                    lon = float(el.attrib['lon'])
                    ele = 0.0
                    for c in el:
                        if c.tag.split('}')[-1] == 'ele':
                            ele = float(c.text)
                    f_lats.append(lat)
                    f_lons.append(lon)
                    f_eles.append(ele)
            
            if f_lats:
                lats.extend(f_lats)
                lons.extend(f_lons)
                eles.extend(f_eles)
                tracks.append((clean, f_lats, f_lons, f_eles))
        except Exception:
            pass

    if not lats:
        raise ValueError("No GPX trackpoints found")

    fig, ax = plt.subplots(figsize=(11, 7), dpi=180)
    
    # 1. Create Topographic Elevation Grid (Contours)
    grid_x, grid_y = np.mgrid[min(lons):max(lons):200j, min(lats):max(lats):200j]
    points = np.column_stack((lons, lats))
    grid_z = griddata(points, eles, (grid_x, grid_y), method='cubic', fill_value=min(eles))
    
    # Plot Filled Elevation Contours (Terrain Color Map)
    contour_fill = ax.contourf(grid_x, grid_y, grid_z, levels=25, cmap='terrain', alpha=0.85)
    contour_lines = ax.contour(grid_x, grid_y, grid_z, levels=12, colors='#333333', linewidths=0.5, alpha=0.6)
    ax.clabel(contour_lines, inline=True, fontsize=7, fmt='%1.0fm', colors='#222222')
    
    cbar = fig.colorbar(contour_fill, ax=ax, pad=0.02)
    cbar.set_label('Elevasi (mdpl)', fontsize=10, weight='bold')

    # 2. Overlay GPX Tracks with Vibrant High-Visibility Lines
    colors = ['#d32f2f', '#7b1fa2', '#1976d2', '#388e3c', '#f57c00', '#00796b']
    for idx, (name, t_lats, t_lons, t_eles) in enumerate(tracks):
        color = colors[idx % len(colors)]
        ax.plot(t_lons, t_lats, color=color, linewidth=2.5, label=name[:22], alpha=0.9)
        # Mark Start/Basecamp & Peak
        ax.scatter(t_lons[0], t_lats[0], color='#212121', s=40, zorder=5, marker='o')
        ax.scatter(t_lons[-1], t_lats[-1], color='#ffd600', edgecolor='#000000', s=80, zorder=5, marker='^')

    title_str = f"🗻 PETA TOPOGRAFI & KONTUR RUTE - {query.upper() if query else 'GUNUNG JAWA'}"
    ax.set_title(title_str, fontsize=12, pad=12, weight='bold', color='#1a237e')
    ax.set_xlabel("Longitude", fontsize=9)
    ax.set_ylabel("Latitude", fontsize=9)
    ax.grid(True, linestyle=':', alpha=0.4, color='#555555')
    ax.legend(fontsize=8, loc='upper left', framealpha=0.9, facecolor='#ffffff', edgecolor='#cccccc')
    
    plt.tight_layout()
    plt.savefig(output_img)
    plt.close()
    
    return output_img

if __name__ == "__main__":
    q = sys.argv[1] if len(sys.argv) > 1 else None
    print(generate_heatmap(q))
