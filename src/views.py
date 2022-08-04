from flask import redirect, render_template, abort, Blueprint



views = Blueprint('views', __name__)


@views.route("/")
def home():
    return render_template("pages/home.html")