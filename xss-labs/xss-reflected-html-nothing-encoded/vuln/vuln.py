"""
VULNERABLE: Reflected XSS — user input echoed directly into HTML with no encoding.
"""
from flask import Flask, request, render_template_string

app = Flask(__name__)

TEMPLATE = """
<!DOCTYPE html><html><body>
<form method="GET">
  <input name="search" value="">
  <button>Search</button>
</form>
<p>Results for: {{ query|safe }}</p>   <!-- VULN: |safe disables autoescaping -->
</body></html>
"""

@app.route("/search")
def search():
    query = request.args.get("search", "")
    # VULN: raw f-string injection — no encoding at all
    return f"<html><body><p>Results for: {query}</p></body></html>"

if __name__ == "__main__":
    app.run(debug=True)
