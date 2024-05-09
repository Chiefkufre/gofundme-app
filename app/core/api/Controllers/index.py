from flask import Blueprint, render_template, url_for
from core.utils.constants.constants import Routes


index = Blueprint("index", __name__)


# home view
@index.get(Routes.DOC)
def home():
    return render_template("api/doc.html")


@index.get(Routes.TEST)
def home2():
    return render_template("frontend/front/home.html")

@index.errorhandler(404)
def page_not_found():
    return render_template("error/404.html")