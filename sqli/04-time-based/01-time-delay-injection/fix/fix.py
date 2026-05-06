from flask import Flask, request
import sqlite3

app = Flask(__name__)

@app.route("/profile")
def profile():

    username = request.args.get("username", "")

    conn = sqlite3.connect("app.db")
    cur = conn.cursor()

    query = "SELECT id FROM users WHERE username = ?"

    cur.execute(query, (username,)).fetchone()

    return {"status": "ok"}
