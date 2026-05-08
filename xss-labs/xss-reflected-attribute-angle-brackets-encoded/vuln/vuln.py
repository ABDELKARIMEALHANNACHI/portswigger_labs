"""
VULNERABLE: Angle brackets encoded but input reflected INSIDE an HTML attribute.
Breaking out of the attribute with " onmouseover="alert(1) bypasses the filter.
"""
from flask import Flask, request
from markupsafe import Markup

app = Flask(__name__)

@app.route("/search")
def search():
    query = request.args.get("search", "")
    # Encodes < > but NOT " — VULN when input is inside an attribute
    safe_query = query.replace("<", "&lt;").replace(">", "&gt;")
    return f'<html><body><input value="{safe_query}"></body></html>'
