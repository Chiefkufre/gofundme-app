import json

import validators

import flask
from flask import redirect, abort, Blueprint, flash, url_for, request, jsonify, render_template
from flask.views import MethodView
from core.models import User, Campaign, Donation, Message
from core.utils.general import paginate
from core.utils.helpers import handle_get_request, handle_create_request, handle_patch_request, get_item_data, delete_item


views = Blueprint("views", __name__)

@views.get("/campaigns/")
def retrieve_campaign():
    response_data = handle_get_request(Campaign, True)
    return response_data


@views.post("/campaigns/create")
def create_campaign():
    json_data = request.get_json()
    response_data, status_code = handle_create_request(Campaign, json_data, is_json=True)
    return response_data, status_code

@views.get('/campaigns/<int:id>/')
def get_campaign_by_id(id:int) -> dict:
    item = get_item_data(Campaign, id)
    return jsonify(item) 

@views.delete('/campaigns/<int:id>/')
def delete_campaign_by_id(id:int) -> tuple:
    item = delete_item(Campaign, id)
    return item

@views.patch('/campaigns/<int:id>/')
def update_campaign(id:int) -> tuple:
    data = request.get_json()
    item = handle_patch_request(data, id, Campaign)
    return item





# Define your routes and template names
routes = [
    {"url": "/campaigns/create", "template": "create.html", "methods": [ "POST",]},
    {"url": "/campaigns/", "template": "front/listing.html", "methods": ["GET"]},
    {"url": "/campaigns/<int:id>", "template": "front/single_listing.html", "methods": ["GET", "PATCH", "DELETE"]},

    {"url": "/users/", "template": "user/dashboard.html", "methods": ["GET"]},
    {"url": "/users/<int:id>", "template": "profile.html", "methods": ["GET", "DELETE", "PATCH"]},
]


@views.post("/campaigns/<int:campaign_id>")
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





   

"""Update"""
# "/campaigns/<int:campaign_id>/update" - campaign
# "users/<int:user_id>/update" - user
#  "/campaigns/<int:campaign_id>/activate" - activate campaign

"""Get"""
# users/<int:user_id>" -user

# DELETE
# "/campaigns/<int:campaign_id>/delete"
# "users/<int:user_id>/delete"

# GROUP API
#  /campaigns/ - get
# "/users"