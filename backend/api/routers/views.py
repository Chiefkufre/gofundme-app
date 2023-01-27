import email
from hashlib import sha256
from unicodedata import category

import validators

import flask
from flask import redirect, abort, Blueprint, flash, url_for, jsonify
from api.models import User, Contact, Campaign



views = Blueprint("views", __name__)

#   TODO: create campaigns
#         POST / campaigns


# TODO: Get all campaign models
    #  GET /campaigns/
     

# TODO: Get all campaigns by on Id
# GET /<campaign_id>

#  TODO: update capaigns based on id
#  PUT /<campaign_id>


# TODO: delete capaigns based on id
#  DELETE /<campaign_id>



# ----------------ROuter for handling donation requests--------------

#   TODO: make campaigns
#  /donations//<campaign_id>


#  TODO: get campaigns
#         GET /donations/<campaign_id>
#         


# -------------------Routers for Users Dashboard

# TODO: Get all users
# GET users/users/

# TODO: get users by id
# GET users/<user_id>


# TODO: update users by id
# PUT users/<user_id>

# TODO: delete users by id
#   DELETE users/<user_id>

