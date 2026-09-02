import matplotlib.pyplot as plt
import numpy as np

def generate_rutestrip_logo(output_png="/tmp/rutestrip_logo.png", output_svg="/tmp/rutestrip_logo.svg"):
    fig, ax = plt.subplots(figsize=(8, 8), dpi=300)
    fig.patch.set_facecolor('#0d1117')
    ax.set_facecolor('#0d1117')
    
    # Outer Compass Ring
    circle = plt.Circle((0, 0), 1.0, color='#1f2937', ec='#ff5500', lw=4, fill=True)
    ax.add_patch(circle)
    
    # Inner Ring
    inner_circle = plt.Circle((0, 0), 0.92, color='#0f172a', ec='#ff9900', lw=1.5, ls='--', fill=True)
    ax.add_patch(inner_circle)
    
    # Compass Cardinals
    ax.text(0, 0.83, 'N', color='#ff5500', fontsize=16, fontweight='bold', ha='center', va='center')
    ax.text(0.83, 0, 'E', color='#94a3b8', fontsize=14, fontweight='bold', ha='center', va='center')
    ax.text(0, -0.83, 'S', color='#94a3b8', fontsize=14, fontweight='bold', ha='center', va='center')
    ax.text(-0.83, 0, 'W', color='#94a3b8', fontsize=14, fontweight='bold', ha='center', va='center')

    # Mountain Peaks (Background Peak & Foreground Peak)
    bg_peak_x = [-0.65, -0.15, 0.45]
    bg_peak_y = [-0.45, 0.42, -0.45]
    ax.fill(bg_peak_x, bg_peak_y, color='#334155', alpha=0.9)
    # Snow cap bg peak
    ax.fill([-0.25, -0.15, -0.03], [0.25, 0.42, 0.25], color='#cbd5e1', alpha=0.95)

    # Foreground Peak
    fg_peak_x = [-0.45, 0.15, 0.65]
    fg_peak_y = [-0.45, 0.58, -0.45]
    ax.fill(fg_peak_x, fg_peak_y, color='#1e293b', ec='#ff5500', lw=2)
    # Snow cap fg peak
    ax.fill([0.02, 0.15, 0.28], [0.38, 0.58, 0.38], color='#ffffff')

    # Trail Line (Glowing Orange Trail GPX track wrapping around the mountain)
    t = np.linspace(-0.5, 0.15, 100)
    trail_x = t
    trail_y = -0.4 + 0.95 * (t + 0.5) + 0.08 * np.sin(t * 18)
    ax.plot(trail_x, trail_y, color='#ff5500', lw=4.5, zorder=10)
    ax.plot(trail_x, trail_y, color='#ffcc00', lw=2.0, zorder=11)
    
    # Waypoint Nodes
    ax.scatter([-0.42, -0.2, 0.0, 0.15], [-0.38, -0.18, 0.12, 0.58], color='#ffea00', edgecolor='#000000', s=[40, 50, 60, 90], zorder=12)

    # Typography
    ax.text(0, -0.56, 'RUTESTRIP', color='#ffffff', fontsize=22, fontweight='bold', ha='center', va='center')
    ax.text(0, -0.70, 'PENDAKIAN BOT', color='#ff9900', fontsize=12, fontweight='bold', ha='center', va='center')

    ax.set_xlim(-1.1, 1.1)
    ax.set_ylim(-1.1, 1.1)
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig(output_png, facecolor='#0d1117', edgecolor='none')
    plt.savefig(output_svg, facecolor='#0d1117', edgecolor='none')
    plt.close()
    
    return output_png, output_svg

if __name__ == "__main__":
    png, svg = generate_rutestrip_logo()
    print(f"PNG:{png}")
    print(f"SVG:{svg}")
