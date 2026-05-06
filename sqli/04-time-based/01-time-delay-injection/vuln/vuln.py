from flask import Flask, request
import sqlite3
import time

app = Flask(__name__)

@app.route("/profile")
def profile():

    username = request.args.get("username", "")

    conn = sqlite3.connect("app.db")
    cur = conn.cursor()

    # Vulnerable time-based injection point
    query = f"""
        SELECT id FROM users
        WHERE username = '{username}'
    """

    print("[SQL]", query)

    start = time.time()

    try:
        cur.execute(query).fetchone()
    except:
        pass

    # Artificial delay simulation (vulnerable pattern in real apps)
    time.sleep(0.2)

    return {
        "status": "ok",
        "time": time.time() - start
    }

if __name__ == "__main__":
    app.run(debug=True)
