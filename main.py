from flask import Flask, render_template, redirect
from flask_login import login_required, current_user, login_user, logout_user
from models import UserModel, db, login
from forms import LoginForm, RegisterForm


app = Flask(__name__)
app.secret_key = "super-secret-key"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = "static/images"


db.init_app(app)
login.init_app(app)
login.login_view = "login"


def get_username():
    if current_user.is_authenticated:
        return current_user.username
    return "Guest"


@app.route("/")
def index():
    return render_template("index.html", page_title="Home", user=get_username())


@app.route("/login", methods=["GET", "POST"])
def login():
    message = ""
    if current_user.is_authenticated:
        return redirect("/")

    form = LoginForm()
    if form.validate_on_submit():
        user = UserModel.query.filter_by(username=form.username.data).first()
        if user:
            if user.check_password(form.password.data):
                login_user(user)
                return redirect("/")
        message = "Invalid username or password"
    return render_template(
        "login/login.html",
        form=form,
        page_title="Login",
        message=message,
    )


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect("/")

    message = ""
    form = RegisterForm()
    if form.validate_on_submit():
        check = UserModel.query.filter_by(username=form.username.data).first()
        if check:
            message = "Username has been taken"
        else:
            user = UserModel(username=form.username.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect("/")
    else:
        message = "Passwords do not match"
    return render_template("login/register.html", form=form, page_title="Register", message=message)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")

@app.route("/sidenav")
def sidenav():
    return render_template("side-nav-base.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
