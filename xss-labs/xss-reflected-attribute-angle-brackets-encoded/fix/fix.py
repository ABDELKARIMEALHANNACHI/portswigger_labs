from flask import Flask, request
from markupsafe import escape

app = Flask(__name__)

@app.route("/search")
def search():
    query = escape(request.args.get("search", ""))
    # FIX: escape() encodes " as &quot; — cannot break out of attribute
    return f'<html><body><input value="{query}"></body></html>'
