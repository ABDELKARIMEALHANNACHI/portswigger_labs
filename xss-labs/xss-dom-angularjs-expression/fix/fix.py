from flask import Flask, request
import html

app = Flask(__name__)

@app.route("/search")
def search():
    query = html.escape(request.args.get("search", ""))
    # FIX: Do NOT use ng-app on pages that reflect user input.
    # If AngularJS must be used, use ng-non-bindable to prevent expression evaluation.
    return f"""<!DOCTYPE html><html>
    <head><script src="https://ajax.googleapis.com/ajax/libs/angularjs/1.7.9/angular.min.js"></script></head>
    <body ng-app>
    <p ng-non-bindable>Results for: {query}</p>
    </body></html>"""
