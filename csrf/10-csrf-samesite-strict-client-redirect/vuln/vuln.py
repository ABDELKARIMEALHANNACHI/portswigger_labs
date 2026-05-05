from flask import Flask, request, session, redirect

app = Flask(__name__)

@app.route("/my-account/change-email", methods=["POST"])
def change_email():

    # Vulnerable CSRF implementation

    email = request.form.get("email")

    update_email(session["username"], email)

    return redirect("/my-account")
