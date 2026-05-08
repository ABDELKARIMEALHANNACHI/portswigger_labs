"""
VULNERABLE: WAF blocks most HTML tags/events — but <body> onresize allowed.
PortSwigger solution: fuzz allowed tags with Burp Intruder, then find allowed event.
"""
from flask import Flask, request
import re

app = Flask(__name__)

BLOCKED_TAGS = re.compile(r'<(script|img|svg|iframe|object|embed|link|style|form|input|button)', re.I)
BLOCKED_EVENTS = re.compile(r'\s+on\w+\s*=', re.I)

@app.route("/search")
def search():
    query = request.args.get("search","")
    if BLOCKED_TAGS.search(query) or BLOCKED_EVENTS.search(query):
        return "<html><body><p>Tag not allowed</p></body></html>"
    # VULN: <body onresize=...> passes the blocklist — handler fires on window resize
    return f"<html><body><p>{query}</p></body></html>"
