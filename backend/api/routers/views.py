import json

import validators

import flask
from flask import redirect, abort, Blueprint, flash, url_for, request, jsonify
from api.models import User, Campaign, Donation, Message
from api.utils.validators import validate_title, validate_user


views = Blueprint("views", __name__)


# Create campaign endpoint
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

        """
        Validate_title: validate title and description

        rtype: len()
        """
        validate_title(title, description)

        campaign = Campaign(**data)
        campaign.insert()

        return (
            jsonify(
                {
                    "message": "Campaign created successfully",
                    "id": campaign.id,
                    "title": campaign.title,
                    "goal": campaign.goal,
                    "description": campaign.description,
                    "created_at": campaign.created_at.strftime("%Y-%m-%d")
                    
                }
            ),
            201,
        )

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
            "created_at": campaign.created_at.strftime("%Y-%m-%d")
        }
    )


# Endpoint to get all campaign objects
@views.get("/campaigns")
def getCampaign():

    campaigns = Campaign.query.filter(Campaign.isActive == True).all()

    campaign_list = []

    for campaign in campaigns:

        campaign_donation = campaign.donations

        donations = []

        """
        Iteration to grab donation made
        
        """
        for donation in campaign.donations:
            donations.append(donation.amount)

        campaign_data = {
            "id": campaign.id,
            "title": campaign.title,
            "goal": campaign.goal,
            "amt_raised": sum(donations),
            "duration": campaign.duration,
            "description": campaign.description,
            "user_id": campaign.user_id,
            "created_at": campaign.created_at.strftime("%Y-%m-%d"),
            "isActive": campaign.isActive,
        }

        campaign_list.append(campaign_data)

    return campaign_list


# Endpoint to get campaign by id
@views.get("/campaigns/<int:campaign_id>")
def get_campaign_by_id(campaign_id):

    search = Campaign.query.filter(Campaign.id == campaign_id)
    campaign = search.first()

    if campaign != None:

        """
        Iteration to grab donation made

        """
        for donation in campaign.donations:
            donations = []
            donations.append(donation.amount)

        return jsonify(
            {
                "Status": "success",
                "id": campaign.id,
                "title": campaign.title,
                "goal": campaign.goal,
                "description": campaign.description,
                "amt_raised": sum(donations),
                "created_at": campaign.created_at.strftime("%Y-%m-%d"),
                "user_id": campaign.user_id,
                "isActive": campaign.isActive,
            }
        )
    else:
        abort(404, description="campaign not found")


# Endpoint to update campaign
@views.put("/campaigns/<int:campaign_id>/update")
def update_campaign(campaign_id):
    """update campaign
    
    Keyword arguments:
    argument -- campaign_id
    Return: campaign details
    """
    


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

        return (
            jsonify(
                {
                    "status": "success",
                    "title": campaign.title,
                    "goal": campaign.goal,
                    "description": campaign.description,
                }
            ),
            200,
        )

    except ValueError as e:
        campaign.rollback()
        return jsonify({"message": str(e)}), 400


#  Endpoint to delete campaign
@views.delete("/campaigns/<int:campaign_id>/delete")
def delete_campaign(campaign_id):
    """""delete campaign
    
    Keyword arguments:
    argument -- campaign_id
    Return: campaign_id, campaign_title
    """
    

    campaign = Campaign.query.filter(Campaign.id == campaign_id).first()

    if campaign == None:
        return jsonify({"message": "Campaign not found"}), 404

    # TODO: check user identity
    try:
        campaign.delete()
        return (
            jsonify({"status": "success", "message": "Campaign deleted successfully"}),
            200,
        )

    except:
        campaign.rollback()

    return jsonify({"id": campaign.id, "title": campaign.title})


# Endpoints to activate and deactivate campaigns

@views.get("/campaigns/<int:campaign_id>/activate")
def activate_campaign(campaign_id):
    """activate a campaign
    
    Keyword arguments:
    argument -- campaign
    Return: return campaign_title, campaign_status
    """
    
    query = Campaign.query.filter(Campaign.id == campaign_id)

    campaign = query.first()

    if campaign is None:
        return jsonify ({"Message": "Campaign not found"})
    
    else:
        campaign.isActive = True
        campaign.update()
        return jsonify({'message': 'Campaign is now active'}), 200
    
    return jsonify(
        {

         "Campaign": campaign.title,
         "isActive": campaign.isActive   
        }
    )

@views.get("/campaigns/<int:campaign_id>/deactivate")
def deactivate_campaign(campaign_id):
    """deactivate a campaign
    
    Keyword arguments:
    argument -- campaign
    Return: return campaign_title, campaign_status
    """
    
    query = Campaign.query.filter(Campaign.id == campaign_id)

    campaign = query.first()

    if campaign is None:
        return jsonify ({"Message": "Campaign not found"})
    
    else:
        campaign.isActive = False
        campaign.update()
        return jsonify({'message': 'Campaign is deactivated'}), 200
    
    return jsonify(
        {

         "Campaign": campaign.title,
         "isActive": campaign.isActive   
        }
    )
    


# ----------------Router for handling donation requests--------------

# Endpoint to make donation

@views.post("/campaigns/<int:campaign_id>/donate")
def make_donation(campaign_id):

    """"make donation request
    
    Keyword arguments:
    argument -- campaign_id
    Return: successful response
    """
    
    data = request.get_json()
    amount = data.get("amount")
    # user_id = data.get('user_id')

    # Validate the donation amount
    if amount <= 0:
        return jsonify({"error": "Invalid donation amount"}), 400
    try:
        # Check if campaign exists
        campaign = Campaign.query.filter_by(id=campaign_id).first()

       

        if campaign is None:
            return jsonify({"error": "Campaign not found"}), 404

        campaign_id = campaign.id

        # TODO: implement user_id here. For the donation, user_id shouldnt be campaign.user_id

        # Create a new donation record
        donation = Donation(
            amount=amount, user_id=campaign.user_id, campaign_id=campaign.id
        )

        donation.insert()

        # Return a successful response
        return jsonify({"message": "Donation successful"}), 201
    except:
        donation.rollback()
        donation.close()
        return jsonify({"message": "Can not make donation right now"}), 400


@views.get("donations/<int:campaign_id>/")
def get_donations_by_campaign(campaign_id):

    search = Campaign.query.filter(Campaign.id == campaign_id)
    campaign = search.first()

    if campaign is None:
        return jsonify({"message": "Campaign not found"})

    donate = Donation.query.filter(Donation.campaign_id == campaign.id).first()

    if donate is not None:
        campaign_donation = campaign.donations

        for donation in campaign.donations:

            donations = []

            user = User.query.filter(User.id == donation.user_id).first()

            """
            id 
            amount 
            created_at 
            user_id 
            campaign_id

            """
            if len(donations) == 0:
                donations = []

            donations.append(
                {
                    "id": donation.id or None,
                    "amount": donation.amount or None,
                    "Donor": user.name or None,
                    "time": donation.created_at.strftime("%Y-%m-%d"),
                }
            )

        return jsonify(
            {
                "campaign_id": campaign.id,
                "campaign_name": campaign.title,
                "description": campaign.description,
                "donations": donations,
            }
        )

    else:
        return jsonify({"message": "No donation for this campaign yet"})


# -------------------Routers for Users Dashboard-----------------
@views.get("/users")
def get_users():

    user_list = []
    users = User.query.all()

    for user in users:

        user_data = {}

        user_data["id"] = (user.id,)
        user_data["name"] = user.name
        user_data["email"] = (user.email,)
        user_data["bio"] = user.bio

        user_list.append(user_data)

    return user_list


@views.get("users/<int:user_id>")
def retrive_user_by_id(user_id):

    query = User.query.filter(User.id == user_id)

    user = query.first()

    if user is None:
        return jsonify({"message": "User not found"}), 404

    return (
        jsonify(
            {
                "status": "success",
                "user_id": user.id,
                "name": user.name,
                "user_email": user.email,
                "user_bio": user.bio,
            }
        ),
        200,
    )


@views.put("users/<int:user_id>/update")
def update_user_detail(user_id):

    user = User.query.filter(User.id == user_id).first()

    if not user:
        return jsonify({"message": "user not found"}), 404

    # TODO: check user identity

    data = request.get_json()

    name = data["name"]
    bio = data["bio"]

    try:
        user.name = name
        user.bio = bio

        user.update()

        return (
            jsonify(
                {
                    "status": "success",
                    "message": "user detail updated successfully",
                    "user_id": user.id,
                    "name": user.name,
                    "user_email": user.email,
                    "user_bio": user.bio,
                }
            ),
            200,
        )

    except:
        user.rollback()
        return jsonify({"message": "Can not update user details, please try again."})


@views.delete("users/<int:user_id>/delete")
def delete_user(user_id):

    user = User.query.filter(User.id == user_id).first()

    if not user:
        return jsonify({"message": "user not found"}), 404

    try:

        # TODO: check for user identity
        user.delete()

        return (
            jsonify(
                {
                    "status": "success",
                    "message": "user deleted successfully",
                }
            ),
            200,
        )

    except:
        user.rollback()
        return jsonify({"message": "Can not delete user, please try again."})
