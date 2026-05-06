from flask import Flask, request

app = Flask(__name__)

@app.route("/check")
def check():
    q = request.args.get("q", "")

    # Simulated unsafe backend query
    return {"result": "processed: " + q}

if __name__ == "__main__":
    app.run(debug=True)
