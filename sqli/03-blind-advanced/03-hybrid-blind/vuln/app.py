from flask import Flask, request
import sqlite3
import time

app = Flask(__name__)

@app.route("/profile")
def profile():

    username = request.args.get("username", "")

    conn = sqlite3.connect("app.db")
    cur = conn.cursor()

    query = f"SELECT username FROM users WHERE username = '{username}'"

    try:
        cur.execute(query).fetchone()
    except:
        pass

    # artificial delay channel
    time.sleep(0.2)

    return {"status": "ok"}

if __name__ == "__main__":
    app.run(debug=True)
