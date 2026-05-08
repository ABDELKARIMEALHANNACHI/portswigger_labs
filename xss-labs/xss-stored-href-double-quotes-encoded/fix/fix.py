from flask import Flask, request, redirect
from markupsafe import escape
import sqlite3
from urllib.parse import urlparse

app = Flask(__name__)
DB = sqlite3.connect(":memory:", check_same_thread=False)
DB.execute("CREATE TABLE comments (author TEXT, website TEXT, body TEXT)")

def is_safe_url(url):
    """Allow only http/https URLs."""
    if not url:
        return False
    try:
        parsed = urlparse(url)
        return parsed.scheme in ("http", "https")
    except Exception:
        return False

@app.route("/comment", methods=["POST"])
def post_comment():
    website = request.form.get("website", "")
    # FIX: validate scheme before storing
    if not is_safe_url(website):
        website = ""
    DB.execute("INSERT INTO comments VALUES (?,?,?)",
               (request.form.get("author",""), website, request.form.get("body","")))
    DB.commit()
    return redirect("/")

@app.route("/")
def index():
    rows = DB.execute("SELECT author, website, body FROM comments").fetchall()
    html = ""
    for author, website, body in rows:
        safe_author  = escape(author)
        safe_website = escape(website)
        safe_body    = escape(body)
        html += f'<p><a href="{safe_website}">{safe_author}</a>: {safe_body}</p>'
    return f"<html><body>{html}</body></html>"
