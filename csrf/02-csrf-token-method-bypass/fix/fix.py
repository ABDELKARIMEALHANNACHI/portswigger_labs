from flask_wtf.csrf import CSRFProtect
import secrets

app.secret_key = secrets.token_hex(32)

csrf = CSRFProtect(app)

@app.route("/my-account/change-email", methods=["POST"])
def change_email():

    token = request.form.get("csrf_token")

    validate_csrf(token)

    update_email(
        session["username"],
        request.form.get("email")
    )

    return redirect("/my-account")
