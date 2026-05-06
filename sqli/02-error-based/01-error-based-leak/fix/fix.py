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
