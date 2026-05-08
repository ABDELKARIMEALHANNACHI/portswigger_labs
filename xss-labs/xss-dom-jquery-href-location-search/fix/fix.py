from flask import Flask
app = Flask(__name__)

@app.route("/feedback")
def feedback():
    return """<!DOCTYPE html><html>
    <head><script src="https://code.jquery.com/jquery-3.6.0.min.js"></script></head>
    <body>
    <a id="backLink">Back</a>
    <script>
        var returnUrl = new URLSearchParams(location.search).get('returnPath') || '/';
        // FIX: validate URL scheme — only allow http/https
        try {
            var url = new URL(returnUrl, window.location.origin);
            if (url.protocol === 'http:' || url.protocol === 'https:') {
                $('#backLink').attr('href', url.href);
            } else {
                $('#backLink').attr('href', '/');
            }
        } catch(e) {
            $('#backLink').attr('href', '/');
        }
    </script>
    </body></html>"""
