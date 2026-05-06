from flask import Flask, request
import sqlite3

app = Flask(__name__)

@app.route("/search")
def search():

    q = request.args.get("q", "")

    conn = sqlite3.connect("store.db")
    cur = conn.cursor()

    query = """
        SELECT id, name, description
        FROM products
        WHERE name LIKE ?
    """

    return {
        "results": cur.execute(query, (f"%{q}%",)).fetchall()
    }
