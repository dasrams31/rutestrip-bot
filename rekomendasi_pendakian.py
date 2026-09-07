import os
import glob
import re
import math
import json
import numpy as np
import gpxpy
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

CACHE_FILE = "/tmp/routes_cache.json"

STOPWORDS_ID = {
    'yang', 'dan', 'di', 'ke', 'dari', 'ini', 'itu', 'dengan', 'untuk', 'pada',
    'adalah', 'sebagai', 'dalam', 'juga', 'atau', 'ada', 'oleh', 'akan', 'sudah',
    'saya', 'kami', 'kita', 'mereka', 'dia', 'ia', 'anda', 'tersebut', 'dapat',
    'bisa', 'harus', 'telah', 'lalu', 'kemudian', 'serta', 'maupun', 'saat',
    'ketika', 'bila', 'kalau', 'jika', 'karena', 'agar', 'supaya', 'hingga',
    'sampai', 'antara', 'seperti', 'yaitu', 'yakni', 'bahwa', 'namun', 'tetapi'
}

PRESERVE_WORDS = {
    'tidak', 'bukan', 'jangan', 'belum', 'tanpa',
    'mudah', 'sulit', 'curam', 'landai', 'panjang', 'pendek',
    'tinggi', 'rendah', 'sejuk', 'panas', 'dingin', 'indah', 'bagus',
    'pemula', 'berpengalaman', 'santai', 'menantang', 'ekstrem'
}

def preprocess_text(text: str, remove_stopwords: bool = True) -> str:
    if not text:
        return ""
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    text = re.sub(r'[^\w\s\-]', ' ', text)
    text = re.sub(r'\b\d+\b', '', text)
    text = re.sub(r'\s+', ' ', text).strip().lower()

    if remove_stopwords:
        words = text.split()
        filtered = [w for w in words if w in PRESERVE_WORDS or w not in STOPWORDS_ID]
        text = ' '.join(filtered)
    return text

def parse_gpx(gpx_path):
    with open(gpx_path, 'r', encoding='utf-8', errors='ignore') as f:
        gpx = gpxpy.parse(f)
    points = []
    wpts = []
    
    for wpt in gpx.waypoints:
        wpts.append(wpt.name if wpt.name else "Pos")

    for track in gpx.tracks:
        for segment in track.segments:
            for pt in segment.points:
                points.append({
                    'lat': pt.latitude,
                    'lon': pt.longitude,
                    'ele': pt.elevation if pt.elevation else 0
                })
    return gpx, points, wpts

def calculate_statistics(gpx, points):
    dist_km = gpx.length_3d() / 1000.0 if points else 0.0
    gain_m = 0.0
    for i in range(1, len(points)):
        diff = points[i]['ele'] - points[i-1]['ele']
        if diff > 0:
            gain_m += diff
    
    # Naismith: Naik = (KM/5) + (Gain/600), Turun = ~60% dari waktu naik
    ascent_hrs = (dist_km / 5.0) + (gain_m / 600.0)
    round_trip_hrs = round(ascent_hrs * 1.6, 2)
    grade = (gain_m / (dist_km * 1000.0) * 100.0) if dist_km > 0 else 0.0

    if grade < 5:
        diff_str = "mudah"
    elif grade < 10:
        diff_str = "sedang"
    elif grade < 15:
        diff_str = "sulit"
    else:
        diff_str = "sangat sulit"

    eles = [p['ele'] for p in points if p['ele'] > 0]
    min_ele = min(eles) if eles else 0
    max_ele = max(eles) if eles else 0

    return {
        'distance_km': round(dist_km, 2),
        'elevation_gain_m': int(gain_m),
        'naismith_duration_hour': round_trip_hrs,
        'average_grade_pct': round(grade, 2),
        'min_elevation': int(min_ele),
        'max_elevation': int(max_ele),
        'difficulty': diff_str
    }

def generate_narrative(stats, route_name, waypoints=None):
    j_desc = "pendek" if stats['distance_km'] < 8 else ("sedang" if stats['distance_km'] < 14 else "panjang")
    w_desc = "singkat" if stats['naismith_duration_hour'] < 5 else ("sedang" if stats['naismith_duration_hour'] < 9 else "lama")
    
    if stats['average_grade_pct'] < 5:
        g_desc = "landai dan sangat ramah pemula"
    elif stats['average_grade_pct'] < 10:
        g_desc = "menantang dengan kemiringan sedang"
    elif stats['average_grade_pct'] < 15:
        g_desc = "curam dan butuh stamina fisik prima"
    else:
        g_desc = "sangat curam dan ekstrem"

    wpt_str = f" Pos lintasan: {', '.join(waypoints[:5])}." if waypoints else ""

    return (
        f"Rute pendakian {route_name} dengan jarak {j_desc} {stats['distance_km']} km. "
        f"Estimasi durasi total PP {w_desc} {stats['naismith_duration_hour']} jam. "
        f"Karakteristik trek {g_desc} (grade {stats['average_grade_pct']}%). "
        f"Elevation gain {stats['elevation_gain_m']}m, elevasi {stats['min_elevation']}m - {stats['max_elevation']}m. "
        f"Tingkat kesulitan: {stats['difficulty']}.{wpt_str}"
    )

class RecommendationSystem:
    def __init__(self, model_name='sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'):
        self.model_name = model_name
        self.model = None
        self.db = []

    def _load_model(self):
        if self.model is None:
            self.model = SentenceTransformer(self.model_name)

    def index_directory(self, gpx_dir, use_cache=True):
        if use_cache and os.path.exists(CACHE_FILE):
            try:
                with open(CACHE_FILE, "r") as f:
                    self.db = json.load(f)
                return
            except Exception:
                pass

        self._load_model()
        gpx_files = glob.glob(os.path.join(gpx_dir, "*.gpx"))
        self.db = []
        for path in gpx_files:
            fname = os.path.basename(path)
            clean_name = re.sub(r'^doc_[a-f0-9]+_', '', fname).replace('.gpx', '')
            try:
                gpx, points, wpts = parse_gpx(path)
                if not points:
                    continue
                stats = calculate_statistics(gpx, points)
                narrative = generate_narrative(stats, clean_name, wpts)
                proc_narrative = preprocess_text(narrative, remove_stopwords=False)
                emb = self.model.encode(proc_narrative).tolist()

                self.db.append({
                    'name': clean_name,
                    'path': path,
                    'stats': stats,
                    'narrative': narrative,
                    'embedding': emb
                })
            except Exception as e:
                print(f"Error indexing {path}: {e}")

        # Save cache
        try:
            with open(CACHE_FILE, "w") as f:
                json.dump(self.db, f)
        except Exception as e:
            print(f"Cache write error: {e}")

    def search(self, query, top_n=3):
        if not self.db:
            return []
        self._load_model()
        proc_q = preprocess_text(query, remove_stopwords=True)
        q_emb = self.model.encode(proc_q)

        # Extraction for numerical hard constraints (e.g. "dibawah 15km", "dibawah 6 jam")
        max_dist = None
        m_dist = re.search(r'(?:dibawah|kurang dari|<)\s*(\d+)\s*km', query.lower())
        if m_dist:
            max_dist = float(m_dist.group(1))

        results = []
        for item in self.db:
            if max_dist and item['stats']['distance_km'] > max_dist:
                continue
            sim = cosine_similarity([q_emb], [item['embedding']])[0][0]
            results.append({
                'item': item,
                'similarity': float(sim)
            })

        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results[:top_n]

if __name__ == '__main__':
    import sys
    query = sys.argv[1] if len(sys.argv) > 1 else "jalur landai ramah pemula"
    rec = RecommendationSystem()
    rec.index_directory('/home/ubuntu/.hermes/cache/documents')
    res = rec.search(query, top_n=3)
    print(json.dumps(res, indent=2))
