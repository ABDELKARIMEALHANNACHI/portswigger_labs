#!/bin/bash

set -e

#####################################
# SAFETY: NEVER RUN WITH SUDO
#####################################
if [ "$EUID" -eq 0 ]; then
  echo "❌ Do NOT run this script with sudo"
  echo "Run it as your normal user: ./cors_fix_structure.sh"
  exit 1
fi

#####################################
# AUTO-DETECT REPO ROOT
#####################################
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$SCRIPT_DIR"

if [ ! -d "$REPO_DIR/cors" ]; then
  echo "❌ cors directory not found in $REPO_DIR"
  exit 1
fi

CORS_DIR="$REPO_DIR/cors"

echo "[+] Using repo: $REPO_DIR"

#####################################
# BACKUP
#####################################
BACKUP_DIR="$REPO_DIR/cors_backup_$(date +%s)"
echo "[+] Creating backup: $BACKUP_DIR"
cp -r "$CORS_DIR" "$BACKUP_DIR"

#####################################
# CLEAN OLD STRUCTURE
#####################################
echo "[+] Cleaning old CORS structure (keeping README.md)"
find "$CORS_DIR" -mindepth 1 ! -name "README.md" -exec rm -rf {} +

#####################################
# LABS TO CREATE
#####################################
LABS=(
  "lab-01-basic-origin-reflection"
  "lab-02-trusted-null-origin"
  "lab-03-insecure-protocols"
)

#####################################
# CREATE STRUCTURE
#####################################
echo "[+] Creating standardized lab architecture..."

for LAB in "${LABS[@]}"; do
  LAB_PATH="$CORS_DIR/$LAB"

  mkdir -p "$LAB_PATH"/{docs,fix,reports,screenshots,tests,vuln}
  mkdir -p "$LAB_PATH/vuln/payloads"

  # core files
  touch "$LAB_PATH/README.md"
  touch "$LAB_PATH/docs/.gitkeep"
  touch "$LAB_PATH/reports/.gitkeep"
  touch "$LAB_PATH/screenshots/.gitkeep"

  # fix
  touch "$LAB_PATH/fix/fix.java"
  touch "$LAB_PATH/fix/fix.py"
  touch "$LAB_PATH/fix/notes.md"

  # vuln
  touch "$LAB_PATH/vuln/vuln.java"
  touch "$LAB_PATH/vuln/vuln.py"
  touch "$LAB_PATH/vuln/vuln_config.json"

  echo "payload template" > "$LAB_PATH/vuln/payloads/payloads.txt"

  # tests
  touch "$LAB_PATH/tests/test_fix.py"
  touch "$LAB_PATH/tests/test_vuln.py"

done

#####################################
# MAIN README
#####################################
echo "[+] Writing README..."

cat > "$CORS_DIR/README.md" << 'EOF'
# CORS Vulnerability Labs

This module contains structured labs for CORS misconfigurations.

## Labs

- Lab 01: Basic Origin Reflection
- Lab 02: Trusted Null Origin
- Lab 03: Insecure Protocol Trust

Each lab includes:
- Vulnerable implementation
- Secure fix
- Payloads
- Tests
- Documentation
EOF

#####################################
# GIT OPERATIONS
#####################################
echo "[+] Git staging..."

cd "$REPO_DIR"

git add cors

git commit -m "Refactor CORS labs into standardized pentest architecture"

git push origin main

echo "[+] DONE ✔ CORS structure rebuilt successfully"
