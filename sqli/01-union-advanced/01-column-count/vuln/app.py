from flask import Flask, request
import sqlite3

app = Flask(__name__)

@app.route("/search")
def search():
    q = request.args.get("q", "")

    conn = sqlite3.connect("app.db")
    cur = conn.cursor()

    query = f"SELECT name FROM products WHERE name LIKE '%{q}%'"

    try:
        cur.execute(query)
        return {"status": "ok"}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    app.run(debug=True)
