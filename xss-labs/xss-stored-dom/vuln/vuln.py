"""
VULNERABLE: Comments stored as JSON in DB; JS uses innerHTML to render.
Angle brackets replaced on server but innerHTML re-parses HTML entities.
"""
from flask import Flask, request, jsonify, redirect
import sqlite3, json, html

app = Flask(__name__)
DB = sqlite3.connect(":memory:", check_same_thread=False)
DB.execute("CREATE TABLE comments (data TEXT)")

@app.route("/post-comment", methods=["POST"])
def post():
    body = request.form.get("body","")
    # Developer thinks replacing < > is enough
    safe_body = body.replace("<","&lt;").replace(">","&gt;")
    DB.execute("INSERT INTO comments VALUES (?)", (json.dumps({"body": safe_body}),))
    DB.commit()
    return redirect("/")

@app.route("/api/comments")
def get_comments():
    rows = DB.execute("SELECT data FROM comments").fetchall()
    return jsonify([json.loads(r[0]) for r in rows])

@app.route("/")
def index():
    # JS fetches comments and uses innerHTML — innerHTML decodes &lt; back to <
    return """<!DOCTYPE html><html><body>
    <div id="comments"></div>
    <script>
        fetch('/api/comments').then(r=>r.json()).then(comments=>{
            comments.forEach(c=>{
                var div = document.createElement('div');
                // VULN: innerHTML decodes HTML entities — &lt;script&gt; becomes <script>
                div.innerHTML = '<p>' + c.body + '</p>';
                document.getElementById('comments').appendChild(div);
            });
        });
    </script></body></html>"""
