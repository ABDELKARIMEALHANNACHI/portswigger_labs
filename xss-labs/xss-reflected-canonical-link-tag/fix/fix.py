from flask import Flask, request
from markupsafe import escape

app = Flask(__name__)

@app.route("/")
def index():
    # FIX: only use the path, fully HTML-attribute-encoded
    safe_path = escape(request.path)
    return f"""<!DOCTYPE html><html>
    <head>
    <link rel="canonical" href="https://vulnerable-lab.com{safe_path}"/>
    </head>
    <body><h1>Home</h1></body></html>"""
