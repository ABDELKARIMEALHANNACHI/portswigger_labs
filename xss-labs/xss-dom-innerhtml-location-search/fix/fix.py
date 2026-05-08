from flask import Flask
app = Flask(__name__)

@app.route("/")
def index():
    return """<!DOCTYPE html><html><body>
    <div id="result"></div>
    <script>
        var query = new URLSearchParams(location.search).get('search') || '';
        // FIX: textContent — never parses as HTML, purely text
        document.getElementById('result').textContent = 'Results for: ' + query;
    </script></body></html>"""
