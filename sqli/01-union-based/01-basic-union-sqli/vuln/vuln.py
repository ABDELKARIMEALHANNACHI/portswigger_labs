from flask import Flask, request, render_template_string
import sqlite3

app = Flask(**name**)

DB = "store.db"

HTML = """

<h1>Product Search</h1>

<form method="GET">
  <input type="text" name="category" placeholder="category">
  <button>Search</button>
</form>

<hr>

{% for row in rows %}

<div>
  <b>{{ row[1] }}</b><br>
  Price: ${{ row[2] }}
</div>
<hr>
{% endfor %}
"""

@app.route("/")
def index():

```
category = request.args.get("category", "")

conn = sqlite3.connect(DB)
cur = conn.cursor()

# =====================================================================
# VULNERABLE QUERY
# =====================================================================

query = f"""
    SELECT id, name, price
    FROM products
    WHERE category = '{category}'
"""

print(f"[DEBUG] Executing SQL: {query}")

rows = cur.execute(query).fetchall()

return render_template_string(HTML, rows=rows)
```

if **name** == "**main**":
app.run(debug=True)
