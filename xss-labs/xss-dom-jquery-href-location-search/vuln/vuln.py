"""
VULNERABLE: jQuery sets href attribute from location.search — allows javascript: URI.
"""
from flask import Flask
app = Flask(__name__)

@app.route("/feedback")
def feedback():
    return """<!DOCTYPE html><html>
    <head><script src="https://code.jquery.com/jquery-3.6.0.min.js"></script></head>
    <body>
    <a id="backLink">Back</a>
    <script>
        // VULN: jQuery .attr('href') with user-controlled value
        // Allows javascript:alert(1) URI scheme
        var returnUrl = new URLSearchParams(location.search).get('returnPath');
        $('#backLink').attr('href', returnUrl);
    </script>
    </body></html>"""
