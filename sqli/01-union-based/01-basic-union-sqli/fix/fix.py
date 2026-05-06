from flask import Flask, request
import sqlite3

app = Flask(**name**)

@app.route("/")
def index():

```
category = request.args.get("category", "")

conn = sqlite3.connect("store.db")
cur = conn.cursor()

# ============================================================
# SECURE PARAMETERIZED QUERY
# ============================================================

query = """
    SELECT id, name, price
    FROM products
    WHERE category = ?
"""

rows = cur.execute(query, (category,)).fetchall()

return {"rows": rows}
```

