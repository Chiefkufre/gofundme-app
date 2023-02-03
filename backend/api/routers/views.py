import json 

import validators

import flask
from flask import redirect, abort, Blueprint, flash, url_for, request, jsonify
from api.models import User, Campaign, Donation, Message
from api.utils.validators import  validate_title, validate_user


views = Blueprint("views", __name__)


@views.post("/campaigns/create")
def create_campaign():

    data = request.get_json()
   
    title = data.get("title")
    goal = data.get("goal")
    description = data.get("description")
    duration = data.get("duration")
    user_id = data.get("user_id")

    

    if not all([title, goal, description, user_id]):
        return jsonify({"message": "Missing required fields"}), 400
    
    try:
         # Validate data
        validate_user(user_id)
      
        validate_title(title, description)
    
        campaign = Campaign(**data)
        campaign.insert()

        return jsonify({
            "message": "Campaign created successfully",
            "id": campaign.id,
            "title": campaign.title,
            "goal": campaign.goal,
            "description": campaign.description,
            "created_at": campaign.created_at
        
        }), 201

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

   

@views.get('/campaigns')
def getCampaign():

    campaigns = Campaign.query.all()

    campaign_list = []

    for campaign in campaigns:
        campaign_data = {

            "id": campaign.id,
            "title": campaign.title,
            "goal": campaign.goal,
            "duration": campaign.duration,
            "description": campaign.description,
            "user_id": campaign.user_id,
            "created_at": campaign.created_at
        }

        campaign_list.append(campaign_data)
    
    return campaign_list



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
                # "donations":type(campaign.donations),
                "created_at": campaign.created_at,
                "user_id": campaign.user_id

            })
    else:
        abort(404, description="campaign not found")


@views.put("/campaigns/<int:campaign_id>/update")
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

    if not goal:
        return jsonify({"message": "goal are required"}), 400

    try:
        validate_title(title, description)

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
        campaign.rollback()
        return jsonify({"message": str(e)}), 400
        



@views.delete("/campaigns/<int:campaign_id>/delete")
def delete_campaign(campaign_id):

    campaign =  Campaign.query.filter(Campaign.id == campaign_id).first()

    if campaign == None:
        return jsonify({
            "message": "Campaign not found"
        }), 404
    
    # TODO: check user identity
    try:
        campaign.delete()
        return jsonify({
            "status": "success",
            "message": "Campaign deleted successfully"

        }), 200
    
    except:
        campaign.rollback()
    
    return jsonify({

        "id": campaign.id,
        "title": campaign.title
    })





# ----------------ROuter for handling donation requests--------------

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

        print("campaign", campaign)


        if campaign is None:
            return jsonify({'error': 'Campaign not found'}), 404
        

        query  = Donation.query.filter_by(id=campaign.id).first()

        print(query)

        campaign_id = campaign.id

        print("campaign_id", campaign_id)
        # Create a new donation record
        donation = Donation(amount=amount, user_id=campaign.user_id, campaign_id=campaign.id)

        print(type(donation))

        donation.insert()

        

        # Return a successful response
        return jsonify({'message': 'Donation successful'}), 201
    except:
        pass
    #     # donation.rollback()
    #     # donation.close()
    #     return jsonify({'message': 'Can not make donation right now'}), 400
    
    



#  TODO: get campaigns
#         GET /donations/<campaign_id>
#         


# -------------------Routers for Users Dashboard-----------------
@views.get('/users')
def get_users():

    user_list = []
    users = User.query.all()

    for user in users:

        user_data = {}

        user_data["id"] = user.id,
        user_data["name"] = user.name
        user_data["email"]= user.email,
        user_data["bio"]= user.bio

        user_list.append(user_data)
    
    return user_list



@views.get("users/<int:user_id>")
def retrive_user_by_id(user_id):
    
    query = User.query.filter(User.id == user_id)

    user = query.first()

    if user is None:
        return  jsonify(
            {
                "message": "User not found"
            }
        ), 404
    

    return jsonify({
        "status": "success",
        "user_id": user.id,
        "name": user.name,
        "user_email": user.email,
        "user_bio": user.bio
    }), 200


@views.put('users/<int:user_id>/update')
def update_user(user_id):
    

    user = User.query.filter(User.id == user_id).first()

    if not user:
        return jsonify({
            "message": "user not found"
        }), 404
    
    # TODO: check user identity

    data = request.get_json()

    name = data["name"]
    bio = data["bio"]

    try:
        user.name = name
        user.bio = bio

        user.update()

        return jsonify({

            "status": "success",
            "message": "user detail updated successfully",
            "user_id": user.id,
            "name": user.name,
            "user_email": user.email,
            "user_bio": user.bio
    }), 200
    
    except:
        user.rollback()
        return jsonify({
            "message": "Can not update user details, please try again."
        })
    

@views.delete('users/<int:user_id>/delete')
def delete_user(user_id):
    
    user = User.query.filter(User.id == user_id).first()

    if not user:
        return jsonify({
            "message": "user not found"
        }), 404

    try:
        
        # TODO: check for user identity
        user.delete()

        return jsonify({

            "status": "success",
            "message": "user deleted successfully",
    }), 200
    
    except:
        user.rollback()
        return jsonify({
            "message": "Can not delete user, please try again."
        })