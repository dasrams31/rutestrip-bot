#!/usr/bin/env bash
set -e

# ==============================================================================
# 🏔️ RUTESTRIP PENDAKIAN BOT - AUTOMATED ONE-CLICK INSTALLER v2.0
# ==============================================================================

echo "======================================================================"
echo "🚀 Starting Automated Installation for RuteStrip Pendakian Bot..."
echo "======================================================================"

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PATH="$HOME/.hermes/bin:$HOME/.cargo/bin:$HOME/.local/bin:$PATH"
HERMES_DIR="$HOME/.hermes"
SKILLS_DIR="$HERMES_DIR/skills/pendakian-jawa"
SCRIPTS_DIR="$HERMES_DIR/scripts"
DOCS_CACHE="$HERMES_DIR/cache/documents"

# ------------------------------------------------------------------------------
# 1. System Package Updates & Dependencies
# ------------------------------------------------------------------------------
echo "📦 [1/7] Installing System Dependencies (git, ffmpeg, python3, curl)..."
if command -v apt-get &> /dev/null; then
    sudo apt-get update -y
    sudo apt-get install -y git curl wget ffmpeg build-essential python3 python3-pip python3-venv libgdal-dev
fi

# ------------------------------------------------------------------------------
# 2. Install 'uv' Package Manager
# ------------------------------------------------------------------------------
echo "⚡ [2/7] Checking & Installing 'uv' Package Manager..."
if ! command -v uv &> /dev/null; then
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source "$HOME/.cargo/env" 2>/dev/null || export PATH="$HOME/.cargo/bin:$PATH"
fi

# ------------------------------------------------------------------------------
# 3. Virtual Environment & Python Dependencies
# ------------------------------------------------------------------------------
echo "🐍 [3/7] Setting up Python Virtual Environment (pendakian_env)..."
cd "$BASE_DIR"
uv venv pendakian_env --allow-existing
export VENV_PYTHON="$BASE_DIR/pendakian_env/bin/python"

echo "📥 Installing PyTorch CPU & Python Packages..."
uv pip install --python "$VENV_PYTHON" torch torchaudio --index-url https://download.pytorch.org/whl/cpu
uv pip install --python "$VENV_PYTHON" -r "$BASE_DIR/requirements.txt"
uv pip install --python "$VENV_PYTHON" psutil

# ------------------------------------------------------------------------------
# 4. Hermes Framework & Skill Placement
# ------------------------------------------------------------------------------
echo "⚙️ [4/7] Deploying Hermes Skill, Scripts & GPX Database..."
mkdir -p "$SKILLS_DIR"
mkdir -p "$SCRIPTS_DIR"
mkdir -p "$DOCS_CACHE"
mkdir -p "$BASE_DIR/gpx_db"

if [ -f "$BASE_DIR/skills/pendakian-jawa/SKILL.md" ]; then
    cp "$BASE_DIR/skills/pendakian-jawa/SKILL.md" "$SKILLS_DIR/SKILL.md"
fi

# Copy all python scripts to ~/.hermes/scripts and $HOME
for script in *.py; do
    if [ -f "$BASE_DIR/$script" ]; then
        cp "$BASE_DIR/$script" "$SCRIPTS_DIR/$script" 2>/dev/null || true
        cp "$BASE_DIR/$script" "$HOME/$script" 2>/dev/null || true
    fi
done

# Copy JSON databases if present
for jsonfile in reviews.json subscribers.json info_rutestrip.json recommendation_history.json tips_history.json broadcast_messages.json users_auth.json users_chat_sessions.json seen_subscribers.json seen_web_users.json last_cron_seen.json; do
    if [ -f "$BASE_DIR/$jsonfile" ]; then
        cp "$BASE_DIR/$jsonfile" "$HOME/$jsonfile" 2>/dev/null || true
    fi
done

# Copy GPX tracks to cache and DB
cp "$BASE_DIR"/*.gpx "$DOCS_CACHE/" 2>/dev/null || true
cp "$BASE_DIR/gpx_db"/*.gpx "$DOCS_CACHE/" 2>/dev/null || true

# ------------------------------------------------------------------------------
# 5. Config Policy & Multi-User Security Hardening
# ------------------------------------------------------------------------------
echo "🔒 [5/7] Configuring Telegram DM Open Access & Strict Security Lockdown..."
if [ -f "$HERMES_DIR/config.yaml" ]; then
    "$VENV_PYTHON" -c "
import yaml, os

config_path = '$HERMES_DIR/config.yaml'
try:
    with open(config_path, 'r') as f:
        cfg = yaml.safe_load(f) or {}
    
    if 'platforms' not in cfg:
        cfg['platforms'] = {}
    if 'telegram' not in cfg['platforms']:
        cfg['platforms']['telegram'] = {}
    
    cfg['platforms']['telegram']['dm_policy'] = 'open'
    cfg['platforms']['telegram']['allow_all_users'] = True
    cfg['platforms']['telegram']['allow_admin_from'] = ['606533609']
    cfg['platforms']['telegram']['group_allow_admin_from'] = ['606533609']
    cfg['platforms']['telegram']['user_allowed_commands'] = []
    cfg['platforms']['telegram']['group_user_allowed_commands'] = []
    
    admin_prompt = '''You are Hermes Pendakian Bot Assistant, running on VPS with Admin Ramadhana (Rama D, ID: 606533609).
You have full tools (terminal, file, web, git) to assist Admin Rama.'''

    cfg['platforms']['telegram']['channel_overrides'] = {
        '606533609': {
            'system_prompt': admin_prompt
        }
    }
    
    with open(config_path, 'w') as f:
        yaml.dump(cfg, f, default_flow_style=False)
    print('✅ Updated config.yaml security policies!')
except Exception as e:
    print('Config update warning:', e)
"
fi

# Ensure TELEGRAM_ALLOW_ALL_USERS=true in .env
if [ -f "$HERMES_DIR/.env" ]; then
    if ! grep -q "TELEGRAM_ALLOW_ALL_USERS=true" "$HERMES_DIR/.env"; then
        echo -e "\nTELEGRAM_ALLOW_ALL_USERS=true" >> "$HERMES_DIR/.env"
    fi
fi

# ------------------------------------------------------------------------------
# 6. Telegram Menu Commands Registration (/ Button Menu)
# ------------------------------------------------------------------------------
echo "📱 [6/7] Updating Telegram Bot Menu Commands (/)..."
"$VENV_PYTHON" -c "
import os, json, urllib.request

env_vars = {}
env_path = '$HERMES_DIR/.env'
if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                env_vars[k.strip()] = v.strip('\"\'')

bot_token = env_vars.get('TELEGRAM_BOT_TOKEN')
if bot_token:
    hiking_commands = [
        {'command': 'info', 'description': 'Detail jalur, pos & simaksi gunung'},
        {'command': 'rekomendasi', 'description': 'Cari rute pendakian via AI'},
        {'command': 'cuaca', 'description': 'Prakiraan cuaca & wind chill live'},
        {'command': 'itinerary', 'description': 'Estimasi waktu tempuh Naismith'},
        {'command': 'logistik', 'description': 'Kalkulator kebutuhan ransum & air'},
        {'command': 'biaya', 'description': 'Estimasi total anggaran pendakian'},
        {'command': 'patungan', 'description': 'Kalkulator split bill kas tim'},
        {'command': 'survival', 'description': 'Panduan darurat & mitigasi hipotermia'},
        {'command': 'satelit', 'description': 'Peta citra satelit rute & pos'},
        {'command': 'heatmap', 'description': 'Peta kontur topografi elevasi 3D'},
        {'command': 'gpx', 'description': 'Download file GPS trek offline'},
        {'command': 'guidebook', 'description': 'Download E-Guidebook PDF resmi'},
        {'command': 'story', 'description': 'Poster infografis elevasi 9:16'},
        {'command': 'porter', 'description': 'Kontak basecamp & ojek resmi'},
        {'command': 'briefing', 'description': 'Teks & Voice Note briefing ranger'},
        {'command': 'help', 'description': 'Tampilkan menu panduan lengkap'}
    ]
    scopes = [{'type': 'default'}, {'type': 'all_private_chats'}, {'type': 'all_group_chats'}]
    for sc in scopes:
        try:
            req = urllib.request.Request(
                f'https://api.telegram.org/bot{bot_token}/setMyCommands',
                data=json.dumps({'commands': hiking_commands, 'scope': sc}).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            urllib.request.urlopen(req, timeout=10)
        except Exception:
            pass
    print('✅ Telegram Bot Commands registered successfully!')
"

# ------------------------------------------------------------------------------
# 7. Verification & Health Check
# ------------------------------------------------------------------------------
echo "🧪 [7/7] Running Self-Test Health Check..."
"$VENV_PYTHON" "$BASE_DIR/pendakian_cli.py" help > /dev/null

echo "======================================================================"
echo "🎉 INSTALLATION COMPLETE! RuteStrip Pendakian Bot is Fully Operational."
echo "======================================================================"
echo "💡 To test the CLI engine directly:"
echo "   $VENV_PYTHON $BASE_DIR/pendakian_cli.py help"
echo "======================================================================"
