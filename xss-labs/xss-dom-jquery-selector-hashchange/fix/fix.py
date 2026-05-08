from flask import Flask
app = Flask(__name__)

@app.route("/")
def index():
    return """<!DOCTYPE html><html>
    <head><script src="https://code.jquery.com/jquery-3.6.0.min.js"></script></head>
    <body>
    <script>
        $(window).on('hashchange', function(){
            var hash = decodeURIComponent(location.hash.slice(1));
            // FIX: validate hash is an alphanumeric ID — not arbitrary HTML
            if (/^[a-zA-Z0-9_-]+$/.test(hash)) {
                var post = $('section[id="' + hash + '"]');
                if (post.length) post[0].scrollIntoView();
            }
        });
    </script>
    </body></html>"""
