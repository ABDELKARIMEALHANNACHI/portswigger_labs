from flask import Flask, request

app = Flask(__name__)

@app.route("/search")
def search():
    q = request.args.get("q", "")

    # weak regex WAF
    blacklist = ["union", "select", "drop"]

    for b in blacklist:
        if b in q.lower():
            return {"blocked": True}

    # but DB still interprets SQL normally
    return {"query": q}

if __name__ == "__main__":
    app.run(debug=True)
