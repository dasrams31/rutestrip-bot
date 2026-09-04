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
uv pip install --python "$VENV_PYTHON" psutil

# ------------------------------------------------------------------------------
# 4. Hermes Framework & Skill Placement
# ------------------------------------------------------------------------------
echo "⚙️ [4/7] Deploying Hermes Skill & Script Specifications..."
mkdir -p "$SKILLS_DIR"
mkdir -p "$SCRIPTS_DIR"
mkdir -p "$DOCS_CACHE"

cp "$BASE_DIR/skills/pendakian-jawa/SKILL.md" "$SKILLS_DIR/SKILL.md"

# Copy python scripts to ~/.hermes/scripts and $HOME
for script in rekomendasi_pendakian.py fitur_pendakian.py itinerary_logistics.py survival_budget.py porter_transport.py gpx_exporter.py gpx_heatmap.py satellite_map.py briefing_audio.py pendakian_cli.py gpx_generator.py broadcast_cuaca_group_part1.py broadcast_cuaca_group_part2.py broadcast_weekend_getaway.py broadcast_survival_tips.py broadcast_bot_usage.py broadcast_channel_bulletin.py broadcast_user_dm.py welcome_handler.py auto_delete_broadcast.py info_rutestrip.py subscriber_report.py monitor_dashboard.py cek_cuaca_gunung.py mountain_newsletter.py cron_execution_reporter.py api.py; do
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
# 6. Setup Automated Cronjobs & Systemd/Daemon Services (Idempotent Check)
# ------------------------------------------------------------------------------
echo "⏰ [6/7] Setting up Weather Monitoring, Channel & Group Broadcasts..."
if command -v hermes &> /dev/null; then
    create_cron_if_missing() {
        local name="$1"
        local schedule="$2"
        local script="$3"
        local deliver="$4"
        local is_no_agent="$5"
        
        if ! hermes cron list | grep -q "$name"; then
            if [ "$is_no_agent" = "true" ]; then
                hermes cron create "$schedule" --name "$name" --script "$script" --no-agent --deliver "$deliver" || true
            else
                hermes cron create "$schedule" "$name" --name "$name" --script "$script" --deliver "$deliver" || true
            fi
        fi
    }

    create_cron_if_missing "monitoring-cuaca-gunung" "every 180m" "cek_cuaca_gunung.py" "origin" "false"
    create_cron_if_missing "random-auto-readme-commit" "every 180m" "auto_readme_commit.py" "origin" "false"
    create_cron_if_missing "channel-bulletin-rutestrip" "0 8 * * *" "broadcast_channel_bulletin.py" "telegram:@rutestrip" "true"
    create_cron_if_missing "broadcast-cuaca-rutestrip-group-part1" "0 7,13,19 * * *" "broadcast_cuaca_group_part1.py" "telegram:@rutestrip_group" "true"
    create_cron_if_missing "broadcast-cuaca-rutestrip-group-part2" "0 7,13,19 * * *" "broadcast_cuaca_group_part2.py" "telegram:@rutestrip_group" "true"
    create_cron_if_missing "broadcast-weekend-getaway-group" "0 6 * * *" "broadcast_weekend_getaway.py" "telegram:@rutestrip_group" "true"
    create_cron_if_missing "broadcast-survival-tips-group" "0 10 * * 2,4" "broadcast_survival_tips.py" "telegram:@rutestrip_group" "true"
    create_cron_if_missing "broadcast-bot-usage-group" "0 20 * * *" "broadcast_bot_usage.py" "telegram:@rutestrip_group" "true"
    create_cron_if_missing "broadcast-user-dm-digest" "0 7 * * *" "broadcast_user_dm.py" "origin" "true"
    create_cron_if_missing "laporan-rutin-pengguna-bot" "0 21 * * *" "subscriber_report.py" "origin" "true"
    create_cron_if_missing "notif-cron-realtime-admin" "every 1m" "cron_execution_reporter.py" "origin" "true"
fi

# Launch API & Monitoring Daemons in Background if not running
if ! pgrep -f "uvicorn api:app" > /dev/null; then
    echo "🌐 Starting REST API Service (Uvicorn Port 8000)..."
    nohup "$VENV_PYTHON" -m uvicorn api:app --host 0.0.0.0 --port 8000 > /dev/null 2>&1 &
fi

if ! pgrep -f "uvicorn monitor_dashboard:app" > /dev/null; then
    echo "📊 Starting Monitoring Dashboard Service (Uvicorn Port 9000)..."
    nohup "$VENV_PYTHON" -m uvicorn monitor_dashboard:app --host 0.0.0.0 --port 9000 > /dev/null 2>&1 &
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

if [ -f "$BASE_DIR/daily_community_announcer.py" ]; then
    cp "$BASE_DIR/daily_community_announcer.py" "$SCRIPTS_DIR/daily_community_announcer.py"
fi

if command -v hermes &> /dev/null; then
    create_cron_if_missing "daily-community-announcer" "0 15 * * *" "daily_community_announcer.py" "telegram:@rutestrip_group" "true"
fi

if [ -f "$BASE_DIR/notify_new_user.py" ]; then
    cp "$BASE_DIR/notify_new_user.py" "$SCRIPTS_DIR/notify_new_user.py"
fi

if command -v hermes &> /dev/null; then
    create_cron_if_missing "notif-pengguna-baru-admin" "every 1m" "notify_new_user.py" "origin" "true"
fi

if [ -f "$BASE_DIR/broadcast_community_to_users.py" ]; then
    cp "$BASE_DIR/broadcast_community_to_users.py" "$SCRIPTS_DIR/broadcast_community_to_users.py"
fi

if command -v hermes &> /dev/null; then
    create_cron_if_missing "broadcast-community-user-dm" "0 14 * * 3,6" "broadcast_community_to_users.py" "origin" "true"
fi
