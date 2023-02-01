import json 

import validators

import flask
from flask import redirect, abort, Blueprint, flash, url_for, request, jsonify
from api.models import User, Campaign, Donation, Message
from api.utils.validators import  validate_title, validate_user


views = Blueprint("views", __name__)
    
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

@views.get('/campaigns')
def getCampaign():

    query = Campaign.query.all()

    return jsonify(query)

# TODO: Get all campaigns by  Id
# GET /<campaign_id>

@views.get('/campaigns/<int:campaign_id>')
def get_campaign_by_id(campaign_id):

    search = Campaign.query.filter(Campaign.id == campaign_id)
    campaign = search.first()

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


#  TODO: update campaigns based on id
@views.put("/api/campaigns/<int:campaign_id>")
# @jwt_required
def update_campaign(campaign_id):
    # Get the campaign from the database
    campaign = Campaign.query.get(campaign_id)
    if not campaign:
        return jsonify({"message": "Campaign not found"}), 404

    # Validate the user is the owner of the campaign
    # user_id = get_jwt_identity()
    # if user_id != campaign.user_id:
    #     return jsonify({"message": "You are not authorized to perform this action"}), 403

    # Get the updated data from the request
    data = request.get_json()

    title = data.get("title")
    goal = data.get("goal")
    description = data.get("description")

    try:
        if not goal:
            return jsonify({"message": "goal are required"}), 400
        
        validated = validate_title(title, description)

        if validated:

            # update
            
            campaign.title = title
            campaign.goal = goal
            campaign.description = description

            # commit to db
            campaign.update()

            return jsonify({
                "status": "success",
                "title":  campaign.title,
                "goal": campaign.goal,
                "description": campaign.description
            }), 200

    except ValueError as e:
        return jsonify({"message": str(e)}), 400
        campaign.rollback()
    


# TODO: delete capaigns based on id
#  DELETE /<campaign_id>



# ----------------ROuter for handling donation requests--------------

#   TODO: make donation
#  /donations//<campaign_id>

@views.post('/campaigns/<int:campaign_id>/donate')
def make_donation(campaign_id):
    data = request.get_json()
    amount = data.get('amount')
    # user_id = data.get('user_id')


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

