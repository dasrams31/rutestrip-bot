import os
import sys
import glob
import re
import math
import json
import subprocess
from typing import Optional
from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

sys.path.append('/root/rutestrip-bot')
from rekomendasi_pendakian import RecommendationSystem
import satellite_map
import gpx_exporter
import itinerary_logistics
import survival_budget
import porter_transport
import cek_cuaca_gunung
import info_rutestrip
import subscriber_report
import broadcast_channel_bulletin
import broadcast_weekend_getaway
import broadcast_survival_tips
import broadcast_bot_usage

app = FastAPI(
    title='RuteStrip Pendakian API',
    description='REST API Asisten Pendakian Gunung (Rekomendasi, Cuaca, GPX, Satelit, Logistik, Bulletin, Stats & Community Info)',
    version='1.2.0'
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

rec_system = RecommendationSystem()
rec_system.index_directory('/root/rutestrip-bot/gpx_db', use_cache=True)

@app.get('/')
def root():
    return {
        'status': 'online',
        'service': 'RuteStrip Pendakian Bot REST API',
        'version': '1.2.0',
        'docs_url': '/docs'
    }

@app.get('/api/info', summary='Informasi Resmi Komunitas & Platform RuteStrip')
def get_info():
    info_path = '/root/rutestrip-bot/info_rutestrip.json'
    if os.path.exists(info_path):
        with open(info_path, 'r') as f:
            data = json.load(f)
        return {'status': 'success', 'data': data}
    return {'status': 'success', 'data': {
        'website': 'https://rutestrip.web.id',
        'ai_chat': 'https://airutestrip.web.id',
        'telegram_group': '@rutestrip_group',
        'telegram_channel': '@rutestrip'
    }}

@app.get('/api/news/bulletin', summary='Daily Mountain Bulletin & News Realtime')
def get_bulletin():
    bulletin_text = broadcast_channel_bulletin.generate_bulletin()
    return {'status': 'success', 'bulletin': bulletin_text}

@app.get('/api/getaway', summary='Rekomendasi Rute Harian & Weekend Getaway')
def get_daily_getaway():
    item = broadcast_weekend_getaway.get_next_recommendation()
    return {'status': 'success', 'recommendation': item}

@app.get('/api/survival/tips', summary='Edukasi Survival & Etika Pendaki Harian')
def get_survival_tips():
    item = broadcast_survival_tips.get_next_tips()
    return {'status': 'success', 'tips': item}

@app.get('/api/stats/subscribers', summary='Statistik & Laporan Pengguna Bot')
def get_subscriber_stats():
    report_text = subscriber_report.generate_report()
    subscribers_path = '/root/rutestrip-bot/subscribers.json'
    sub_data = {}
    if os.path.exists(subscribers_path):
        with open(subscribers_path, 'r') as f:
            sub_data = json.load(f)
    return {
        'status': 'success',
        'total_subscribers': len(sub_data),
        'report_summary': report_text
    }

@app.get('/api/rekomendasi', summary='Rekomendasi Rute AI (SBERT)')
def get_recommendation(query: str = Query(..., description='Kata kunci kriteria pendakian'), limit: int = 5):
    results = rec_system.search(query, top_n=limit)
    formatted = []
    for r in results:
        item = r['item']
        formatted.append({
            'mountain_route': item['name'],
            'similarity_score': round(r['similarity'], 4),
            'stats': item['stats'],
            'narrative': item['narrative']
        })
    return {'query': query, 'total': len(formatted), 'results': formatted}

@app.get('/api/cuaca', summary='Prakiraan Cuaca Live Realtime (Open-Meteo)')
def get_weather(mountain: Optional[str] = Query(None, description='Nama gunung')):
    weather_text = cek_cuaca_gunung.check_all_weather()
    if mountain:
        lines = [line for line in weather_text.splitlines() if mountain.lower() in line.lower()]
        return {'mountain': mountain, 'weather_info': lines if lines else weather_text}
    return {'weather_info': weather_text}

def get_safe_mountain_name(mtn: str) -> str:
    clean = re.sub(r'[^a-zA-Z0-9]', '', (mtn or '').lower().strip())
    noise_words = ['topografinya', 'satelitnya', 'petanya', 'peta', 'topo', 'topografi', 'satelit', 'foto', 'gambar']
    if not clean or clean in noise_words or len(clean) < 3:
        return 'merbabu'
    gpx = gpx_exporter.find_gpx(clean)
    if not gpx or not os.path.exists(gpx):
        return 'merbabu'
    return clean

@app.get('/api/map/satellite', summary='Peta Satelit / Topografi Kontur (PNG)')
def get_satellite_map(mountain: str = Query('merbabu', description='Nama gunung'), map_type: str = Query('satelit', description='satelit atau topografi')):
    safe_mtn = get_safe_mountain_name(mountain)
    clean_type = map_type.lower().strip()
    output_path = f'/tmp/api_map_{safe_mtn}_{clean_type}.png'
    
    if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
        return FileResponse(output_path, media_type='image/png', filename=f'map_{safe_mtn}.png')
    
    q_str = f'{safe_mtn} topo' if clean_type in ['topografi', 'topo'] else safe_mtn
    try:
        res_path = satellite_map.generate_satellite_map(query=q_str, output_img=output_path)
        return FileResponse(res_path, media_type='image/png', filename=f'map_{safe_mtn}.png')
    except Exception as e:
        fallback_path = f'/tmp/api_map_merbabu_{clean_type}.png'
        try:
            res_path = satellite_map.generate_satellite_map(query=('merbabu topo' if clean_type in ['topografi', 'topo'] else 'merbabu'), output_img=fallback_path)
            return FileResponse(res_path, media_type='image/png', filename='map_merbabu.png')
        except Exception:
            return JSONResponse({'status': 'fallback', 'message': 'Map rendered default'}, status_code=200)

@app.get('/api/gpx', summary='Export File GPX / KML Track Offline')
def get_gpx_file(mountain: str = Query('merbabu', description='Nama gunung'), format: str = Query('gpx', description='gpx atau kml')):
    safe_mtn = get_safe_mountain_name(mountain)
    filepath = gpx_exporter.find_gpx(safe_mtn) or gpx_exporter.find_gpx('merbabu')
    if not filepath or not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail=f'File GPX tidak ditemukan.')
    
    if format.lower() == 'kml':
        kml_path = gpx_exporter.gpx_to_kml(filepath)
        return FileResponse(kml_path, media_type='application/vnd.google-earth.kml+xml', filename=f'{safe_mtn}.kml')
    
    return FileResponse(filepath, media_type='application/gpx+xml', filename=os.path.basename(filepath))

@app.get('/api/itinerary', summary='Naismith Itinerary Generator')
def get_itinerary(mountain: str = Query('merbabu'), mode: str = Query('2d1n')):
    safe_mtn = get_safe_mountain_name(mountain)
    res = subprocess.run(['python3', '/root/rutestrip-bot/itinerary_logistics.py', 'itinerary', safe_mtn, mode], capture_output=True, text=True)
    return {'mountain': safe_mtn, 'mode': mode, 'itinerary': res.stdout.strip()}

@app.get('/api/logistik', summary='Kalkulator Perbekalan Air & Makanan')
def get_logistics(people: int = Query(3), days: int = Query(2)):
    res = subprocess.run(['python3', '/root/rutestrip-bot/itinerary_logistics.py', 'logistics', str(people), str(days)], capture_output=True, text=True)
    return {'people': people, 'days': days, 'logistics': res.stdout.strip()}

@app.get('/api/biaya', summary='Kalkulator Biaya Pendakian')
def get_budget(mountain: str = Query('sumbing'), people: int = Query(3), days: int = Query(2)):
    safe_mtn = get_safe_mountain_name(mountain)
    res = subprocess.run(['python3', '/root/rutestrip-bot/survival_budget.py', 'budget', safe_mtn, str(people), str(days)], capture_output=True, text=True)
    return {'mountain': safe_mtn, 'people': people, 'days': days, 'budget_info': res.stdout.strip()}

@app.get('/api/survival', summary='Panduan Survival First Aid')
def get_survival(topic: str = Query('hipotermia')):
    res = subprocess.run(['python3', '/root/rutestrip-bot/survival_budget.py', 'survival', topic], capture_output=True, text=True)
    return {'topic': topic, 'guide': res.stdout.strip()}

@app.get('/api/porter', summary='Kontak Porter & Basecamp')
def get_porter(mountain: str = Query('sumbing')):
    safe_mtn = get_safe_mountain_name(mountain)
    res = subprocess.run(['python3', '/root/rutestrip-bot/porter_transport.py', safe_mtn], capture_output=True, text=True)
    return {'mountain': safe_mtn, 'porter_info': res.stdout.strip()}
