from flask import Flask, request

app = Flask(__name__)

@app.route("/update-email", methods=["GET","POST"])
def update_email():
    if request.method == "POST":
        return "Email updated"
    return '''
    <form method="POST">
        <input name="email">
        <button>Update</button>
    </form>
    '''
