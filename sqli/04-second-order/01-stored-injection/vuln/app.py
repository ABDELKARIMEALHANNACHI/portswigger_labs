from flask import Flask, request
import sqlite3

app = Flask(__name__)

@app.route("/register", methods=["POST"])
def register():

    username = request.form.get("username", "")

    conn = sqlite3.connect("app.db")
    cur = conn.cursor()

    # stored directly (unsafe)
    cur.execute(f"INSERT INTO users(username) VALUES('{username}')")
    conn.commit()

    return {"status": "registered"}

@app.route("/admin/users")
def admin():

    conn = sqlite3.connect("app.db")
    cur = conn.cursor()

    # later execution context
    result = cur.execute("SELECT username FROM users").fetchall()

    return {"users": result}

if __name__ == "__main__":
    app.run(debug=True)
