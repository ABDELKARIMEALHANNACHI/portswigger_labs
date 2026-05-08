"""
VULNERABLE: User-controlled path reflected into <link rel=canonical href=...>
Allows injection of accesskey + onclick attributes → XSS via keyboard shortcut.
"""
from flask import Flask, request

app = Flask(__name__)

@app.route("/")
def index():
    path = request.path + ("?" + request.query_string.decode() if request.query_string else "")
    # VULN: full URL (including query string) injected into canonical href
    return f"""<!DOCTYPE html><html>
    <head>
    <link rel="canonical" href="https://vulnerable-lab.com{path}"/>
    </head>
    <body><h1>Home</h1></body></html>"""
