import os
import sys
import glob
import re
import math
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

app = FastAPI(
    title='RuteStrip Pendakian API',
    description='REST API Asisten Pendakian Gunung (SBERT Recommendation, Weather, GPX Exporter, Satellite Map, Logistics & Survival)',
    version='1.0.0'
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
        'version': '1.0.0',
        'docs_url': '/docs'
    }

@app.get('/api/rekomendasi')
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

@app.get('/api/cuaca')
def get_weather(mountain: Optional[str] = Query(None, description='Nama gunung')):
    weather_text = cek_cuaca_gunung.check_all_weather()
    if mountain:
        lines = [line for line in weather_text.splitlines() if mountain.lower() in line.lower()]
        return {'mountain': mountain, 'weather_info': lines if lines else weather_text}
    return {'weather_info': weather_text}

@app.get('/api/map/satellite')
def get_satellite_map(mountain: str = Query('sumbing', description='Nama gunung'), map_type: str = Query('satelit', description='satelit atau topografi')):
    output_path = f'/tmp/api_map_{mountain}_{map_type}.png'
    q_str = f'{mountain} topo' if map_type.lower() in ['topografi', 'topo'] else mountain
    try:
        res_path = satellite_map.generate_satellite_map(query=q_str, output_img=output_path)
        return FileResponse(res_path, media_type='image/png', filename=f'map_{mountain}.png')
    except Exception as e:
        raise HTTPException(status_code=404, detail=f'File GPX trek untuk gunung {mountain} tidak ditemukan.')

@app.get('/api/gpx')
def get_gpx_file(mountain: str = Query(..., description='Nama gunung'), format: str = Query('gpx', description='gpx atau kml')):
    filepath = gpx_exporter.find_gpx(mountain)
    if not filepath or not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail=f'File GPX untuk {mountain} tidak ditemukan.')
    
    if format.lower() == 'kml':
        kml_path = gpx_exporter.gpx_to_kml(filepath)
        return FileResponse(kml_path, media_type='application/vnd.google-earth.kml+xml', filename=f'{mountain}.kml')
    
    return FileResponse(filepath, media_type='application/gpx+xml', filename=os.path.basename(filepath))

@app.get('/api/itinerary')
def get_itinerary(mountain: str = Query(..., description='Nama gunung'), mode: str = Query('2d1n', description='2d1n atau tektok')):
    res = subprocess.run(['python3', '/root/itinerary_logistics.py', 'itinerary', mountain, mode], capture_output=True, text=True)
    return {'mountain': mountain, 'mode': mode, 'itinerary': res.stdout.strip()}

@app.get('/api/logistik')
def get_logistics(people: int = Query(3), days: int = Query(2)):
    res = subprocess.run(['python3', '/root/itinerary_logistics.py', 'logistics', str(people), str(days)], capture_output=True, text=True)
    return {'people': people, 'days': days, 'logistics': res.stdout.strip()}

@app.get('/api/biaya')
def get_budget(mountain: str = Query('sumbing'), people: int = Query(3), days: int = Query(2)):
    res = subprocess.run(['python3', '/root/survival_budget.py', 'budget', mountain, str(people), str(days)], capture_output=True, text=True)
    return {'mountain': mountain, 'people': people, 'days': days, 'budget_info': res.stdout.strip()}

@app.get('/api/survival')
def get_survival(topic: str = Query('hipotermia')):
    res = subprocess.run(['python3', '/root/survival_budget.py', 'survival', topic], capture_output=True, text=True)
    return {'topic': topic, 'guide': res.stdout.strip()}

@app.get('/api/porter')
def get_porter(mountain: str = Query('sumbing')):
    res = subprocess.run(['python3', '/root/porter_transport.py', mountain], capture_output=True, text=True)
    return {'mountain': mountain, 'porter_info': res.stdout.strip()}
