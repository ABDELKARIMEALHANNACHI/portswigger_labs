from flask import Flask, request
import sqlite3

app = Flask(__name__)

@app.route("/product")
def product():

    pid = request.args.get("id", "")

    conn = sqlite3.connect("app.db")
    cur = conn.cursor()

    # Vulnerable query with no sanitization
    query = f"SELECT name, price FROM products WHERE id = {pid}"

    print("[SQL]", query)

    try:
        result = cur.execute(query).fetchall()
        return {"result": result}

    except Exception as e:
        # ❌ ERROR LEAKAGE (real-world misconfig)
        return {
            "error": str(e),
            "query": query
        }

if __name__ == "__main__":
    app.run(debug=True)
