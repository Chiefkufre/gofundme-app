import flask
import validators
import os

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
from werkzeug.security import check_password_hash, generate_password_hash, gen_salt
from core.models import User
from core.utils.validators import PlatformValidator

auths = Blueprint("auths", __name__)

validators = PlatformValidator(User)


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

    # Validate if required data are passed
    validate_error = validators.validate_json_request(request.get_json())
    if validate_error:
        return validate_error
    
    # Validate Email uniqueness
    request_email = request.get_json()['email'];
    email_error = validators.validate_email(request_email)
    
    
    try:



        hashed_password = generate_password_hash(password)

        new_user = User(email=email, password=hashed_password, name=name, bio=bio)

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
def signin_user():
    data = request.get_json()

    email = data["email"]
    password = data["password"]

    user = User.query.filter(User.email == email).first()
    print(user.password)
    check_password = check_password_hash(user.password, password)

    if check_password:
        login_user(user, remember=True)
        return redirect(url_for("index.home")), 200

    else:
        return jsonify({"message": "incorrect login detaila"}), 403


# Logout control center


@auths.route("/logout")
@login_required
def logout():
    logout_user()
    return
