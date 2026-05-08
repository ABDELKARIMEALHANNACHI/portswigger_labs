from flask import Flask, request
import bleach

ALLOWED_SVG_TAGS = ["svg", "circle", "rect", "path", "text"]
ALLOWED_SVG_ATTRS = {
    "svg": ["xmlns", "width", "height", "viewBox"],
    "circle": ["cx", "cy", "r", "fill"],
    "path": ["d", "fill", "stroke"],
}

app = Flask(__name__)

@app.route("/search")
def search():
    query = request.args.get("search","")
    clean = bleach.clean(query, tags=ALLOWED_SVG_TAGS,
                         attributes=ALLOWED_SVG_ATTRS, strip=True)
    return f"<html><body>{clean}</body></html>"
