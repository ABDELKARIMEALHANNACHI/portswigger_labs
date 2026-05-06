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
