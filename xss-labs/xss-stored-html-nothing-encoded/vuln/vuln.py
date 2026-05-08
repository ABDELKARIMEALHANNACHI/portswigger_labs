"""
VULNERABLE: Stored XSS — comment content saved raw to DB, rendered without encoding.
"""
from flask import Flask, request, redirect
import sqlite3

app = Flask(__name__)

def get_db():
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE IF NOT EXISTS comments (body TEXT)")
    return db

DB = get_db()

@app.route("/post", methods=["GET"])
def get_post():
    comments = DB.execute("SELECT body FROM comments").fetchall()
    comments_html = "".join(f"<p>{c[0]}</p>" for c in comments)  # VULN: raw
    return f"<html><body>{comments_html}<form method=POST><input name=body><button>Post</button></form></body></html>"

@app.route("/post", methods=["POST"])
def post_comment():
    body = request.form.get("body", "")
    DB.execute("INSERT INTO comments VALUES (?)", (body,))  # stored as-is
    DB.commit()
    return redirect("/post")

if __name__ == "__main__":
    app.run(debug=True)
