"""
VULNERABLE: Some SVG tags allowed. <animatetransform> with onbegin bypasses filter.
"""
from flask import Flask, request
import re

app = Flask(__name__)

BLOCKED = re.compile(r'<(script|img|body|iframe|input|form|object|embed)', re.I)
BLOCKED_EVENTS = re.compile(r'\s+on(?!begin)\w+\s*=', re.I)  # blocks most events but misses onbegin

@app.route("/search")
def search():
    query = request.args.get("search","")
    if BLOCKED.search(query) or BLOCKED_EVENTS.search(query):
        return "<p>Not allowed</p>"
    return f"<html><body>{query}</body></html>"
