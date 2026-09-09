import re

# Kata kunci yang relevan dengan domain RuteStrip Pendakian
ALLOWED_KEYWORDS = [
    'gunung', 'pendakian', 'muncak', 'tektok', 'basecamp', 'pos', 'kawah', 'puncak', 'sabana',
    'cuaca', 'hujan', 'angin', 'suhu', 'gpx', 'kml', 'peta', 'satelit', 'topografi', 'elevasi',
    'itinerary', 'logistik', 'air', 'makanan', 'biaya', 'simaksi', 'ojek', 'porter',
    'survival', 'hipotermia', 'ams', 'first aid', 'darurat', 'tenda', 'sb', 'sleeping bag',
    'carrier', 'sepatu', 'jaket', 'ponco', 'info', 'komunitas', 'website', 'rutestrip',
    'jalur', 'rute', 'rekomendasi', 'trek', 'tracking', 'dieng', 'sumbing', 'merbabu', 'slamet',
    'sindoro', 'lawu', 'prau', 'semeru', 'merapi', 'bromo', 'arjuno', 'welirang', 'raung',
    'rinjani', 'ijen', 'cikuray', 'guntur', 'papandayan', 'gede', 'pangrango', 'salak', 'ciremai',
    'andong', 'kembang', 'ungaran', 'pemula', 'camp', 'camping'
]

# Kata kunci sensitif / sistem yang wajib diblokir
BLOCKED_PATTERNS = [
    r'\.\./', r'/etc/', r'/var/', r'/proc/', r'/sys/', r'/root',
    r'sudo', r'rm\s', r'chmod', r'chown', r'exec', r'eval',
    r'system', r'bash', r'fastapi', r'swagger', r'uvicorn', r'tunnel', r'cloudflared',
    r'trycloudflare', r'8000', r'/docs', r'openapi', r'endpoint'
]

OUT_OF_SCOPE_MSG = "Maaf, saya adalah RuteStrip AI Assistant yang khusus diprogram untuk membantu informasi pendakian gunung, cuaca live, rute trek, logistik, dan survival outdoor. Ada informasi pendakian gunung yang bisa saya bantu? 🏔️"

SYSTEM_BLOCKED_MSG = "Maaf, informasi sistem dan API backend bersifat rahasia dan hanya dapat diakses oleh Admin (@dasrams). Ada informasi pendakian gunung yang bisa saya bantu? 🏔️"

def validate_webchat_query(prompt: str) -> dict:
    text = (prompt or "").strip()
    if not text:
        return {"allowed": False, "message": OUT_OF_SCOPE_MSG}

    # 1. Pengecekan Sistem & Keamanan (Anti Injection)
    for pat in BLOCKED_PATTERNS:
        if re.search(pat, text, re.IGNORECASE):
            return {"allowed": False, "message": SYSTEM_BLOCKED_MSG}

    # 2. Pengecekan Relevansi Topik Pendakian (Domain Scope)
    text_lower = text.lower()
    is_relevant = any(kw in text_lower for kw in ALLOWED_KEYWORDS)

    if not is_relevant:
        return {"allowed": False, "message": OUT_OF_SCOPE_MSG}

    return {"allowed": True, "clean_prompt": text}
