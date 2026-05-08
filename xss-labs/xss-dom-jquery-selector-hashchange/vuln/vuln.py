"""
VULNERABLE: jQuery $() used as selector with location.hash value.
When hash contains HTML, jQuery creates and inserts it into the DOM.
"""
from flask import Flask
app = Flask(__name__)

@app.route("/")
def index():
    return """<!DOCTYPE html><html>
    <head><script src="https://code.jquery.com/jquery-1.12.4.min.js"></script></head>
    <body>
    <script>
        // VULN: jQuery $() with user-controlled string acts as HTML factory
        $(window).on('hashchange', function(){
            var post = $('section[id=' + decodeURIComponent(location.hash.slice(1)) + ']');
            if (post) post[0].scrollIntoView();
        });
        // If hash looks like HTML, jQuery creates it → DOM XSS
        // Exploit: #<img src=x onerror=print()>
    </script>
    </body></html>"""
