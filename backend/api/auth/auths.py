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

    email = data["email"]
    name = data["name"]
    password = data["password"]
    bio = data["bio"]

    try:
        if not email:
            return jsonify({"message": "Email is required"}), 400
        if not name:
            return jsonify({"message": "Name is required"}), 400
        if not bio:
            return jsonify({"message": "Bio is required"}), 400
        if not password:
            return jsonify({"message": "Password is required"}), 400

        validate_email(email)
        

        salt = os.urandom(16)
        hashed_password = generate_password_hash(password, salt=salt)

        new_password = generate_password_hash(password)
        
        new_user = User(email=email, password=new_password, name=name, bio=bio)

        new_user.insert()

        return (
            jsonify(
                {
                    "message": "User created successfully",
                    "id": new_user.id,
                    "name": new_user.name,
                    "email": new_user.email,
                    "bio": new_user.bio,
                }
            ),
            201,
        )

    except ValueError as e:
        return jsonify({"message": str(e)}), 400
        campaign.rollback()


# function to handle posting to login route
@auths.post("/login")
def login_user():
    
    data = request.get_json()

    email  = data["email"]
    password = data["password"]

    user = User.query.filter(User.email == email).first()

    check_password = check_password_hash(user.password, password)


    return


# Logout control center


@auths.route("/logout")
@login_required
def logout():

    logout_user()
    return
