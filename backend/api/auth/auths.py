import flask
import validators

from flask import (
    Blueprint,
    redirect,
    abort,
    Blueprint,
    flash,
    request,
    url_for,
    jsonify,
)
from flask_login import login_required, login_user, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from api.models import User
from api.utils.validators import validate_email


auths = Blueprint("auths", __name__)


@auths.post("/register")
def register_user():

    """Register new User

    :param  id: user id-auto-regenerated
    :param  name : new user name
    :type name: str
    :param email: new user email 
    :type email: str
    :param password: new user password
    :type password: str
    :param bio: new user bio
    :type bio: str
    :raises HTTPException for different validation errors
    :return: new user detail
    :rtype: JSON object
    """

    data = request.get_json()

    email = data['email']
    name = data['name']
    password = data['password']
    bio = data['bio']

    try:
        if not all([email, name, bio, password]):
            return jsonify({"message": "Missing required fields"}), 400
        
        validate_email(email)

        new_user = User(**data)
        new_user.insert()
        
        return jsonify({"message": "User created successfully"}), 201

    except ValueError as e:
        return jsonify({"message": str(e)}), 400
        campaign.rollback()

    return jsonify({
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "bio": user.bio
    })


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
