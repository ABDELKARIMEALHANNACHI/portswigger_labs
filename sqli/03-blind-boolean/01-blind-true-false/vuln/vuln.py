from flask import Flask, request
import sqlite3

app = Flask(__name__)

@app.route("/user")
def user():

    username = request.args.get("username", "")

    conn = sqlite3.connect("app.db")
    cur = conn.cursor()

    # Blind vulnerable query
    query = f"""
        SELECT id, username
        FROM users
        WHERE username = '{username}'
    """

    try:
        result = cur.execute(query).fetchone()

        if result:
            return {"exists": True}
        else:
            return {"exists": False}

    except:
        return {"exists": False}

if __name__ == "__main__":
    app.run(debug=True)
