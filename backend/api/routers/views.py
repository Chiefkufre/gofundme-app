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

#   TODO: make donation
#  /donations//<campaign_id>
from sqlalchemy.orm import exc

@views.post('/api/campaigns/<int:campaign_id>/donate')
def make_donation(campaign_id):
    data = request.get_json()
    amount = data.get('amount')

    # Validate the donation amount
    if amount <= 0:
        return jsonify({'error': 'Invalid donation amount'}), 400

    try:
           # Check if campaign exists
        campaign = Campaign.query.filter_by(id=campaign_id).first()

        if campaign is None:
            return jsonify({'error': 'Campaign not found'}), 404
        else:
            # Create a new donation record
            donation = Donation(amount=amount, campaign_id=campaign_id)
            donation.insert(donation)

            # update the total raised for the campaign
            donation.increase_amount(amount)

            # Return a successful response
            return jsonify({'message': 'Donation successful'}), 201
    except:
        
        donation.rollback()
        donation.close()
        return jsonify({'message': 'Can not make donation right now'}), 400
    
    



#  TODO: get campaigns
#         GET /donations/<campaign_id>
#         


# -------------------Routers for Users Dashboard-----------------

# TODO: Get all users
# GET users/users/

# TODO: get users by id
# GET users/<user_id>


# TODO: update users by id
# PUT users/<user_id>

# TODO: delete users by id
#   DELETE users/<user_id>

