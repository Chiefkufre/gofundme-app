import json 

import validators

import flask
from flask import redirect, abort, Blueprint, flash, url_for, request, jsonify
from api.models import User, Campaign, Donation, Message
from api.utils.validators import  validate_title, validate_user


views = Blueprint("views", __name__)


    # id = db.Column(db.Integer, primary_key=True)
    # title = db.Column(db.String(100), nullable=False)
    # description = db.Column(db.String(500), nullable=False)
    # goal = db.Column(db.Float, nullable=False)
    # duration = db.Column(db.Integer, nullable=False)
    # created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    # user_id = db.Column(db.Integer,db.ForeignKey('user.id'), nullable=False)
    # donations = db.relationship('Donation', backref='campaign', lazy=True)

    
#   TODO: create campaigns
#         POST / campaigns
@views.post("/campaigns/create")
def create_campaign():

    data = request.get_json()
   
    title = data.get("title")
    goal = data.get("goal")
    description = data.get("description")
    user_id = data.get("user_id")

    if not all([title, goal, description, user_id]):
        return jsonify({"message": "Missing required fields"}), 400
    
    try:
         # Validate data
        validate_user(user_id)

        validate_title(title, description)
    
        campaign = Campaign(**data)
        campaign.insert()

        return jsonify({"message": "Campaign created successfully"}), 201

    except ValueError as e:
        return jsonify({"message": str(e)}), 400
        campaign.rollback()

    
    return jsonify(
        {
            "Status": "success",
            "id": campaign.id,
            "title": campaign.title,
            "goal": campaign.goal,
            "description": campaign.description,
            "created_at": campaign.created_at

        })

   

    

# TODO: Get all campaign models
    #  GET /campaigns/

@views.get('/campaign')
def getCampaign():

    query = Campaign.query.all()

    return json.loads(query)
     

# TODO: Get all campaigns by  Id
# GET /<campaign_id>

@views.get('/campaign/<int:campaign_id>')
def get_campaign_id(campaign_id):

    campaign = Campaign.query.filter(Campaign.id == campaign_id).first()

    if campaign != None:
        return jsonify(
            {
                "Status": "success",
                "id": campaign.id,
                "title": campaign.title,
                "goal": campaign.goal,
                "description": campaign.description,
                "created_at": campaign.created_at

            })
    else:
        abort(400, description="user not found")


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

