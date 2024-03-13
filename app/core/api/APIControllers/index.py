from flask import Blueprint, render_template, url_for


index = Blueprint("index", __name__)


# home view
@index.get("/doc")
def home():
    return render_template("api/doc.html")
