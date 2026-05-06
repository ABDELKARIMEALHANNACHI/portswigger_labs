from flask import Flask, request
import sqlite3
import os

app = Flask(__name__)

@app.route("/search")
def search():

    q = request.args.get("q", "")

    conn = sqlite3.connect("app.db")
    cur = conn.cursor()

    try:
        # vulnerable: DB resolves external domain
        cur.execute(f"SELECT load_extension('{q}')")
        return {"status": "ok"}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    app.run(debug=True)
