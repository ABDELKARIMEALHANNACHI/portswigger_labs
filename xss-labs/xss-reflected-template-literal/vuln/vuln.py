"""
VULNERABLE: User input reflected inside a JS template literal `...${input}...`
All quotes and angle brackets escaped/encoded — but ${} is NOT a quote/bracket.
"""
from flask import Flask, request
import html

app = Flask(__name__)

@app.route("/search")
def search():
    query = request.args.get("search","")
    # Encodes < > ' " \ — but ${} syntax doesn't use any of these
    safe = html.escape(query).replace("'","\\'").replace("\\","\\\\")
    return f"""<html><body>
    <script>
        var msg = `Hello {safe}, your results are ready.`;
        document.getElementById('msg').textContent = msg;
    </script>
    </body></html>"""
