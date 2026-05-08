"""
VULNERABLE: Website field rendered inside onclick="trackLink('URL')"
' and \ escaped, < > " encoded — but HTML entities decoded in onclick attribute.
Injecting &apos; (HTML entity for ') bypasses the JS string escaping.
"""
from flask import Flask, request, redirect
import html, sqlite3

app = Flask(__name__)
DB = sqlite3.connect(":memory:", check_same_thread=False)
DB.execute("CREATE TABLE comments (author TEXT, website TEXT)")

@app.route("/comment", methods=["POST"])
def comment():
    author  = request.form.get("author","")
    website = request.form.get("website","")
    # Encode AND escape
    safe_web = html.escape(website).replace("'","\\'").replace("\\","\\\\")
    DB.execute("INSERT INTO comments VALUES (?,?)", (author, safe_web))
    DB.commit()
    return redirect("/")

@app.route("/")
def index():
    rows = DB.execute("SELECT author, website FROM comments").fetchall()
    html_out = ""
    for author, website in rows:
        # VULN: website inside onclick="trackLink('...')" 
        # HTML entity &apos; is decoded by HTML parser before JS sees it
        html_out += f'<a href="#" onclick="trackLink(\'{website}\')">{author}</a>'
    return f"<html><body>{html_out}</body></html>"
