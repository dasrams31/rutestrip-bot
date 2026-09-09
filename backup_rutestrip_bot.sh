#!/usr/bin/env bash
set -e

# ==============================================================================
# 🏔️ RUTESTRIP PENDAKIAN BOT - AUTOMATED LIGHTWEIGHT BACKUP SCRIPT
# ==============================================================================

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_DIR="/tmp/rutestrip_backups"
REPO_BACKUP_DIR="$BASE_DIR/backups"
TIMESTAMP="$(date +'%Y%m%d_%H%M%S')"
TEMP_ARCHIVE="$BACKUP_DIR/rutestrip_bot_code_backup_$TIMESTAMP.tar.gz"
FINAL_ARCHIVE="$REPO_BACKUP_DIR/rutestrip_bot_code_backup_$TIMESTAMP.tar.gz"

echo "======================================================================"
echo "📦 Starting RuteStrip Bot Code & Data Backup ($TIMESTAMP)..."
echo "======================================================================"

mkdir -p "$BACKUP_DIR"
mkdir -p "$REPO_BACKUP_DIR"

# Archive Python scripts, JSON databases, configs & skills (Excluding heavy GPX binaries & venv)
tar -czf "$TEMP_ARCHIVE" \
    --exclude="$BASE_DIR/pendakian_env" \
    --exclude="$BASE_DIR/.git" \
    --exclude="$BASE_DIR/gpx_db" \
    --exclude="$BASE_DIR/backups" \
    --exclude="*.png" \
    --exclude="*.svg" \
    -C "$BASE_DIR" .

mv "$TEMP_ARCHIVE" "$FINAL_ARCHIVE"

echo "✅ Backup archive created: $FINAL_ARCHIVE"
echo "📊 Archive Size: $(du -sh "$FINAL_ARCHIVE" | cut -f1)"

# Keep only the last 2 lightweight backups
cd "$REPO_BACKUP_DIR"
ls -t rutestrip_bot_code_backup_*.tar.gz 2>/dev/null | tail -n +3 | xargs rm -f 2>/dev/null || true

# Commit & Push backup log / archive to GitLab
cd "$BASE_DIR"
git add backups/ backup_rutestrip_bot.sh 2>/dev/null || true
git commit -m "chore(backup): create automated lightweight bot backup ($TIMESTAMP)" || true
git push origin main

echo "======================================================================"
echo "🎉 BACKUP & GITLAB SYNC SUCCESSFUL!"
echo "======================================================================"
