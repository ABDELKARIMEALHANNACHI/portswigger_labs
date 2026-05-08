"""
FIX: HTML-encode stored content at RENDER time (encode on output, not input).
"""
from flask import Flask, request, redirect
from markupsafe import escape
import sqlite3

app = Flask(__name__)
DB = sqlite3.connect(":memory:", check_same_thread=False)
DB.execute("CREATE TABLE comments (body TEXT)")

@app.route("/post")
def get_post():
    comments = DB.execute("SELECT body FROM comments").fetchall()
    # FIX: escape at render time
    comments_html = "".join(f"<p>{escape(c[0])}</p>" for c in comments)
    return f"<html><body>{comments_html}</body></html>"

@app.route("/post", methods=["POST"])
def post_comment():
    body = request.form.get("body", "")
    DB.execute("INSERT INTO comments VALUES (?)", (body,))
    DB.commit()
    return redirect("/post")
