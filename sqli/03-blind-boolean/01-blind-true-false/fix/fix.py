from flask import Flask, request
import sqlite3

app = Flask(__name__)

@app.route("/user")
def user():

    username = request.args.get("username", "")

    conn = sqlite3.connect("app.db")
    cur = conn.cursor()

    query = "SELECT id, username FROM users WHERE username = ?"

    result = cur.execute(query, (username,)).fetchone()

    return {"exists": bool(result)}
