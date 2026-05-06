from flask import Flask, request
import sqlite3
import urllib.parse

app = Flask(__name__)

@app.route("/product")
def product():
    q = request.args.get("q", "")

    # naive decode filter
    decoded = urllib.parse.unquote(q)

    if "select" in decoded.lower():
        return {"blocked": True}

    return {"ok": True}

if __name__ == "__main__":
    app.run(debug=True)
