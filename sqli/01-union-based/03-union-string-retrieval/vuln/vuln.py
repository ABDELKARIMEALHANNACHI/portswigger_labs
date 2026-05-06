from flask import Flask, request
import sqlite3

app = Flask(__name__)

@app.route("/search")
def search():

    q = request.args.get("q", "")

    conn = sqlite3.connect("store.db")
    cur = conn.cursor()

    # Vulnerable query
    query = f"""
        SELECT id, name, description
        FROM products
        WHERE name LIKE '%{q}%'
    """

    print("[SQL]", query)

    return {"results": cur.execute(query).fetchall()}

if __name__ == "__main__":
    app.run(debug=True)
