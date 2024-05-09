# Configure route for admin activities.  

from flask import Blueprint, jsonify, redirect, request, render_template
from core.api.APIRepository.repository import handle_get_request
from core.utils.constants.constants import Routes
from core.models import User

from flask_login import login_user

from werkzeug.security import check_password_hash, generate_password_hash, gen_salt
from flask_jwt_extended import (
    create_access_token,
    set_access_cookies,
)


admin = Blueprint('admin', __name__)

admin.get(Routes.ADMIN_DASHBOARD)
def home():
    return render_template('backend/admin/dashboard.html')

admin.get(Routes.ADMIN_USERS)
def get_user():
    response_data = handle_get_request(User, True)
    return jsonify(response_data);


admin.get(Routes.ADMIN_LOGIN)
def get_login_page():
    return render_template('frontend/front/layout.html')

admin.post(Routes.ADMIN_LOGIN)
def sign_in_user():
    data = request.get_json()

    email = data["email"]
    password = data["password"]

    user = User.query.filter(User.email == email).first()

    if user and check_password_hash(user.password, password):
        # Login the user using Flask-Login
        login_user(user, remember=True)
        identity = {"id": user.id, "email": user.email}
        # Create and return the access token in the headers
        access_token = create_access_token(identity=identity)
        response = jsonify({"msg": "login sucessful"})
        set_access_cookies(response, access_token)
        return response, 200

    else:
        return jsonify({"message": "incorrect login detaila"}), 403