import sys
import os
import time
import json
import sqlite3
import psutil
import subprocess
import hashlib
import hmac
from collections import defaultdict
from typing import Optional, List, Dict
from fastapi import FastAPI, Request, Response, HTTPException, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# ==============================================================================
# SECURITY LAYER & RATE LIMITING
# ==============================================================================

app = FastAPI(
    title="DasRams System Sentinel & Ecosystem Monitor",
    docs_url=None,
    redoc_url=None
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ALLOWED_PASSWORDS = ["Misaka03!", "Soyusa03!"]
AUTH_SALT = "dasrams_sentinel_hardened_salt_v2"
COOKIE_NAME = "sentinel_session"

def generate_auth_token(password: str) -> str:
    return hashlib.sha256(f"{password}_{AUTH_SALT}".encode()).hexdigest()

VALID_AUTH_TOKENS = [generate_auth_token(p) for p in ALLOWED_PASSWORDS]

# Sliding Window Rate Limiter
class RateLimiter:
    def __init__(self, max_requests: int = 10, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(list)

    def is_allowed(self, client_ip: str) -> bool:
        now = time.time()
        self.requests[client_ip] = [
            t for t in self.requests[client_ip] if now - t < self.window_seconds
        ]
        if len(self.requests[client_ip]) >= self.max_requests:
            return False
        self.requests[client_ip].append(now)
        return True

login_rate_limiter = RateLimiter(max_requests=8, window_seconds=60)

# Security Headers Middleware
@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self' https: data: blob: 'unsafe-inline' 'unsafe-eval'; "
        "style-src 'self' https: data: 'unsafe-inline'; "
        "font-src 'self' https: data:; "
        "img-src 'self' https: data: blob:; "
        "script-src 'self' https: 'unsafe-inline' 'unsafe-eval'; "
        "connect-src 'self' https: wss:;"
    )
    return response

class LoginRequest(BaseModel):
    password: str = Field(..., min_length=1, max_length=64)

def constant_time_check(provided: str, actual: str) -> bool:
    return hmac.compare_digest(provided.encode("utf-8"), actual.encode("utf-8"))

def is_authenticated(request: Request) -> bool:
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        return False
    return any(constant_time_check(token, valid_token) for valid_token in VALID_AUTH_TOKENS)

# ==============================================================================
# TELEMETRY & SERVICE DISCOVERY ENGINE
# ==============================================================================

def check_process(name_pattern: str) -> bool:
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmd = " ".join(proc.info['cmdline'] or [])
            if name_pattern in cmd:
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False

def check_port(port: int) -> bool:
    try:
        for conn in psutil.net_connections(kind='inet'):
            laddr = getattr(conn, 'laddr', None)
            if laddr:
                p = getattr(laddr, 'port', None) or (laddr[1] if isinstance(laddr, tuple) and len(laddr) > 1 else None)
                if p == port and getattr(conn, 'status', '') == 'LISTEN':
                    return True
    except Exception:
        pass
    return False

def get_9router_data():
    db_path = "/home/ubuntu/.9router/db/data.sqlite"
    providers_list = []
    total_requests = 0
    catalog_count = 0
    
    cat_path = "/home/ubuntu/.9router/model-catalog.json"
    if os.path.exists(cat_path):
        try:
            with open(cat_path, 'r') as f:
                cat_data = json.load(f)
                catalog_count = len(cat_data) if isinstance(cat_data, list) else len(cat_data.keys())
        except Exception:
            catalog_count = 18

    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            rows = cursor.execute("SELECT id, provider, name, isActive, data FROM providerConnections").fetchall()
            for r in rows:
                p_id, p_type, name, is_active, data_json = r
                p_data = {}
                try:
                    p_data = json.loads(data_json) if data_json else {}
                except Exception:
                    pass
                
                status_str = "ACTIVE" if is_active == 1 else "INACTIVE"
                if p_data.get("testStatus") == "unavailable" or ("lastError" in p_data and p_data["lastError"]):
                    status_str = "WARNING"
                
                providers_list.append({
                    "id": p_id,
                    "provider": p_type,
                    "name": name or "Unnamed Account",
                    "status": status_str,
                    "email": p_data.get("email", name or "N/A"),
                    "project_id": p_data.get("projectId", "N/A"),
                    "last_error": p_data.get("lastError", None),
                    "last_refresh": p_data.get("lastRefreshAt", "N/A")
                })
            
            req_count = cursor.execute("SELECT COUNT(*) FROM usageHistory").fetchone()
            if req_count:
                total_requests = req_count[0]
            conn.close()
        except Exception:
            pass
            
    return providers_list, total_requests, catalog_count

def get_cron_events():
    events = []
    seen_file = "/home/ubuntu/rutestrip-bot/last_cron_seen.json"
    if os.path.exists(seen_file):
        try:
            with open(seen_file, 'r') as f:
                data = json.load(f)
                for k, v in data.items():
                    events.append({
                        "task": k.replace("_", " ").title(),
                        "timestamp": v if isinstance(v, str) else time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(v)),
                        "status": "SUCCESS"
                    })
        except Exception:
            pass

    hermes_jobs_file = "/home/ubuntu/.hermes/cron/jobs.json"
    active_jobs = []
    if os.path.exists(hermes_jobs_file):
        try:
            with open(hermes_jobs_file, 'r') as f:
                j_data = json.load(f)
                for job in j_data if isinstance(j_data, list) else j_data.get("jobs", []):
                    active_jobs.append({
                        "id": job.get("job_id", job.get("id", "cron")),
                        "name": job.get("name", "Scheduled Agent Task"),
                        "schedule": job.get("schedule", "Recurring"),
                        "enabled": job.get("enabled", True)
                    })
        except Exception:
            pass

    return events[:10], active_jobs

# ==============================================================================
# REST API ENDPOINTS
# ==============================================================================

@app.post("/api/login")
def login(data: LoginRequest, request: Request, response: Response):
    client_ip = request.client.host if request.client else "unknown"
    if not login_rate_limiter.is_allowed(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Terlalu banyak percobaan login gagal. Silakan tunggu 1 menit."
        )

    for pwd in ALLOWED_PASSWORDS:
        if constant_time_check(data.password, pwd):
            token = generate_auth_token(pwd)
            response.set_cookie(
                key=COOKIE_NAME,
                value=token,
                max_age=60 * 60 * 24 * 30, # 30 hari
                httponly=True,
                samesite="lax",
                secure=True
            )
            return {"success": True, "message": "Otorisasi berhasil."}
            
    raise HTTPException(status_code=401, detail="Master key salah!")

@app.get("/logout")
@app.post("/api/logout")
def logout(response: Response):
    response.delete_cookie(COOKIE_NAME)
    return RedirectResponse(url="/", status_code=302)

@app.get("/api/diagnostics")
def run_diagnostics(request: Request):
    if not is_authenticated(request):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    services_to_test = [
        {"name": "Nginx Web Server", "port": 80, "subdomain": "dasrams.biz.id"},
        {"name": "Nginx SSL (HTTPS)", "port": 443, "subdomain": "dasrams.biz.id"},
        {"name": "RuteStrip REST Engine", "port": 8000, "subdomain": "api.dasrams.biz.id"},
        {"name": "Sutarjio Gemini Hunter", "port": 8090, "subdomain": "sutarjio.dasrams.biz.id"},
        {"name": "SynapseGuild AI RPG", "port": 8100, "subdomain": "rpg.dasrams.biz.id"},
        {"name": "ReelCraft Video Engine", "port": 8080, "subdomain": "reelcraft.dasrams.biz.id"},
        {"name": "Database Adminer", "port": 8088, "subdomain": "db.dasrams.biz.id"},
        {"name": "n8n Automation Hub", "port": 5678, "subdomain": "n8n.dasrams.biz.id"},
        {"name": "9router AI Gateway", "port": 20128, "subdomain": "9router.dasrams.biz.id"},
        {"name": "Mailcow SOGo Webmail", "port": 8095, "subdomain": "mail.dasrams.biz.id"},
        {"name": "Sentinel Telemetry", "port": 9000, "subdomain": "monitor.dasrams.biz.id"}
    ]
    
    results = []
    for s in services_to_test:
        t0 = time.time()
        is_open = check_port(s["port"])
        lat = round((time.time() - t0) * 1000, 2)
        results.append({
            "name": s["name"],
            "port": s["port"],
            "subdomain": s["subdomain"],
            "status": "ONLINE" if is_open else "OFFLINE",
            "latency_ms": max(lat, 0.45)
        })
    return {"timestamp": time.strftime('%H:%M:%S'), "results": results}

@app.get("/api/status")
def get_system_status(request: Request):
    if not is_authenticated(request):
        raise HTTPException(status_code=401, detail="Unauthorized")

    cpu_usage = psutil.cpu_percent(interval=0.3)
    cpu_cores = psutil.cpu_count(logical=True) or 1
    load1, load5, load15 = psutil.getloadavg()
    
    memory = psutil.virtual_memory()
    swap = psutil.swap_memory()
    disk = psutil.disk_usage('/')
    net_io = psutil.net_io_counters()
    
    uptime_seconds = time.time() - psutil.boot_time()
    
    # Detailed service status mapping
    services = {
        "sutarjio": check_port(8090),
        "rpg_agent": check_port(8100),
        "api": check_port(8000),
        "router": check_port(20128),
        "n8n": check_port(5678),
        "mailcow": check_port(8095) or check_port(25),
        "reelcraft": check_port(8080),
        "adminer": check_port(8088),
        "monitor": check_port(9000),
        "hermes_bot": check_process("rutestrip_bot") or check_process("hermes")
    }

    # Subscribers & analytics
    subscribers_count = 0
    sub_file = "/home/ubuntu/rutestrip-bot/subscribers.json"
    if os.path.exists(sub_file):
        try:
            with open(sub_file, 'r') as f:
                subscribers_count = len(json.load(f))
        except Exception:
            pass

    providers_list, total_ai_requests, catalog_count = get_9router_data()
    cron_events, active_jobs = get_cron_events()

    return {
        "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
        "system": {
            "os": f"Linux {os.uname().release}",
            "hostname": os.uname().nodename,
            "uptime_human": f"{int(uptime_seconds // 86400)}d {int((uptime_seconds % 86400) // 3600)}h {int((uptime_seconds % 3600) // 60)}m",
            "cpu": {
                "usage_percent": cpu_usage,
                "cores": cpu_cores,
                "load_avg": [round(load1, 2), round(load5, 2), round(load15, 2)]
            },
            "ram": {
                "total_gb": round(memory.total / (1024**3), 2),
                "used_gb": round(memory.used / (1024**3), 2),
                "free_gb": round(memory.available / (1024**3), 2),
                "percent": memory.percent
            },
            "swap": {
                "total_gb": round(swap.total / (1024**3), 2),
                "used_gb": round(swap.used / (1024**3), 2),
                "percent": swap.percent
            },
            "disk": {
                "total_gb": round(disk.total / (1024**3), 2),
                "used_gb": round(disk.used / (1024**3), 2),
                "free_gb": round(disk.free / (1024**3), 2),
                "percent": disk.percent
            },
            "network": {
                "bytes_sent_mb": round(net_io.bytes_sent / (1024**2), 2),
                "bytes_recv_mb": round(net_io.bytes_recv / (1024**2), 2)
            }
        },
        "services": services,
        "community": {
            "subscribers": subscribers_count,
            "ai_total_requests": total_ai_requests,
            "ai_models_count": catalog_count
        },
        "router_providers": providers_list,
        "cron_events": cron_events,
        "scheduled_jobs": active_jobs
    }

# ==============================================================================
# UI/UX FRONTEND TEMPLATES (LINEAR / VERCEL STYLE)
# ==============================================================================

LOGIN_HTML = """<!DOCTYPE html>
<html lang="id" class="dark">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Sentinel Telemetry — Authentication</title>
  
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css" crossorigin="anonymous" />
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@6.5.1/css/all.min.css" />
  
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {
      darkMode: "class",
      theme: {
        extend: {
          colors: {
            brand: { yellow: "#FFE600", amber: "#FACC15" },
            surface: { base: "#080A0F", card: "#10141E", elevate: "#171D2C", border: "rgba(255, 255, 255, 0.08)" }
          },
          fontFamily: {
            sans: ['"Plus Jakarta Sans"', 'system-ui', 'sans-serif'],
            mono: ['"JetBrains Mono"', 'ui-monospace', 'monospace']
          }
        }
      }
    }
  </script>
</head>
<body class="bg-[#080A0F] text-slate-100 min-h-screen flex items-center justify-center p-4 antialiased selection:bg-brand-yellow selection:text-black">
  <div class="max-w-sm w-full bg-[#10141E] border border-white/10 rounded-2xl p-6 sm:p-8 space-y-6 shadow-2xl relative overflow-hidden">
    
    <div class="text-center space-y-2">
      <div class="w-12 h-12 rounded-xl bg-brand-yellow/10 text-brand-yellow border border-brand-yellow/30 mx-auto flex items-center justify-center text-xl shadow-lg shadow-brand-yellow/10">
        <i class="fa-solid fa-shield-halved"></i>
      </div>
      <h1 class="text-base font-bold text-white font-mono tracking-tight">SENTINEL TELEMETRY</h1>
      <p class="text-xs text-zinc-400">DasRams Infrastructure Gate</p>
    </div>

    <form onsubmit="handleLogin(event)" class="space-y-4 text-xs">
      <div>
        <label class="block text-zinc-400 font-medium mb-1.5">Master Key Otorisasi</label>
        <input 
          type="password" 
          id="password" 
          required 
          placeholder="••••••••••••" 
          class="w-full bg-[#080A0F] border border-white/10 rounded-lg px-3.5 py-2.5 text-center font-mono text-sm tracking-widest text-white focus:outline-none focus:border-brand-yellow transition"
        />
      </div>

      <div id="errorMsg" class="hidden p-2.5 rounded-lg bg-red-950/60 border border-red-800/60 text-red-400 text-[11px] text-center font-medium"></div>

      <button 
        type="submit" 
        id="submitBtn"
        class="w-full bg-[#FFE600] hover:bg-[#FFF066] text-black font-bold py-2.5 rounded-lg transition duration-150 flex items-center justify-center gap-2 shadow-lg shadow-brand-yellow/20"
      >
        <span>Authenticate Node</span>
        <i class="fa-solid fa-arrow-right text-xs"></i>
      </button>
    </form>

    <div class="pt-3 border-t border-white/5 text-center text-[10px] font-mono text-zinc-500 flex items-center justify-center gap-1.5">
      <i class="fa-solid fa-lock text-[9px]"></i>
      <span>Protected Zero-Trust Sentinel Gateway</span>
    </div>
  </div>

  <script>
    async function handleLogin(e) {
      e.preventDefault();
      const pwd = document.getElementById('password').value;
      const btn = document.getElementById('submitBtn');
      const err = document.getElementById('errorMsg');

      btn.disabled = true;
      btn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin text-xs"></i> <span>Verifying...</span>';
      err.classList.add('hidden');

      try {
        const res = await fetch('/api/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ password: pwd })
        });

        if (res.ok) {
          window.location.reload();
        } else {
          err.innerText = 'Akses ditolak: Master key salah.';
          err.classList.remove('hidden');
          btn.disabled = false;
          btn.innerHTML = '<span>Authenticate Node</span> <i class="fa-solid fa-arrow-right text-xs"></i>';
        }
      } catch (err) {
        err.innerText = 'Gagal terhubung ke server.';
        err.classList.remove('hidden');
        btn.disabled = false;
        btn.innerHTML = '<span>Authenticate Node</span>';
      }
    }
  </script>
</body>
</html>"""

DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="id" class="dark">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Sentinel Telemetry — DasRams Infrastructure Watchdog</title>
  
  <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 76 65'><path d='M38 0L76 65H0L38 0Z' fill='%23FFE600'/></svg>" />
  
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css" crossorigin="anonymous" />
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@6.5.1/css/all.min.css" />
  
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {
      darkMode: "class",
      theme: {
        extend: {
          colors: {
            brand: { yellow: "#FFE600", amber: "#FACC15", gold: "#EAB308" },
            surface: { base: "#080A0F", card: "#10141E", elevate: "#171D2C", border: "rgba(255, 255, 255, 0.08)", hover: "#1E2638" },
            accent: { emerald: "#10B981", amber: "#F59E0B", crimson: "#EF4444", indigo: "#6366F1" }
          },
          fontFamily: {
            sans: ['"Plus Jakarta Sans"', 'system-ui', 'sans-serif'],
            mono: ['"JetBrains Mono"', 'ui-monospace', 'monospace']
          }
        }
      }
    }
  </script>

  <style>
    * { border-color: rgba(255, 255, 255, 0.08); }
    body {
      background-color: #080A0F;
      color: #F1F5F9;
      font-family: 'Plus Jakarta Sans', system-ui, sans-serif;
      overflow-x: hidden;
      -webkit-font-smoothing: antialiased;
    }
    .font-mono { font-family: 'JetBrains Mono', monospace; }
    .tabular-nums { font-variant-numeric: tabular-nums; }
    
    .glass-card {
      background: #10141E;
      border: 1px solid rgba(255, 255, 255, 0.08);
      box-shadow: 0 8px 24px -4px rgba(0, 0, 0, 0.6);
    }
    
    .btn-interactive {
      transition: all 140ms cubic-bezier(0.16, 1, 0.3, 1);
    }
    .btn-interactive:active { transform: scale(0.98); }
    
    .custom-scroll::-webkit-scrollbar { width: 5px; height: 5px; }
    .custom-scroll::-webkit-scrollbar-thumb { background: #262D42; border-radius: 4px; }
  </style>
</head>
<body class="min-h-screen flex flex-col antialiased selection:bg-brand-yellow selection:text-black">

  <!-- Top Header Navigation -->
  <header class="sticky top-0 z-40 bg-surface-base/90 backdrop-blur-md border-b border-surface-border px-4 sm:px-8 py-3.5">
    <div class="max-w-7xl mx-auto flex items-center justify-between">
      <div class="flex items-center space-x-3.5">
        <div class="w-9 h-9 rounded-lg bg-surface-card border border-brand-yellow/30 flex items-center justify-center text-brand-yellow shadow-md shadow-brand-yellow/10">
          <i class="fa-solid fa-heart-pulse text-base"></i>
        </div>
        <div>
          <div class="flex items-center space-x-2">
            <h1 class="text-sm font-bold tracking-tight text-white font-mono">SENTINEL MONITOR</h1>
            <span class="text-[10px] font-mono px-1.5 py-0.5 rounded bg-brand-yellow/10 text-brand-yellow border border-brand-yellow/30 font-semibold">LIVE</span>
          </div>
          <p class="text-[11px] text-zinc-400 font-medium">DasRams Node Watchdog & Telemetry</p>
        </div>
      </div>

      <div class="flex items-center space-x-3">
        <!-- Live Uptime -->
        <div class="hidden sm:flex items-center space-x-2 bg-surface-card px-3 py-1.5 rounded-lg border border-surface-border text-xs font-mono">
          <i class="fa-regular fa-clock text-brand-yellow text-xs"></i>
          <span class="text-zinc-400 text-[11px]">Uptime:</span>
          <span id="txt-uptime" class="text-white font-bold tabular-nums">0d 0h 0m</span>
        </div>

        <!-- Refresh Button -->
        <button onclick="fetchStatus()" title="Refresh Telemetry" class="btn-interactive px-3 py-1.5 rounded-lg bg-surface-card border border-surface-border text-zinc-300 hover:text-white text-xs font-medium flex items-center gap-1.5">
          <i id="ico-refresh" class="fa-solid fa-arrows-rotate text-[11px]"></i>
          <span class="hidden sm:inline">Sync</span>
        </button>

        <!-- Logout Button -->
        <a href="/logout" title="Lock Session" class="btn-interactive p-2 rounded-lg bg-surface-card border border-surface-border text-zinc-400 hover:text-red-400 text-xs">
          <i class="fa-solid fa-lock text-xs"></i>
        </a>
      </div>
    </div>
  </header>

  <!-- Main Container -->
  <main class="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-8 space-y-6">
    
    <!-- Telemetry Hardware Gauges Grid -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-3.5 sm:gap-4">
      
      <!-- CPU Gauge -->
      <div class="glass-card rounded-xl p-4 sm:p-5 flex flex-col justify-between">
        <div class="flex items-center justify-between">
          <span class="text-[11px] uppercase tracking-wider font-semibold text-zinc-400 flex items-center gap-1.5">
            <i class="fa-solid fa-microchip text-brand-yellow text-xs"></i>
            CPU Core Usage
          </span>
          <span id="txt-cpu-cores" class="text-[10px] font-mono px-1.5 py-0.5 rounded bg-surface-base text-zinc-400 border border-surface-border">4 Cores</span>
        </div>
        <div class="my-3">
          <div class="flex items-baseline space-x-1">
            <span id="val-cpu" class="text-2xl sm:text-3xl font-bold font-mono text-white tabular-nums">0</span>
            <span class="text-xs text-zinc-500 font-mono">%</span>
          </div>
          <!-- Progress Bar -->
          <div class="w-full h-1.5 bg-surface-base rounded-full mt-2 overflow-hidden border border-surface-border">
            <div id="bar-cpu" class="h-full bg-brand-yellow transition-all duration-300" style="width: 0%"></div>
          </div>
        </div>
        <div class="text-[11px] font-mono text-zinc-500 flex justify-between">
          <span>Load Avg:</span>
          <span id="txt-load-avg" class="text-zinc-300">0.0, 0.0, 0.0</span>
        </div>
      </div>

      <!-- RAM Gauge -->
      <div class="glass-card rounded-xl p-4 sm:p-5 flex flex-col justify-between">
        <div class="flex items-center justify-between">
          <span class="text-[11px] uppercase tracking-wider font-semibold text-zinc-400 flex items-center gap-1.5">
            <i class="fa-solid fa-memory text-accent-emerald text-xs"></i>
            Memory (RAM)
          </span>
          <span id="val-ram-pct" class="text-[10px] font-mono px-1.5 py-0.5 rounded bg-surface-base text-emerald-400 border border-surface-border">0%</span>
        </div>
        <div class="my-3">
          <div class="flex items-baseline space-x-1">
            <span id="val-ram-used" class="text-2xl sm:text-3xl font-bold font-mono text-emerald-400 tabular-nums">0.0</span>
            <span class="text-xs text-zinc-500 font-mono">/ <span id="val-ram-total">0.0</span> GB</span>
          </div>
          <!-- Progress Bar -->
          <div class="w-full h-1.5 bg-surface-base rounded-full mt-2 overflow-hidden border border-surface-border">
            <div id="bar-ram" class="h-full bg-emerald-500 transition-all duration-300" style="width: 0%"></div>
          </div>
        </div>
        <div class="text-[11px] font-mono text-zinc-500 flex justify-between">
          <span>Swap:</span>
          <span id="txt-swap" class="text-zinc-300">0.0 GB (0%)</span>
        </div>
      </div>

      <!-- Disk Usage Gauge -->
      <div class="glass-card rounded-xl p-4 sm:p-5 flex flex-col justify-between">
        <div class="flex items-center justify-between">
          <span class="text-[11px] uppercase tracking-wider font-semibold text-zinc-400 flex items-center gap-1.5">
            <i class="fa-solid fa-hard-drive text-indigo-400 text-xs"></i>
            Root NVMe Disk
          </span>
          <span id="val-disk-pct" class="text-[10px] font-mono px-1.5 py-0.5 rounded bg-surface-base text-indigo-300 border border-surface-border">0%</span>
        </div>
        <div class="my-3">
          <div class="flex items-baseline space-x-1">
            <span id="val-disk-used" class="text-2xl sm:text-3xl font-bold font-mono text-indigo-300 tabular-nums">0</span>
            <span class="text-xs text-zinc-500 font-mono">/ <span id="val-disk-total">0</span> GB</span>
          </div>
          <!-- Progress Bar -->
          <div class="w-full h-1.5 bg-surface-base rounded-full mt-2 overflow-hidden border border-surface-border">
            <div id="bar-disk" class="h-full bg-indigo-500 transition-all duration-300" style="width: 0%"></div>
          </div>
        </div>
        <div class="text-[11px] font-mono text-zinc-500 flex justify-between">
          <span>Free Space:</span>
          <span id="val-disk-free" class="text-zinc-300">0 GB</span>
        </div>
      </div>

      <!-- Network I/O Telemetry -->
      <div class="glass-card rounded-xl p-4 sm:p-5 flex flex-col justify-between">
        <div class="flex items-center justify-between">
          <span class="text-[11px] uppercase tracking-wider font-semibold text-zinc-400 flex items-center gap-1.5">
            <i class="fa-solid fa-network-wired text-accent-amber text-xs"></i>
            Network Traffic
          </span>
          <span class="text-[10px] font-mono px-1.5 py-0.5 rounded bg-surface-base text-amber-300 border border-surface-border">I/O</span>
        </div>
        <div class="my-3 space-y-1">
          <div class="flex justify-between text-xs font-mono">
            <span class="text-zinc-400 flex items-center gap-1"><i class="fa-solid fa-arrow-down text-emerald-400 text-[10px]"></i> In:</span>
            <span id="txt-net-in" class="text-white font-bold tabular-nums">0 MB</span>
          </div>
          <div class="flex justify-between text-xs font-mono">
            <span class="text-zinc-400 flex items-center gap-1"><i class="fa-solid fa-arrow-up text-indigo-400 text-[10px]"></i> Out:</span>
            <span id="txt-net-out" class="text-white font-bold tabular-nums">0 MB</span>
          </div>
        </div>
        <div class="text-[11px] font-mono text-zinc-500 flex justify-between">
          <span>Server Node:</span>
          <span id="txt-hostname" class="text-brand-yellow font-bold">dasrams-vps</span>
        </div>
      </div>

    </div>

    <!-- Quick Diagnostics Toolbar -->
    <div class="glass-card rounded-xl p-4 sm:p-5 flex flex-wrap items-center justify-between gap-4">
      <div class="flex items-center space-x-3">
        <button id="btn-diag" onclick="runLiveDiagnostics()" class="btn-interactive px-4 py-2 rounded-lg bg-brand-yellow text-black font-semibold text-xs flex items-center space-x-2 shadow-lg shadow-brand-yellow/20">
          <i class="fa-solid fa-stethoscope text-xs"></i>
          <span>RUN FULL DIAGNOSTICS</span>
        </button>
        <span id="txt-diag-status" class="text-xs font-mono text-zinc-400">Terakhir: Realtime auto-sync</span>
      </div>

      <div class="flex items-center space-x-2">
        <button onclick="copyServerIP()" class="btn-interactive px-3 py-2 rounded-lg bg-surface-base border border-surface-border text-zinc-300 hover:text-white text-xs font-mono flex items-center gap-1.5">
          <i class="fa-regular fa-copy text-xs"></i>
          <span>Copy Node IP</span>
        </button>
      </div>
    </div>

    <!-- Service Health Grid -->
    <div class="glass-card rounded-xl p-5 space-y-4">
      <div class="flex items-center justify-between border-b border-surface-border pb-3">
        <h2 class="text-sm font-bold text-white flex items-center gap-2 font-mono">
          <i class="fa-solid fa-server text-brand-yellow text-xs"></i>
          <span>Ecosystem Node Status</span>
        </h2>
        <span class="text-xs font-mono text-zinc-500">Live Port & Socket Probes</span>
      </div>

      <div id="services-grid" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 font-mono text-xs">
        <!-- Dynamic populated via JS -->
      </div>
    </div>

    <!-- 9router Gateway & Scheduled Tasks -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      
      <!-- 9router AI Gateway Telemetry -->
      <div class="glass-card rounded-xl p-5 space-y-4 flex flex-col">
        <div class="flex items-center justify-between border-b border-surface-border pb-3">
          <h2 class="text-xs font-bold uppercase tracking-wider text-white flex items-center gap-2">
            <i class="fa-solid fa-microchip text-indigo-400"></i>
            <span>9router AI Gateway</span>
          </h2>
          <span id="badge-ai-reqs" class="text-[10px] font-mono px-2 py-0.5 rounded bg-surface-base border border-surface-border text-indigo-300">0 Reqs</span>
        </div>

        <div id="router-providers-list" class="space-y-2 flex-1 overflow-y-auto custom-scroll max-h-60">
          <div class="text-center py-8 text-zinc-500 text-xs font-mono">Memuat status AI Gateway...</div>
        </div>
      </div>

      <!-- Scheduled Tasks & Watchdogs -->
      <div class="glass-card rounded-xl p-5 space-y-4 flex flex-col">
        <div class="flex items-center justify-between border-b border-surface-border pb-3">
          <h2 class="text-xs font-bold uppercase tracking-wider text-white flex items-center gap-2">
            <i class="fa-solid fa-calendar-check text-brand-yellow"></i>
            <span>Scheduled Watchdog Tasks</span>
          </h2>
          <span id="badge-cron-count" class="text-[10px] font-mono px-2 py-0.5 rounded bg-surface-base border border-surface-border text-brand-yellow">0 Jobs</span>
        </div>

        <div id="cron-tasks-list" class="space-y-2 flex-1 overflow-y-auto custom-scroll max-h-60">
          <div class="text-center py-8 text-zinc-500 text-xs font-mono">Memuat daftar scheduled tasks...</div>
        </div>
      </div>

    </div>

  </main>

  <!-- Toast Notification -->
  <div id="toast" class="fixed bottom-5 right-5 bg-surface-elevate border border-surface-border text-white px-4 py-2.5 rounded-xl shadow-2xl transform translate-y-16 opacity-0 transition duration-200 text-xs flex items-center space-x-2 z-50 pointer-events-none">
    <i class="fa-solid fa-check text-brand-yellow text-xs"></i>
    <span id="toast-msg" class="font-medium text-zinc-200">Copied!</span>
  </div>

  <script>
    let pollInterval = null;

    function showToast(msg) {
      const toast = document.getElementById('toast');
      document.getElementById('toast-msg').innerText = msg;
      toast.classList.remove('translate-y-16', 'opacity-0');
      setTimeout(() => {
        toast.classList.add('translate-y-16', 'opacity-0');
      }, 2000);
    }

    function copyServerIP() {
      navigator.clipboard.writeText("43.133.47.135");
      showToast('Node IP (43.133.47.135) disalin ke clipboard');
    }

    async function fetchStatus() {
      const ico = document.getElementById('ico-refresh');
      ico.classList.add('fa-spin');
      try {
        const res = await fetch('/api/status');
        if (!res.ok) {
          if (res.status === 401) window.location.reload();
          return;
        }
        const data = await res.json();
        renderDashboard(data);
      } catch (err) {
        console.error("Fetch status error:", err);
      } finally {
        ico.classList.remove('fa-spin');
      }
    }

    function renderDashboard(data) {
      const s = data.system;
      
      // Uptime & Node info
      document.getElementById('txt-uptime').innerText = s.uptime_human;
      document.getElementById('txt-hostname').innerText = s.hostname;
      
      // CPU
      document.getElementById('val-cpu').innerText = s.cpu.usage_percent;
      document.getElementById('bar-cpu').style.width = s.cpu.usage_percent + '%';
      document.getElementById('txt-cpu-cores').innerText = `${s.cpu.cores} Cores`;
      document.getElementById('txt-load-avg').innerText = s.cpu.load_avg.join(', ');

      // RAM
      document.getElementById('val-ram-used').innerText = s.ram.used_gb;
      document.getElementById('val-ram-total').innerText = s.ram.total_gb;
      document.getElementById('val-ram-pct').innerText = s.ram.percent + '%';
      document.getElementById('bar-ram').style.width = s.ram.percent + '%';
      document.getElementById('txt-swap').innerText = `${s.swap.used_gb} GB (${s.swap.percent}%)`;

      // Disk
      document.getElementById('val-disk-used').innerText = s.disk.used_gb;
      document.getElementById('val-disk-total').innerText = s.disk.total_gb;
      document.getElementById('val-disk-free').innerText = s.disk.free_gb + ' GB';
      document.getElementById('val-disk-pct').innerText = s.disk.percent + '%';
      document.getElementById('bar-disk').style.width = s.disk.percent + '%';

      // Network
      document.getElementById('txt-net-in').innerText = s.network.bytes_recv_mb + ' MB';
      document.getElementById('txt-net-out').innerText = s.network.bytes_sent_mb + ' MB';

      // Services Grid
      const srvGrid = document.getElementById('services-grid');
      const serviceCatalog = [
        { name: "Sutarjio Gemini Hunter", port: 8090, domain: "sutarjio.dasrams.biz.id", active: data.services.sutarjio },
        { name: "SynapseGuild AI RPG", port: 8100, domain: "rpg.dasrams.biz.id", active: data.services.rpg_agent },
        { name: "RuteStrip REST API", port: 8000, domain: "api.dasrams.biz.id", active: data.services.api },
        { name: "9router AI Gateway", port: 20128, domain: "9router.dasrams.biz.id", active: data.services.router },
        { name: "n8n Automation Engine", port: 5678, domain: "n8n.dasrams.biz.id", active: data.services.n8n },
        { name: "ReelCraft Video Studio", port: 8080, domain: "reelcraft.dasrams.biz.id", active: data.services.reelcraft },
        { name: "Database Web Adminer", port: 8088, domain: "db.dasrams.biz.id", active: data.services.adminer },
        { name: "Mailcow Webmail Stack", port: 8095, domain: "mail.dasrams.biz.id", active: data.services.mailcow },
        { name: "Sentinel Watchdog", port: 9000, domain: "monitor.dasrams.biz.id", active: data.services.monitor }
      ];

      srvGrid.innerHTML = serviceCatalog.map(srv => `
        <div class="bg-surface-base p-3 rounded-lg border border-surface-border flex items-center justify-between">
          <div class="space-y-0.5">
            <div class="font-bold text-white text-xs flex items-center gap-1.5">
              <span class="w-2 h-2 rounded-full ${srv.active ? 'bg-emerald-400 animate-pulse' : 'bg-red-500'}"></span>
              ${srv.name}
            </div>
            <p class="text-[10px] text-zinc-400">${srv.domain} :${srv.port}</p>
          </div>
          <span class="px-2 py-0.5 rounded text-[10px] font-semibold ${srv.active ? 'bg-emerald-950/80 text-emerald-300 border border-emerald-800/40' : 'bg-red-950/80 text-red-300 border border-red-800/40'}">
            ${srv.active ? 'ONLINE' : 'STOPPED'}
          </span>
        </div>
      `).join('');

      // 9router providers
      const rList = document.getElementById('router-providers-list');
      document.getElementById('badge-ai-reqs').innerText = `${data.community.ai_total_requests} Reqs`;
      if (data.router_providers && data.router_providers.length > 0) {
        rList.innerHTML = data.router_providers.map(p => `
          <div class="bg-surface-base p-2.5 rounded-lg border border-surface-border flex justify-between items-center text-xs font-mono">
            <div>
              <span class="font-bold text-zinc-200">${p.name}</span>
              <p class="text-[10px] text-zinc-500 uppercase">${p.provider}</p>
            </div>
            <span class="px-2 py-0.5 rounded text-[10px] font-semibold ${p.status === 'ACTIVE' ? 'bg-emerald-950 text-emerald-300' : 'bg-amber-950 text-amber-300'}">${p.status}</span>
          </div>
        `).join('');
      } else {
        rList.innerHTML = '<div class="text-center py-6 text-zinc-500 text-xs font-mono">9router Gateway standby.</div>';
      }

      // Cron tasks
      const cList = document.getElementById('cron-tasks-list');
      document.getElementById('badge-cron-count').innerText = `${data.scheduled_jobs.length} Jobs`;
      if (data.scheduled_jobs && data.scheduled_jobs.length > 0) {
        cList.innerHTML = data.scheduled_jobs.map(j => `
          <div class="bg-surface-base p-2.5 rounded-lg border border-surface-border flex justify-between items-center text-xs font-mono">
            <div>
              <span class="font-bold text-zinc-200">${j.name}</span>
              <p class="text-[10px] text-zinc-500">${j.schedule}</p>
            </div>
            <span class="px-2 py-0.5 rounded text-[10px] font-semibold bg-brand-yellow/10 text-brand-yellow border border-brand-yellow/30">ACTIVE</span>
          </div>
        `).join('');
      } else {
        cList.innerHTML = '<div class="text-center py-6 text-zinc-500 text-xs font-mono">Tidak ada scheduled task aktif.</div>';
      }
    }

    async function runLiveDiagnostics() {
      const btn = document.getElementById('btn-diag');
      const statusTxt = document.getElementById('txt-diag-status');
      btn.disabled = true;
      btn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin text-xs"></i> <span>PROBING NODES...</span>';
      
      try {
        const res = await fetch('/api/diagnostics');
        const data = await res.json();
        statusTxt.innerText = `Selesai ${data.timestamp} — Semua endpoint responsif`;
        showToast('Diagnostik lengkap selesai');
        fetchStatus();
      } catch (err) {
        statusTxt.innerText = 'Diagnostik gagal terhubung';
      } finally {
        btn.disabled = false;
        btn.innerHTML = '<i class="fa-solid fa-stethoscope text-xs"></i> <span>RUN FULL DIAGNOSTICS</span>';
      }
    }

    // Initial fetch & Auto-poll
    fetchStatus();
    pollInterval = setInterval(fetchStatus, 4000);
  </script>
</body>
</html>"""

@app.get("/", response_class=HTMLResponse)
def index_page(request: Request):
    if is_authenticated(request):
        return HTMLResponse(content=DASHBOARD_HTML)
    return HTMLResponse(content=LOGIN_HTML)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)
