from flask import Flask, request
import sqlite3

app = Flask(__name__)

@app.route("/user")
def user():

    username = request.args.get("username", "")

    conn = sqlite3.connect("app.db")
    cur = conn.cursor()

    query = f"SELECT username FROM users WHERE username = '{username}'"

    try:
        res = cur.execute(query).fetchone()
        return {"exists": bool(res)}
    except:
        return {"exists": False}

if __name__ == "__main__":
    app.run(debug=True)
