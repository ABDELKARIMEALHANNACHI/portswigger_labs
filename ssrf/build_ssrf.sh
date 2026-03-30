#!/bin/bash

echo "[+] Starting SSRF lab structure creation..."

# =========================
# LAB LIST
# =========================
labs=(
"basic-ssrf-local-server"
"basic-ssrf-backend-system"
"ssrf-blacklist-filter"
"ssrf-open-redirect-bypass"
"ssrf-whitelist-filter"
"blind-ssrf-oob"
"ssrf-dns-rebinding"
"ssrf-flawed-url-parsing"
"ssrf-validation-bypass-redirect"
"ssrf-open-redirect-chain"
"ssrf-internal-metadata-api"
"ssrf-aws-metadata"
)

# =========================
# CREATE STRUCTURE
# =========================
for lab in "${labs[@]}"; do
    mkdir -p "$lab"/{vuln,fix,exploit,notes}

    touch "$lab/vuln/vuln.py"
    touch "$lab/vuln/vuln.php"
    touch "$lab/vuln/vuln.java"

    touch "$lab/fix/fix.py"
    touch "$lab/fix/fix.php"
    touch "$lab/fix/fix.java"

    touch "$lab/exploit/payloads.txt"
    touch "$lab/exploit/request.txt"
    touch "$lab/exploit/response.txt"

    touch "$lab/notes/explanation.txt"
    touch "$lab/notes/methodology.txt"

    cat <<EOF > "$lab/README.md"
# $lab

## 🎯 Lab Goal

## 🧠 Vulnerability

## ⚔️ Exploitation

## 🛡️ Fix

## 🔥 Payloads

## 📌 Key Takeaways
EOF

done

echo "[+] Structure created."

# =========================
# GIT PUSH (SAFE MODE)
# =========================

echo "[+] Adding changes..."
git add .

echo "[+] Committing..."
git commit -m "Add SSRF labs structure (PortSwigger)"

echo "[+] Pushing..."
git push

echo "[+] DONE 🚀"
