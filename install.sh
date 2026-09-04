#!/usr/bin/env bash
set -e

# ==============================================================================
# 🏔️ RUTESTRIP PENDAKIAN BOT - AUTOMATED ONE-CLICK INSTALLER
# ==============================================================================

echo "======================================================================"
echo "🚀 Starting Automated Installation for RuteStrip Pendakian Bot..."
echo "======================================================================"

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
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
    sudo apt-get install -y git curl wget ffmpeg build-essential python3 python3-pip python3-venv
fi

# ------------------------------------------------------------------------------
# 2. Install 'uv' Package Manager
# ------------------------------------------------------------------------------
echo "⚡ [2/7] Checking & Installing 'uv' Package Manager..."
if ! command -v uv &> /dev/null; then
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source "$HOME/.cargo/env" || export PATH="$HOME/.cargo/bin:$PATH"
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

# ------------------------------------------------------------------------------
# 4. Hermes Framework & Skill Placement
# ------------------------------------------------------------------------------
echo "⚙️ [4/7] Deploying Hermes Skill & Script Specifications..."
mkdir -p "$SKILLS_DIR"
mkdir -p "$SCRIPTS_DIR"
mkdir -p "$DOCS_CACHE"

cp "$BASE_DIR/skills/pendakian-jawa/SKILL.md" "$SKILLS_DIR/SKILL.md"

# Copy python scripts to ~/.hermes/scripts and $HOME
for script in rekomendasi_pendakian.py fitur_pendakian.py itinerary_logistics.py survival_budget.py porter_transport.py gpx_exporter.py gpx_heatmap.py satellite_map.py briefing_audio.py pendakian_cli.py gpx_generator.py daily_web_announcer.py daily_community_announcer.py broadcast_cuaca_group.py broadcast_weekend_getaway.py broadcast_survival_tips.py broadcast_bot_usage.py broadcast_channel_bulletin.py welcome_handler.py auto_delete_broadcast.py info_rutestrip.py subscriber_report.py api.py; do
    if [ -f "$BASE_DIR/$script" ]; then
        cp "$BASE_DIR/$script" "$SCRIPTS_DIR/$script" 2>/dev/null || true
        cp "$BASE_DIR/$script" "$HOME/$script" 2>/dev/null || true
    fi
done

# Copy JSON data files if present
for jsonfile in reviews.json subscribers.json info_rutestrip.json recommendation_history.json tips_history.json broadcast_messages.json; do
    if [ -f "$BASE_DIR/$jsonfile" ]; then
        cp "$BASE_DIR/$jsonfile" "$HOME/$jsonfile" 2>/dev/null || true
    fi
done

# Copy GPX files & GPX Database if present
mkdir -p "$BASE_DIR/gpx_db"
cp "$BASE_DIR"/*.gpx "$DOCS_CACHE/" 2>/dev/null || true
cp "$BASE_DIR/gpx_db"/*.gpx "$BASE_DIR/gpx_db/" 2>/dev/null || true

# ------------------------------------------------------------------------------
# 5. Config Policy & DM Authorization
# ------------------------------------------------------------------------------
echo "🔒 [5/7] Configuring Telegram DM Open Access & Allowlist Policy..."
if command -v hermes &> /dev/null; then
    hermes config set telegram.dm_policy open || true
    hermes config set telegram.allow_from "*" || true
    hermes config set telegram.group_allow_from "*" || true
    hermes config set cron.wrap_response false || true
fi

# ------------------------------------------------------------------------------
# 6. Setup Automated Cronjobs & Systemd/Daemon Services
# ------------------------------------------------------------------------------
echo "⏰ [6/7] Setting up Weather Monitoring, Channel & Group Broadcasts..."
if command -v hermes &> /dev/null; then
    hermes cron create "every 180m" "Laporkan hasil update cuaca dari script chat ini secara ringkas." --name "monitoring-cuaca-gunung" --script "cek_cuaca_gunung.py" --deliver "origin" || true
    hermes cron create "every 180m" "Jalankan script auto_readme_commit.py untuk memproses commit acak ke GitLab." --name "random-auto-readme-commit" --script "auto_readme_commit.py" --deliver "origin" || true
    
    # Official Channel Bulletin (Pasif Satu Arah)
    hermes cron create "0 8 * * *" "Daily mountain news bulletin to channel" --name "channel-bulletin-rutestrip" --script "broadcast_channel_bulletin.py" --no-agent --deliver "telegram:@rutestrip" || true

    # Group Broadcast Cronjobs
    hermes cron create "0 7,13,19 * * *" "Broadcast cuaca gunung rutin ke grup" --name "broadcast-cuaca-rutestrip-group" --script "broadcast_cuaca_group.py" --no-agent --deliver "telegram:@rutestrip_group" || true
    hermes cron create "0 6 * * *" "Rekomendasi pendakian harian & weekend getaway" --name "broadcast-weekend-getaway-group" --script "broadcast_weekend_getaway.py" --no-agent --deliver "telegram:@rutestrip_group" || true
    hermes cron create "0 10 * * 2,4" "Tips survival & etika pendaki" --name "broadcast-survival-tips-group" --script "broadcast_survival_tips.py" --no-agent --deliver "telegram:@rutestrip_group" || true
    hermes cron create "0 20 * * *" "Broadcast panduan penggunaan bot harian" --name "broadcast-bot-usage-group" --script "broadcast_bot_usage.py" --no-agent --deliver "telegram:@rutestrip_group" || true
    
    # Admin Growth Report
    hermes cron create "0 21 * * *" "Laporan statistik pengguna harian ke admin" --name "laporan-rutin-pengguna-bot" --script "subscriber_report.py" --no-agent --deliver "origin" || true
fi

# Launch API Daemon in Background if not running
if ! pgrep -f "uvicorn api:app" > /dev/null; then
    echo "🌐 Starting REST API Service (Uvicorn)..."
    nohup "$VENV_PYTHON" -m uvicorn api:app --host 0.0.0.0 --port 8000 > /dev/null 2>&1 &
fi

# ------------------------------------------------------------------------------
# 7. Verification & Health Check
# ------------------------------------------------------------------------------
echo "🧪 [7/7] Running Self-Test Health Check..."
"$VENV_PYTHON" "$BASE_DIR/pendakian_cli.py" help > /dev/null

echo "======================================================================"
echo "🎉 INSTALLATION SUCCESSFUL! RuteStrip Pendakian Bot is Ready."
echo "======================================================================"
echo "💡 To test locally, run:"
echo "   $VENV_PYTHON $BASE_DIR/pendakian_cli.py help"
echo "======================================================================"
