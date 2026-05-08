from flask import Flask, request, jsonify, redirect
import sqlite3, json

app = Flask(__name__)
DB = sqlite3.connect(":memory:", check_same_thread=False)
DB.execute("CREATE TABLE comments (body TEXT)")

@app.route("/post-comment", methods=["POST"])
def post():
    body = request.form.get("body","")
    DB.execute("INSERT INTO comments VALUES (?)", (body,))  # store raw
    DB.commit()
    return redirect("/")

@app.route("/api/comments")
def get_comments():
    rows = DB.execute("SELECT body FROM comments").fetchall()
    return jsonify([{"body": r[0]} for r in rows])

@app.route("/")
def index():
    return """<!DOCTYPE html><html><body>
    <div id="comments"></div>
    <script>
        fetch('/api/comments').then(r=>r.json()).then(comments=>{
            comments.forEach(c=>{
                var p = document.createElement('p');
                // FIX: textContent — never interprets as HTML
                p.textContent = c.body;
                document.getElementById('comments').appendChild(p);
            });
        });
    </script></body></html>"""
