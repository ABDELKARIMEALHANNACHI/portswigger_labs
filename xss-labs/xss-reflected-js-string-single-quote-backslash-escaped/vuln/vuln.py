"""
VULNERABLE: ' escaped to \' and \ escaped to \\ — but </script> not handled.
Closing the script tag bypasses JS string escaping entirely.
"""
from flask import Flask, request

app = Flask(__name__)

@app.route("/search")
def search():
    query = request.args.get("search","")
    # Escapes ' and \ but not < > — doesn't help when you close </script>
    safe = query.replace("\\","\\\\").replace("'","\\'")
    return f"""<html><body>
    <script>var q = '{safe}'; doSearch(q);</script>
    </body></html>"""
