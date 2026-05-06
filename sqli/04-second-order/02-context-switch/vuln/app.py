from flask import Flask, request
import sqlite3

app = Flask(__name__)

@app.route("/comment", methods=["POST"])
def comment():

    c = request.form.get("comment", "")

    conn = sqlite3.connect("app.db")
    cur = conn.cursor()

    cur.execute(f"INSERT INTO comments(text) VALUES('{c}')")
    conn.commit()

    return {"ok": True}

@app.route("/admin/review")
def review():

    conn = sqlite3.connect("app.db")
    cur = conn.cursor()

    # different execution context
    return {"data": cur.execute("SELECT text FROM comments").fetchall()}

if __name__ == "__main__":
    app.run(debug=True)
