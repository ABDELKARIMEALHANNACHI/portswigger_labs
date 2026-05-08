"""
FIX: HTML-encode all user input before reflecting it into the page.
Flask's Jinja2 auto-escapes by default — never use |safe with user data.
"""
from flask import Flask, request
from markupsafe import escape

app = Flask(__name__)

@app.route("/search")
def search():
    query = escape(request.args.get("search", ""))   # FIX: HTML-encode
    return f"<html><body><p>Results for: {query}</p></body></html>"
