import email
from hashlib import sha256
from unicodedata import category

import validators

import flask
from flask import redirect, abort, Blueprint, flash, url_for, jsonify
from api.models import User, Contact, Campaign



views = Blueprint("views", __name__)



@views.get("campaign/<int:id>")
def get_campaign(id):

    return "nothing"
# /api/
#     /auth/
#         POST /register
#         POST /login
#         POST /logout
#     /campaigns/
#         GET /
#         POST /
#         GET /<campaign_id>
#         PUT /<campaign_id>
#         DELETE /<campaign_id>
#     /donations/
#         GET /<campaign_id>cd back
#         POST /<campaign_id>
#     /users/
#         GET /
#         GET /<user_id>
#         PUT /<user_id>
#         DELETE /<user_id>

