from flask import Flask, request, redirect
import html, sqlite3
from urllib.parse import urlparse

app = Flask(__name__)
DB = sqlite3.connect(":memory:", check_same_thread=False)
DB.execute("CREATE TABLE comments (author TEXT, website TEXT)")

def safe_url(url):
    try:
        p = urlparse(url)
        return p.scheme in ("http","https") and bool(p.netloc)
    except: return False

@app.route("/comment", methods=["POST"])
def comment():
    website = request.form.get("website","")
    if not safe_url(website):
        website = "#"
    DB.execute("INSERT INTO comments VALUES (?,?)",
               (request.form.get("author",""), website))
    DB.commit()
    return redirect("/")

@app.route("/")
def index():
    rows = DB.execute("SELECT author, website FROM comments").fetchall()
    html_out = ""
    for author, website in rows:
        # FIX: use data attribute + external JS handler; avoid inline onclick with URL
        safe_author  = html.escape(author)
        safe_website = html.escape(website)
        html_out += f'<a href="{safe_website}" data-track="true">{safe_author}</a>'
    return f"""<html><body>
    {html_out}
    <script>
    document.querySelectorAll('[data-track]').forEach(function(el){{
        el.addEventListener('click', function(e){{
            trackLink(this.href);  // safe — href is already validated
        }});
    }});
    </script>
    </body></html>"""
