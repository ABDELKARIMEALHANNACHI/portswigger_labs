from flask import Flask, request
import sqlite3

app = Flask(__name__)

@app.route("/profile/update", methods=["POST"])
def update():

    bio = request.form.get("bio", "")

    conn = sqlite3.connect("app.db")
    cur = conn.cursor()

    cur.execute(f"INSERT INTO profiles(bio) VALUES('{bio}')")
    conn.commit()

    return {"status": "saved"}

@app.route("/admin/export")
def export():

    conn = sqlite3.connect("app.db")
    cur = conn.cursor()

    # business logic query
    return {"export": cur.execute("SELECT bio FROM profiles").fetchall()}

if __name__ == "__main__":
    app.run(debug=True)
