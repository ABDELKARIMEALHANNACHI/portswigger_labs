"""
VULNERABLE: AngularJS ng-app scope. Input reflected inside ng-app div.
AngularJS evaluates {{ }} expressions — allows sandbox escape.
"""
from flask import Flask, request

app = Flask(__name__)

@app.route("/search")
def search():
    query = request.args.get("search", "")
    # HTML-encodes < > " but AngularJS {{ }} still evaluated
    import html
    safe = html.escape(query)
    return f"""<!DOCTYPE html><html>
    <head><script src="https://ajax.googleapis.com/ajax/libs/angularjs/1.7.9/angular.min.js"></script></head>
    <body ng-app>
    <p>Results for: {safe}</p>
    </body></html>"""
