#!/bin/bash
# =========================================
# Daily GitHub Sync — Midnight Auto-Push
# Pushes all new/modified files in workdir
# to https://github.com/tasharve2022/ai-projects
# =========================================

WORKDIR="/a0/usr/workdir"
TOKEN_FILE="$HOME/secrets/github_token.txt"
DATE_TAG=$(date '+%Y-%m-%d')

cd "$WORKDIR" || { echo "[FAIL] Cannot cd to $WORKDIR"; exit 1; }

# Read token securely
if [ ! -f "$TOKEN_FILE" ]; then
    echo "[FAIL] GitHub token not found at $TOKEN_FILE"
    exit 1
fi
TOKEN=$(cat "$TOKEN_FILE")

# Set remote with token-based auth
REMOTE_URL="https://tasharve2022:${TOKEN}@github.com/tasharve2022/ai-projects.git"
git remote set-url origin "$REMOTE_URL" 2>/dev/null || true

# Add all new/modified files (respects .gitignore)
git add -A

# Check if there's anything to commit
if git diff --cached --quiet; then
    echo "[OK $DATE_TAG] No changes to push."
    exit 0
fi

# Commit with date tag
git commit -m "Daily sync: $DATE_TAG"

# Push to main branch
git push origin main 2>&1
if [ $? -eq 0 ]; then
    echo "[OK $DATE_TAG] Push successful."
else
    echo "[FAIL $DATE_TAG] Push failed."
    exit 1
fi
