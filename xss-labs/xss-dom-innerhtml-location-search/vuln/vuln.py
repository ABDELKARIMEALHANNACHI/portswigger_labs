"""
VULNERABLE: innerHTML assigned from location.search — DOM XSS.
Note: innerHTML ignores <script> tags but executes event handlers.
"""
from flask import Flask
app = Flask(__name__)

@app.route("/")
def index():
    return """<!DOCTYPE html><html><body>
    <div id="result"></div>
    <script>
        var query = new URLSearchParams(location.search).get('search');
        // VULN: innerHTML executes event handlers in injected HTML
        document.getElementById('result').innerHTML = 'Results for: ' + query;
    </script></body></html>"""
