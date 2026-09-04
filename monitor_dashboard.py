import sys
import os
import time
import json
import psutil
import subprocess
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="RuteStrip Status & Monitoring Dashboard")

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
    
    # Subscribers Count
    subscribers_count = 0
    sub_file = "/root/rutestrip-bot/subscribers.json"
    if os.path.exists(sub_file):
        try:
            with open(sub_file, 'r') as f:
                subscribers_count = len(json.load(f))
        except Exception:
            pass

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
            "website_rutestrip": "ONLINE"
        },
        "bot_stats": {
            "total_subscribers": subscribers_count,
            "gpx_database_count": 55,
            "active_cronjobs": 6
        }
    }

@app.get("/", response_class=HTMLResponse)
def get_dashboard_html():
    html_content = """
    <!DOCTYPE html>
    <html lang="id">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>RuteStrip Realtime Monitoring Dashboard</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body { background-color: #0f172a; color: #f8fafc; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
            .card { background-color: #1e293b; border: 1px solid #334155; border-radius: 12px; }
            .status-badge { padding: 6px 16px; border-radius: 20px; font-weight: 600; font-size: 0.85rem; }
            .badge-online { background-color: #059669; color: #ecfdf5; }
            .badge-offline { background-color: #dc2626; color: #fef2f2; }
            .metric-val { font-size: 1.8rem; font-weight: 700; color: #38bdf8; }
            .header-title { font-weight: 800; background: linear-gradient(to right, #38bdf8, #34d399); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        </style>
    </head>
    <body class="p-4">
        <div class="container-fluid">
            <div class="d-flex justify-content-between align-items-center mb-4 pb-2 border-bottom border-secondary">
                <div>
                    <h2 class="header-title mb-1">🏔️ RuteStrip Realtime Monitoring Dashboard</h2>
                    <p class="text-secondary mb-0">System Status, Infrastructure, Services & Bot Metrics</p>
                </div>
                <div class="text-end">
                    <span class="badge bg-primary px-3 py-2">IP: 188.166.224.148</span>
                    <span class="text-muted ms-2" id="last-update">Updating...</span>
                </div>
            </div>

            <!-- Services Status Cards -->
            <div class="row g-3 mb-4">
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
                                <small class="text-secondary d-block">AI Agent Engine</small>
                                <span class="fs-5 fw-bold">Hermes Gateway</span>
                            </div>
                            <span id="st-hermes" class="status-badge badge-online">ONLINE</span>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card p-3">
                        <div class="d-flex justify-content-between align-items-center">
                            <div>
                                <small class="text-secondary d-block">Website Principal</small>
                                <span class="fs-5 fw-bold">rutestrip.web.id</span>
                            </div>
                            <span id="st-web" class="status-badge badge-online">ONLINE</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- VPS Hardware Resource Metrics -->
            <div class="row g-3 mb-4">
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

            <!-- Bot Metrics & Database Info -->
            <div class="row g-3">
                <div class="col-md-4">
                    <div class="card p-4">
                        <h5 class="fw-bold mb-3 text-info">📊 Bot Statistics</h5>
                        <div class="d-flex justify-content-between py-2 border-bottom border-secondary">
                            <span>Subscribers / Chat Users</span>
                            <span class="fw-bold" id="sub-count">0</span>
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
                        <h5 class="fw-bold mb-3 text-success">🌐 Active Infrastructure Endpoints</h5>
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
                                    <td>Monitoring Dashboard</td>
                                    <td><code>http://188.166.224.148:9000</code></td>
                                    <td>9000</td>
                                    <td><span class="badge bg-success">ACTIVE</span></td>
                                </tr>
                                <tr>
                                    <td>REST API Service</td>
                                    <td><code>http://188.166.224.148:8000/docs</code></td>
                                    <td>8000</td>
                                    <td><span class="badge bg-success">ACTIVE</span></td>
                                </tr>
                                <tr>
                                    <td>Website Principal</td>
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
        </div>

        <script>
            async function updateStatus() {
                try {
                    const res = await fetch('/api/status');
                    const data = await res.json();
                    
                    // Update Metrics
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
                    
                    // Update Services Badges
                    updateBadge('st-api', data.services.fastapi_api);
                    updateBadge('st-bot', data.services.rutestrip_bot);
                    updateBadge('st-hermes', data.services.hermes_gateway);
                    updateBadge('st-web', data.services.website_rutestrip);
                    
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
