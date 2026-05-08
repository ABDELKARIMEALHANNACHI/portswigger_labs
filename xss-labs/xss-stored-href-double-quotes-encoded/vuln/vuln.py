"""
VULNERABLE: Website field stored in DB; rendered in href attribute.
Double quotes encoded but javascript: URI allowed.
"""
from flask import Flask, request, redirect
import sqlite3

app = Flask(__name__)
DB = sqlite3.connect(":memory:", check_same_thread=False)
DB.execute("CREATE TABLE comments (author TEXT, website TEXT, body TEXT)")

@app.route("/comment", methods=["POST"])
def post_comment():
    author  = request.form.get("author", "")
    website = request.form.get("website", "")  # VULN: stored with no scheme validation
    body    = request.form.get("body", "")
    DB.execute("INSERT INTO comments VALUES (?,?,?)", (author, website, body))
    DB.commit()
    return redirect("/")

@app.route("/")
def index():
    rows = DB.execute("SELECT author, website, body FROM comments").fetchall()
    html = ""
    for author, website, body in rows:
        # " encoded as &quot; but javascript: scheme not blocked
        safe_website = website.replace('"', '&quot;').replace('<','&lt;').replace('>','&gt;')
        html += f'<p><a href="{safe_website}">{author}</a>: {body}</p>'
    return f"<html><body>{html}</body></html>"
