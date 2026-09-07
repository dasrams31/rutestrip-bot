import sys
import os
import time
import json
import sqlite3
import psutil
import subprocess
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="RuteStrip Status & AI Token Monitoring Dashboard")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def check_process(name_pattern):
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmd = " ".join(proc.info['cmdline'] or [])
            if name_pattern in cmd:
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False

def get_9router_data():
    db_path = "/home/ubuntu/.9router/db/data.sqlite"
    providers_list = []
    total_requests = 0
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Query Provider Connections / AI Tokens
            rows = cursor.execute("SELECT id, provider, name, isActive, data FROM providerConnections").fetchall()
            for r in rows:
                p_id, p_type, name, is_active, data_json = r
                p_data = {}
                try:
                    p_data = json.loads(data_json) if data_json else {}
                except Exception:
                    pass
                
                status = "ACTIVE" if is_active == 1 else "INACTIVE"
                if p_data.get("testStatus") == "unavailable" or "lastError" in p_data and p_data["lastError"]:
                    status = "WARNING / ERROR"
                
                providers_list.append({
                    "id": p_id,
                    "provider": p_type,
                    "name": name or "Unnamed Account",
                    "status": status,
                    "email": p_data.get("email", name or "N/A"),
                    "project_id": p_data.get("projectId", "N/A"),
                    "last_error": p_data.get("lastError", None),
                    "last_refresh": p_data.get("lastRefreshAt", "N/A")
                })
            
            # Query Total Usage Requests
            req_count = cursor.execute("SELECT COUNT(*) FROM usageHistory").fetchone()
            if req_count:
                total_requests = req_count[0]
            conn.close()
        except Exception as e:
            print("Database 9router query error:", e)
            
    return providers_list, total_requests

@app.get("/api/status")
def get_system_status():
    # VPS System Metrics
    cpu_usage = psutil.cpu_percent(interval=0.5)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    uptime_seconds = time.time() - psutil.boot_time()
    
    # Services Status
    fastapi_running = check_process("uvicorn api:app")
    hermes_running = check_process("hermes_cli.main gateway run") or check_process("hermes")
    router_running = check_process("9router") or check_process("cloudflared")
    
    # Subscribers Count
    subscribers_count = 0
    sub_file = "/home/ubuntu/rutestrip-bot/subscribers.json"
    if os.path.exists(sub_file):
        try:
            with open(sub_file, 'r') as f:
                subscribers_count = len(json.load(f))
        except Exception:
            pass

    # 9router AI Provider Tokens & Usage
    tokens_list, total_ai_requests = get_9router_data()

    return {
        "vps": {
            "cpu_percent": cpu_usage,
            "memory_percent": memory.percent,
            "memory_used_mb": round(memory.used / (1024 * 1024), 2),
            "memory_total_mb": round(memory.total / (1024 * 1024), 2),
            "disk_percent": disk.percent,
            "disk_used_gb": round(disk.used / (1024**3), 2),
            "disk_total_gb": round(disk.total / (1024**3), 2),
            "uptime_hours": round(uptime_seconds / 3600, 1)
        },
        "services": {
            "fastapi_api": "ONLINE" if fastapi_running else "OFFLINE",
            "rutestrip_bot": "ONLINE" if hermes_running else "OFFLINE",
            "hermes_gateway": "ONLINE" if hermes_running else "OFFLINE",
            "router_9router": "ONLINE" if router_running else "OFFLINE",
            "website_rutestrip": "ONLINE"
        },
        "bot_stats": {
            "total_subscribers": subscribers_count,
            "gpx_database_count": 55,
            "active_cronjobs": 6
        },
        "ai_tokens": {
            "total_tokens_registered": len(tokens_list),
            "total_ai_requests": total_ai_requests,
            "active_providers": tokens_list
        }
    }

@app.get("/", response_class=HTMLResponse)
@app.get("/monitoring", response_class=HTMLResponse)
def get_dashboard_html():
    html_content = """
    <!DOCTYPE html>
    <html lang="id">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>RuteStrip Realtime Monitoring & AI Token Dashboard</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css">
        <style>
            body { background-color: #0f172a; color: #f8fafc; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; padding-top: 75px; }
            .navbar { background-color: #1e293b; border-bottom: 1px solid #334155; }
            .card { background-color: #1e293b; border: 1px solid #334155; border-radius: 12px; }
            .status-badge { padding: 6px 16px; border-radius: 20px; font-weight: 600; font-size: 0.85rem; }
            .badge-online { background-color: #059669; color: #ecfdf5; }
            .badge-offline { background-color: #dc2626; color: #fef2f2; }
            .badge-warning { background-color: #d97706; color: #fffbeb; }
            .metric-val { font-size: 1.8rem; font-weight: 700; color: #38bdf8; }
            .header-title { font-weight: 800; background: linear-gradient(to right, #38bdf8, #34d399); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
            .nav-link { font-weight: 600; color: #94a3b8 !important; }
            .nav-link.active { color: #38bdf8 !important; border-bottom: 2px solid #38bdf8; }
            section { scroll-margin-top: 90px; }
        </style>
    </head>
    <body>

        <!-- Navbar Access Navigation -->
        <nav class="navbar navbar-expand-lg fixed-top navbar-dark">
            <div class="container-fluid px-4">
                <a class="navbar-brand header-title fs-4" href="#">🏔️ RuteStrip Monitor</a>
                <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                    <span class="navbar-toggler-icon"></span>
                </button>
                <div class="collapse navbar-collapse" id="navbarNav">
                    <ul class="navbar-nav me-auto ms-4">
                        <li class="nav-item">
                            <a class="nav-link active" href="#sec-overview"><i class="bi bi-speedometer2 me-1"></i> Overview</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="#sec-ai-tokens"><i class="bi bi-cpu me-1"></i> AI Tokens & 9Router</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="#sec-services"><i class="bi bi-diagram-3 me-1"></i> Services & VPS</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="#sec-bot-stats"><i class="bi bi-bar-chart-line me-1"></i> Bot Stats</a>
                        </li>
                    </ul>
                    <div class="d-flex align-items-center gap-2">
                        <span class="badge bg-primary px-3 py-2">IP: 188.166.224.148</span>
                        <span class="text-muted small" id="last-update">Updating...</span>
                    </div>
                </div>
            </div>
        </nav>

        <div class="container-fluid px-4 py-3">

            <!-- Section 1: Overview & Services Badges -->
            <section id="sec-overview" class="mb-4">
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <h4 class="fw-bold text-info mb-0"><i class="bi bi-hdd-network me-2"></i> System Services Overview</h4>
                </div>
                <div class="row g-3">
                    <div class="col-md-3">
                        <div class="card p-3">
                            <div class="d-flex justify-content-between align-items-center">
                                <div>
                                    <small class="text-secondary d-block">REST API Service</small>
                                    <span class="fs-5 fw-bold">FastAPI Server</span>
                                </div>
                                <span id="st-api" class="status-badge badge-online">ONLINE</span>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card p-3">
                            <div class="d-flex justify-content-between align-items-center">
                                <div>
                                    <small class="text-secondary d-block">Telegram Bot</small>
                                    <span class="fs-5 fw-bold">RuteStrip Bot</span>
                                </div>
                                <span id="st-bot" class="status-badge badge-online">ONLINE</span>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card p-3">
                            <div class="d-flex justify-content-between align-items-center">
                                <div>
                                    <small class="text-secondary d-block">AI Gateway / Router</small>
                                    <span class="fs-5 fw-bold">9Router Daemon</span>
                                </div>
                                <span id="st-router" class="status-badge badge-online">ONLINE</span>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card p-3">
                            <div class="d-flex justify-content-between align-items-center">
                                <div>
                                    <small class="text-secondary d-block">AI Agent Engine</small>
                                    <span class="fs-5 fw-bold">Hermes Framework</span>
                                </div>
                                <span id="st-hermes" class="status-badge badge-online">ONLINE</span>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            <!-- Section 2: AI Token Monitoring & 9Router Pool -->
            <section id="sec-ai-tokens" class="mb-4">
                <div class="card p-4">
                    <div class="d-flex justify-content-between align-items-center mb-3">
                        <div>
                            <h4 class="fw-bold text-success mb-1"><i class="bi bi-key-fill me-2"></i> AI Token & Provider Connections (9Router Pool)</h4>
                            <p class="text-secondary mb-0">Daftar Akun, Status Token bertugas, & Total AI Request Usage</p>
                        </div>
                        <div class="text-end">
                            <span class="fs-5 fw-bold text-warning" id="total-ai-req">0</span>
                            <small class="text-muted d-block">Total AI Requests Handled</small>
                        </div>
                    </div>

                    <div class="table-responsive">
                        <table class="table table-dark table-hover align-middle mb-0">
                            <thead>
                                <tr>
                                    <th>Provider Engine</th>
                                    <th>Account / Token Name</th>
                                    <th>Project ID</th>
                                    <th>Status Token</th>
                                    <th>Last Error / Note</th>
                                </tr>
                            </thead>
                            <tbody id="token-table-body">
                                <tr>
                                    <td colspan="5" class="text-center text-muted">Memuat data token AI...</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </section>

            <!-- Section 3: Hardware Resource Metrics -->
            <section id="sec-services" class="mb-4">
                <h4 class="fw-bold text-warning mb-3"><i class="bi bi-cpu me-2"></i> VPS Hardware Resources</h4>
                <div class="row g-3">
                    <div class="col-md-3">
                        <div class="card p-3">
                            <small class="text-secondary">CPU Usage</small>
                            <div class="metric-val" id="cpu-val">0%</div>
                            <div class="progress mt-2" style="height: 6px;">
                                <div id="cpu-bar" class="progress-bar bg-info" style="width: 0%"></div>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card p-3">
                            <small class="text-secondary">RAM Memory</small>
                            <div class="metric-val" id="ram-val">0%</div>
                            <small class="text-muted" id="ram-detail">0 / 0 MB</small>
                            <div class="progress mt-2" style="height: 6px;">
                                <div id="ram-bar" class="progress-bar bg-success" style="width: 0%"></div>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card p-3">
                            <small class="text-secondary">Disk Storage</small>
                            <div class="metric-val" id="disk-val">0%</div>
                            <small class="text-muted" id="disk-detail">0 / 0 GB</small>
                            <div class="progress mt-2" style="height: 6px;">
                                <div id="disk-bar" class="progress-bar bg-warning" style="width: 0%"></div>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card p-3">
                            <small class="text-secondary">VPS Server Uptime</small>
                            <div class="metric-val" style="color: #a78bfa;" id="uptime-val">0 Hours</div>
                            <small class="text-muted">Ubuntu VPS 22.04 LTS</small>
                        </div>
                    </div>
                </div>
            </section>

            <!-- Section 4: Bot & Endpoints Stats -->
            <section id="sec-bot-stats" class="mb-4">
                <div class="row g-3">
                    <div class="col-md-4">
                        <div class="card p-4">
                            <h5 class="fw-bold mb-3 text-info"><i class="bi bi-people me-2"></i> Bot Community Stats</h5>
                            <div class="d-flex justify-content-between py-2 border-bottom border-secondary">
                                <span>Subscribers / Chat Users</span>
                                <span class="fw-bold" id="sub-count">0 Users</span>
                            </div>
                            <div class="d-flex justify-content-between py-2 border-bottom border-secondary">
                                <span>GPX Mountain Tracks</span>
                                <span class="fw-bold">55 Tracks</span>
                            </div>
                            <div class="d-flex justify-content-between py-2">
                                <span>Active Cronjobs</span>
                                <span class="fw-bold">6 Active Jobs</span>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-8">
                        <div class="card p-4">
                            <h5 class="fw-bold mb-3 text-success"><i class="bi bi-globe me-2"></i> Active System Endpoints</h5>
                            <table class="table table-dark table-hover mb-0">
                                <thead>
                                    <tr>
                                        <th>Service</th>
                                        <th>Endpoint / URL</th>
                                        <th>Port</th>
                                        <th>Status</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td>Monitoring & AI Token Dashboard</td>
                                        <td><code>https://airutestrip.web.id/monitoring</code></td>
                                        <td>9000</td>
                                        <td><span class="badge bg-success">ACTIVE</span></td>
                                    </tr>
                                    <tr>
                                        <td>REST API Service & Docs</td>
                                        <td><code>http://188.166.224.148:8000/docs</code></td>
                                        <td>8000</td>
                                        <td><span class="badge bg-success">ACTIVE</span></td>
                                    </tr>
                                    <tr>
                                        <td>Website Utama</td>
                                        <td><code>https://rutestrip.web.id</code></td>
                                        <td>443</td>
                                        <td><span class="badge bg-success">ACTIVE</span></td>
                                    </tr>
                                    <tr>
                                        <td>AI Chat Assistant</td>
                                        <td><code>https://airutestrip.web.id</code></td>
                                        <td>443</td>
                                        <td><span class="badge bg-success">ACTIVE</span></td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </section>

        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            async function updateStatus() {
                try {
                    const res = await fetch('/api/status');
                    const data = await res.json();
                    
                    // Hardware Metrics
                    document.getElementById('cpu-val').innerText = data.vps.cpu_percent + '%';
                    document.getElementById('cpu-bar').style.width = data.vps.cpu_percent + '%';
                    
                    document.getElementById('ram-val').innerText = data.vps.memory_percent + '%';
                    document.getElementById('ram-bar').style.width = data.vps.memory_percent + '%';
                    document.getElementById('ram-detail').innerText = data.vps.memory_used_mb + ' / ' + data.vps.memory_total_mb + ' MB';
                    
                    document.getElementById('disk-val').innerText = data.vps.disk_percent + '%';
                    document.getElementById('disk-bar').style.width = data.vps.disk_percent + '%';
                    document.getElementById('disk-detail').innerText = data.vps.disk_used_gb + ' / ' + data.vps.disk_total_gb + ' GB';
                    
                    document.getElementById('uptime-val').innerText = data.vps.uptime_hours + ' Jam';
                    document.getElementById('sub-count').innerText = data.bot_stats.total_subscribers + ' Users';
                    document.getElementById('total-ai-req').innerText = data.ai_tokens.total_ai_requests;
                    
                    // Badges Services
                    updateBadge('st-api', data.services.fastapi_api);
                    updateBadge('st-bot', data.services.rutestrip_bot);
                    updateBadge('st-router', data.services.router_9router);
                    updateBadge('st-hermes', data.services.hermes_gateway);

                    // AI Token Table Update
                    const tbody = document.getElementById('token-table-body');
                    tbody.innerHTML = '';
                    if (data.ai_tokens.active_providers && data.ai_tokens.active_providers.length > 0) {
                        data.ai_tokens.active_providers.forEach(p => {
                            let badgeClass = 'badge bg-success';
                            if (p.status.includes('WARNING') || p.status.includes('ERROR')) {
                                badgeClass = 'badge bg-warning text-dark';
                            } else if (p.status === 'INACTIVE') {
                                badgeClass = 'badge bg-danger';
                            }

                            const tr = document.createElement('tr');
                            tr.innerHTML = `
                                <td><span class="badge bg-secondary">${p.provider}</span></td>
                                <td class="fw-bold">${p.email}</td>
                                <td><code>${p.project_id}</code></td>
                                <td><span class="${badgeClass}">${p.status}</span></td>
                                <td class="small text-muted">${p.last_error ? p.last_error : 'Normal / Operating'}</td>
                            `;
                            tbody.appendChild(tr);
                        });
                    } else {
                        tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted">Tidak ada token AI terdeteksi.</td></tr>';
                    }
                    
                    document.getElementById('last-update').innerText = 'Updated ' + new Date().toLocaleTimeString();
                } catch (e) {
                    console.error("Error fetching status:", e);
                }
            }

            function updateBadge(id, status) {
                const el = document.getElementById(id);
                el.innerText = status;
                if (status === 'ONLINE') {
                    el.className = 'status-badge badge-online';
                } else {
                    el.className = 'status-badge badge-offline';
                }
            }

            setInterval(updateStatus, 3000);
            updateStatus();
        </script>
    </body>
    </html>
    """
    return html_content
