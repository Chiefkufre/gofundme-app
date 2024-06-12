# Configure route for admin activities.

from flask import Blueprint, current_app, flash, jsonify, redirect, request, render_template, url_for
from core.src.Repository.repository import _get_item, get_item_data, handle_get_request
from core.utils.constants.constants import Routes
from core.models import Campaign, User

from flask_login import login_required, login_user

from werkzeug.security import check_password_hash, generate_password_hash, gen_salt
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    set_access_cookies,
)


admin = Blueprint("admin", __name__)

@admin.get(Routes.ADMIN_DASHBOARD)
def admin_dasboard():
    return render_template("backend/admin/dashboard.html")


@admin.get(Routes.ADMIN_USERS)
@login_required
@jwt_required()
def get_user():
    response_data = handle_get_request(User, True)
    return jsonify(response_data)

@admin.patch(Routes.CAMPAIGN_STATUS)
@login_required
@jwt_required()
def toggle_campaign_status(id):
    req = request.form.get('status')
    status = False
    if req == 'true':
        status = True
    item = _get_item(Campaign, id)
    if item:
        item.toggle(status)
        current_app.logger.info(
            f" Campaign - '{item.serialize()['title']}' is {item.serialize()['is_active']}"
        )
    data = {}
    if item.serialize()['is_active'] == True:
        data['message'] = "Your campaign status is now active"
    else:
        data['message'] = "Unable to activate your campaign now"
    flash(data['message'])
    return redirect(url_for('admin.admin_dasboard'))

@admin.get(Routes.SINGLE_USER)
@login_required
@jwt_required()
def get_user_by_id(id):
    user = get_item_data(User, id)
    return jsonify(user.serialize())

@admin.get(Routes.ADMIN_LOGIN)
def get_login_page():
    return render_template("backend/admin/login.html")


@admin.post(Routes.ADMIN_LOGIN)
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


