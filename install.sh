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
uv venv pendakian_env
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
cp "$BASE_DIR/cek_cuaca_gunung.py" "$SCRIPTS_DIR/cek_cuaca_gunung.py"
cp "$BASE_DIR/auto_readme_commit.py" "$SCRIPTS_DIR/auto_readme_commit.py"

# Symlink or copy python scripts to /home/ubuntu root for legacy paths if needed
for script in rekomendasi_pendakian.py fitur_pendakian.py itinerary_logistics.py survival_budget.py porter_transport.py gpx_exporter.py gpx_heatmap.py satellite_map.py briefing_audio.py pendakian_cli.py gpx_generator.py; do
    if [ -f "$BASE_DIR/$script" ]; then
        cp "$BASE_DIR/$script" "$HOME/$script" 2>/dev/null || true
    fi
done

# Copy GPX files if present
cp "$BASE_DIR"/*.gpx "$DOCS_CACHE/" 2>/dev/null || true

# ------------------------------------------------------------------------------
# 5. Config Policy & DM Authorization
# ------------------------------------------------------------------------------
echo "🔒 [5/7] Configuring Telegram DM Open Access Policy..."
if command -v hermes &> /dev/null; then
    hermes config set telegram.dm_policy open || true
fi

# ------------------------------------------------------------------------------
# 6. Setup Automated Cronjobs
# ------------------------------------------------------------------------------
echo "⏰ [6/7] Setting up Weather Monitoring & Auto-Commit Cronjobs..."
if command -v hermes &> /dev/null; then
    hermes cronjob create --name "monitoring-cuaca-gunung" --schedule "every 3h" --script "cek_cuaca_gunung.py" --prompt "Laporkan hasil update cuaca dari script chat ini secara ringkas." --deliver "origin" || true
    hermes cronjob create --name "random-auto-readme-commit" --schedule "every 3h" --script "auto_readme_commit.py" --prompt "Jalankan script auto_readme_commit.py untuk memproses commit acak ke GitLab." --deliver "origin" || true
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
