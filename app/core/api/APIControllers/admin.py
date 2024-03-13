# Configure route for admin activities.  

from flask import Blueprint, jsonify, redirect, request
from app.core.utils.helpers import handle_get_request
from core.models import User

admin = Blueprint('admin', __name__)

admin.get('admin/users')
def get_user():
    response_data = handle_get_request(User, True)
    return jsonify(response_data);
