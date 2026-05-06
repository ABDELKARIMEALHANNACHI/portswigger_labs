from flask import Flask, request
import sqlite3

app = Flask(__name__)

@app.route("/check")
def check():

    q = request.args.get("q", "")

    conn = sqlite3.connect("app.db")
    cur = conn.cursor()

    query = f"SELECT 1 FROM users WHERE username = '{q}'"

    try:
        res = cur.execute(query).fetchone()
        return {"result": bool(res)}
    except:
        return {"result": False}

if __name__ == "__main__":
    app.run(debug=True)
