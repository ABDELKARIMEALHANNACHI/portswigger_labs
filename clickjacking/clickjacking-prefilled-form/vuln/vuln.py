from flask import Flask, request

app = Flask(__name__)

@app.route("/update", methods=["GET","POST"])
def update():
    email = request.args.get("email","")
    return f'''
    <form method="POST">
        <input type="hidden" name="email" value="{email}">
        <button>Submit</button>
    </form>
    '''
