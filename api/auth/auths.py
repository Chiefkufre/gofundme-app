import flask
import validators

from flask import (
    Blueprint,
    redirect,
    abort,
    Blueprint,
    flash,
    url_for,
    jsonify,
)
from flask_login import login_required, login_user, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash



auths = Blueprint("auths", __name__)


# user registration control center
@auths.get("/register")
def register_form():


    return 
@auths.post("/register")
def register_user():


    return 

# Function handles login route
@auths.get("/login")
def login_form():
    

    return 

# function to handle posting to login route
@auths.post("/login")
def login_user():
   
    return 


# Logout control center


@auths.route("/logout")
@login_required
def logout():

    logout_user()
    return 
