"""
VULNERABLE: All standard HTML tags blocked. Custom elements allowed.
Custom elements can have autofocus + onfocus → no user interaction needed.
"""
from flask import Flask, request
import re

app = Flask(__name__)

# Blocks all known standard HTML tags
STANDARD_TAGS = re.compile(
    r'<(script|img|svg|body|iframe|object|embed|input|button|'
    r'form|link|style|html|head|meta|div|span|p|a|table|details|'
    r'marquee|video|audio|base|frame|frameset|isindex|layer)',
    re.I
)

@app.route("/search")
def search():
    query = request.args.get("search", "")
    if STANDARD_TAGS.search(query):
        return "<p>Tag not allowed</p>"
    return f"<html><body><p>{query}</p></body></html>"
