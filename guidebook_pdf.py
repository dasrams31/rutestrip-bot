#!/usr/bin/env python3
import sys
import os
import glob
import math
import xml.etree.ElementTree as ET
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm, mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, HRFlowable
from reportlab.graphics.shapes import Drawing, Rect, String, Line, PolyLine, Circle

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GPX_DB_DIR = os.path.join(BASE_DIR, "gpx_db")
if not os.path.exists(GPX_DB_DIR):
    GPX_DB_DIR = "/home/ubuntu/rutestrip-bot/gpx_db"

def haversine(p1, p2):
    R = 6371000
    phi1, phi2 = math.radians(p1[0]), math.radians(p2[0])
    dphi = math.radians(p2[0] - p1[0])
    dlambda = math.radians(p2[1] - p1[1])
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1-a))

def find_gpx_file(mountain_query: str):
    query = mountain_query.lower()
    files = glob.glob(os.path.join(GPX_DB_DIR, "*.gpx"))
    matches = [f for f in files if all(q in os.path.basename(f).lower() for q in query.split())]
    if not matches:
        matches = [f for f in files if any(q in os.path.basename(f).lower() for q in query.split())]
    return matches[0] if matches else (files[0] if files else None)

def parse_gpx_data(gpx_path):
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
        "max_ele": max(eles),
        "start_ele": pts[0][2],
        "summit_ele": max(eles)
    }

def get_difficulty_label(gain, dist):
    if gain > 1600 or dist > 13:
        return "TINGGI (Hard / Ekstrem)", colors.HexColor("#c0392b")
    elif gain > 900 or dist > 7:
        return "SEDANG (Moderate)", colors.HexColor("#d35400")
    else:
        return "RAMAH PEMULA (Easy)", colors.HexColor("#27ae60")

def draw_elevation_chart(distances, elevations, width=480, height=100):
    d = Drawing(width, height)
    # Background Box
    d.add(Rect(0, 0, width, height, fillColor=colors.HexColor("#f8fafc"), strokeColor=colors.HexColor("#cbd5e1"), strokeWidth=1, rx=4, ry=4))
    
    if not distances or len(distances) < 2:
        d.add(String(width/2, height/2, "Profil Elevasi GPX", textAnchor="middle", fontSize=9, fillColor=colors.gray))
        return d

    # Resample to max 100 points for smooth rendering
    step = max(1, len(distances) // 100)
    sub_d = distances[::step]
    sub_e = elevations[::step]
    if sub_d[-1] != distances[-1]:
        sub_d.append(distances[-1])
        sub_e.append(elevations[-1])

    max_d = max(sub_d) if max(sub_d) > 0 else 1.0
    min_e = min(sub_e)
    max_e = max(sub_e)
    ele_range = max(1.0, max_e - min_e)

    pad_x = 25
    pad_y = 18
    chart_w = width - (2 * pad_x)
    chart_h = height - (2 * pad_y)

    # Gridlines
    for gy in [0.25, 0.5, 0.75, 1.0]:
        y_pos = pad_y + (gy * chart_h)
        d.add(Line(pad_x, y_pos, width - pad_x, y_pos, strokeColor=colors.HexColor("#e2e8f0"), strokeWidth=0.5))

    # Polyline Points
    pts = []
    for dist, ele in zip(sub_d, sub_e):
        x = pad_x + (dist / max_d) * chart_w
        y = pad_y + ((ele - min_e) / ele_range) * chart_h
        pts.extend([x, y])

    # Draw elevation line
    d.add(PolyLine(pts, strokeColor=colors.HexColor("#1b5e20"), strokeWidth=2))

    # Labels
    d.add(String(pad_x, 5, f"Basecamp: {int(sub_e[0])} mdpl", fontSize=7, fillColor=colors.HexColor("#475569")))
    d.add(String(width - pad_x, 5, f"Puncak: {int(max_e)} mdpl ({max_d:.1f} km)", textAnchor="end", fontSize=7, fillColor=colors.HexColor("#475569")))
    d.add(String(pad_x, height - 12, f"▲ Profil Elevasi Rute", fontSize=7.5, fillColor=colors.HexColor("#1e293b")))

    return d

def generate_guidebook_pdf(mountain_query: str, output_path: str = None) -> str:
    gpx_file = find_gpx_file(mountain_query)
    if not gpx_file:
        raise FileNotFoundError(f"File GPX untuk rute '{mountain_query}' tidak ditemukan.")

    raw_name = os.path.basename(gpx_file).replace('.gpx', '').replace('Mt. ', 'Gunung ').replace('_', ' ')
    data = parse_gpx_data(gpx_file)
    if not data:
        raise ValueError("Data GPX tidak memiliki titik elevasi valid.")

    if not output_path:
        safe_name = "".join([c if c.isalnum() else "_" for c in raw_name.lower()])
        output_path = f"/tmp/guidebook_{safe_name}.pdf"

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=15*mm,
        rightMargin=15*mm,
        topMargin=12*mm,
        bottomMargin=12*mm
    )

    styles = getSampleStyleSheet()
    
    # Custom Typography Styles
    title_style = ParagraphStyle(
        'MainTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#0f172a'),
        spaceAfter=2
    )
    
    subtitle_style = ParagraphStyle(
        'SubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#475569'),
        spaceAfter=8
    )

    sec_header_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#1b5e20'),
        spaceBefore=6,
        spaceAfter=4
    )

    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#1e293b')
    )

    body_bold = ParagraphStyle(
        'BodyDarkBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#0f172a')
    )

    alert_style = ParagraphStyle(
        'AlertText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor('#7f1d1d')
    )

    elements = []

    # 1. HEADER BANNER
    elements.append(Paragraph(f"🏔️ <b>OFFLINE GUIDEBOOK & EXPEDITION BRIEFING</b>", subtitle_style))
    elements.append(Paragraph(f"<b>{raw_name.upper()}</b>", title_style))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#166534"), spaceBefore=2, spaceAfter=8))

    # 2. KEY METRICS TABLE (Naismith Time, Distance, Gain, Elevation)
    naismith_hours = (data["total_dist"] / 4.0) + (data["total_gain"] / 600.0)
    diff_label, diff_color = get_difficulty_label(data["total_gain"], data["total_dist"])
    
    metrics_data = [
        [
            Paragraph("<b>Puncak Tertinggi:</b>", body_style),
            Paragraph(f"{int(data['summit_ele'])} mdpl", body_bold),
            Paragraph("<b>Total Jarak (One-way):</b>", body_style),
            Paragraph(f"{data['total_dist']:.2f} km", body_bold)
        ],
        [
            Paragraph("<b>Elevasi Basecamp:</b>", body_style),
            Paragraph(f"{int(data['start_ele'])} mdpl", body_bold),
            Paragraph("<b>Total Elevation Gain:</b>", body_style),
            Paragraph(f"+{int(data['total_gain'])} m", body_bold)
        ],
        [
            Paragraph("<b>Estimasi Waktu Naik:</b>", body_style),
            Paragraph(f"~{naismith_hours:.1f} Jam (Naismith)", body_bold),
            Paragraph("<b>Tingkat Kesulitan:</b>", body_style),
            Paragraph(f"<b>{diff_label}</b>", body_bold)
        ]
    ]

    t_metrics = Table(metrics_data, colWidths=[3.2*cm, 4.5*cm, 3.8*cm, 4.5*cm])
    t_metrics.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f1f5f9')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(t_metrics)
    elements.append(Spacer(1, 6))

    # 3. ELEVATION CHART
    elements.append(draw_elevation_chart(data["distances"], data["elevations"], width=480, height=90))
    elements.append(Spacer(1, 6))

    # 4. ITINERARY & ESTIMASI WAKTU POS KE POS
    elements.append(Paragraph("⏱️ <b>ESTIMASI RUTE & RENCANA PERJALANAN (ITINERARY 2D1N)</b>", sec_header_style))
    
    # Generate generic or specific checkpoints
    total_km = data["total_dist"]
    step_km = total_km / 4.0
    
    itin_rows = [
        [Paragraph("<b>Pos / Checkpoint</b>", body_bold), Paragraph("<b>Jarak Kumulatif</b>", body_bold), Paragraph("<b>Estimasi Durasi</b>", body_bold), Paragraph("<b>Keterangan & Tips</b>", body_bold)],
        [Paragraph("Basecamp Regristrasi", body_style), Paragraph("0.0 km (Start)", body_style), Paragraph("08:00 WIB", body_style), Paragraph("Registrasi simaksi, briefing ranger, cek logistik", body_style)],
        [Paragraph("Pos 1 (Batas Vegetasi)", body_style), Paragraph(f"~{step_km*1:.1f} km", body_style), Paragraph("+60 - 90 menit", body_style), Paragraph("Trek perkebunan/hutan landai, ojek batas pos", body_style)],
        [Paragraph("Pos 2 / Pos Air", body_style), Paragraph(f"~{step_km*2:.1f} km", body_style), Paragraph("+90 - 120 menit", body_style), Paragraph("Rest point, isi persediaan botol air minum", body_style)],
        [Paragraph("Pos Camp (Shelter Tenda)", body_style), Paragraph(f"~{step_km*3:.1f} km", body_style), Paragraph("Tiba ~14:30 WIB", body_style), Paragraph("Dirikan tenda dome, makan malam, istirahat malam", body_style)],
        [Paragraph("Puncak (Summit Attack)", body_style), Paragraph(f"~{total_km:.1f} km", body_style), Paragraph("Start 03:30 (120 mnt)", body_style), Paragraph("Golden Sunrise, angin kencang, bawa jaket tebal", body_style)],
    ]

    t_itin = Table(itin_rows, colWidths=[4.2*cm, 2.8*cm, 3.2*cm, 6.0*cm])
    t_itin.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#e2e8f0')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
    ]))
    elements.append(t_itin)
    elements.append(Spacer(1, 6))

    # 5. DUA KOLOM: PERLENGKAPAN WAJIB & FIRST AID EMERGENCY
    elements.append(Paragraph("🎒 <b>CHECKLIST PERLENGKAPAN & PROTOKOL KESELAMATAN LAPANGAN</b>", sec_header_style))

    col_gear = [
        Paragraph("<b>PERLENGKAPAN WAJIB (TIM & PRIBADI):</b>", body_bold),
        Paragraph("• Tenda dome windproof + flysheet & pasak kokoh", body_style),
        Paragraph("• Sleeping bag polar/bulu + matras aluminium/foil", body_style),
        Paragraph("• Jaket windproof/waterproof + thermal base layer", body_style),
        Paragraph("• Headlamp + baterai cadangan & senter darurat", body_style),
        Paragraph("• Raincoat / jas hujan 2-piece (wajib di tas carrier)", body_style),
        Paragraph("• Air minum minimal 3 Liter / orang / 24 jam", body_style),
        Paragraph("• Kompor portable + gas kaleng cadangan & nesting", body_style),
        Paragraph("• Trash bag (Dilarang tinggalkan sampah sekecil apapun)", body_style),
    ]

    col_safety = [
        Paragraph("<b>FIRST AID & PROTOKOL DARURAT:</b>", body_bold),
        Paragraph("• <b>Hipotermia:</b> Lindungi dari angin, ganti baju basah, bungkus thermal blanket, beri minuman manis hangat.", body_style),
        Paragraph("• <b>AMS (Pusing/Mual):</b> Istirahat, minum air, jika tidak membaik dalam 2 jam ➔ <i>TURUN ELEVASI SEGERA!</i>", body_style),
        Paragraph("• <b>STOP Rule Tersesat:</b> Stop, Think, Observe, Plan. Jangan turun ke jurang/lembah buta tanpa jejak.", body_style),
        Paragraph("• <b>NOAA Wind Chill:</b> Suhu puncak malam hari terasa 4-8°C lebih dingin saat angin kencang berhembus.", body_style),
        Paragraph("• <b>Kontak Darurat:</b> Basarnas (115) | Polsek terdekat | Basecamp", alert_style)
    ]

    t_duo = Table([[col_gear, col_safety]], colWidths=[8.2*cm, 8.2*cm])
    t_duo.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,0), colors.HexColor('#f8fafc')),
        ('BACKGROUND', (1,0), (1,0), colors.HexColor('#fef2f2')),
        ('BOX', (0,0), (0,0), 1, colors.HexColor('#cbd5e1')),
        ('BOX', (1,0), (1,0), 1, colors.HexColor('#fecaca')),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    elements.append(t_duo)
    elements.append(Spacer(1, 8))

    # FOOTER NOTE
    gen_time = datetime.now().strftime("%d %B %Y, %H:%M WIB")
    footer_text = Paragraph(
        f"<i>RuteStrip Mountain Guidebook • Dokumen navigasi offline resmi untuk pendaki • Dibuat pada: {gen_time}</i>",
        subtitle_style
    )
    elements.append(footer_text)

    # Build Document
    doc.build(elements)
    return output_path

if __name__ == "__main__":
    q = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "sumbing kaliangkrik"
    try:
        pdf_path = generate_guidebook_pdf(q)
        print(f"GUIDEBOOK:{pdf_path}")
    except Exception as e:
        print(f"ERROR:{e}")
