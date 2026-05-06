from flask import Flask, request
import sqlite3

app = Flask(__name__)

@app.route("/product")
def product():
    pid = request.args.get("id", "")

    conn = sqlite3.connect("app.db")
    cur = conn.cursor()

    query = f"SELECT name FROM products WHERE id = {pid}"

    try:
        cur.execute(query)
        return {"ok": True}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    app.run(debug=True)
