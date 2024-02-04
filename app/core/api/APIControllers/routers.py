import json

import logging
from flask import redirect, abort, Blueprint, url_for, request, jsonify, current_app
from core.auth.jwt import jwt
from flask_login import login_required, current_user
from flask_jwt_extended import jwt_required, get_jwt_identity
from core.models import User, Campaign, Donation, Message
from core.utils.proj.tasks import activate_campaign
from core.utils.general import paginate
from core.utils.helpers import (
    handle_get_request,
    handle_create_request,
    handle_patch_request,
    _get_item,
    get_item_data,
    delete_item,
    _clean_data,
)


api = Blueprint("api", __name__)


# ////////////////////////////// Campaigns Routes ///////////////////////////////////////
@api.get("/campaigns/")
@jwt_required()
def retrieve_campaign():
    """Return all campaign in db

    Args: None

    rType: json(Dict)
    """
    print(current_user)
    response_data = handle_get_request(Campaign, False)
    return jsonify(response_data)
 

@api.post("/campaigns/create")
@login_required
@jwt_required()
def create_campaign():
    """Create a single unit of campaign in db

    Args: Send json payLoad

    rType: json(List[Dict])
    """
    json_data = request.get_json()
    _clData = _clean_data(json_data)
    _clData['user_id'] = get_jwt_identity()['id']
    response_data, status_code = handle_create_request(Campaign, _clData, is_json=True)
    return response_data, status_code


@api.get("/campaigns/<int:id>/")
@login_required
@jwt_required()
def get_campaign_by_id(id) -> dict:
    identity = get_jwt_identity()
    item = get_item_data(Campaign, id)
    if identity["id"] != item["user_id"]:
        item = {"msg": "You have not created any campaign yet"}
    return jsonify(item)


@api.patch("/campaigns/<int:id>/status")
@login_required
@jwt_required()
def toggle_campaign_status(id):
    status = request.get_json()["status"]
    item = _get_item(Campaign, id)
    if item:
        item.activate(status)
        current_app.logger.info(
            f" Campaign - '{item.serialize()['title']}' is {status}"
        )
    return jsonify(item.serialize())


@api.post("/campaigns/<int:id>/publish")
@login_required
@jwt_required()
def publish_campaign(id):
    status = request.get_json()["is_publish"]
    message = ""
    item = _get_item(Campaign, id)
    if item:
        current_status = item.publish(status)
        if current_status == True:
            message = "Campaign has been publish"
            current_app.logger.info(
                f"Campaign - {item.serialize()['title']} has been publish"
            )
        else:
            message = "Campaign is now unpublish"
            current_app.logger.info(
                f" Campaign - {item.serialize()['title']} has been unpublish"
            )

        obj = item.serialize()
        obj["message"] = message
    return jsonify(obj)


@api.patch("/campaigns/<int:id>/")
@login_required
@jwt_required()
def update_campaign(id: int) -> tuple:
    data = request.get_json()
    item = handle_patch_request(data, id, Campaign)
    return jsonify(item)


@api.delete("/campaigns/<int:id>/")
@login_required
@jwt_required()
def delete_campaign_by_id(id: int) -> tuple:
    item = delete_item(Campaign, id)
    current_app.logger.info(f" Campaign - {item.serialize()['title']} has been deleted")
    return jsonify(item)


# ////////////////////////////// Donations Routes ///////////////////////////////////////
@api.post("/campaigns/<int:id>/donation")
def make_donation(id):
    """ "Process Donation creation

    Args:
        argument -- campaign_id

    rType: successful | Error response
    """

    data = request.get_json()

    donated_amount = request.get_json()["amount"]
    # user_id = data.get('user_id')

    # Validate the donation amount
    if donated_amount <= 0.0:
        return jsonify({"error": "Invalid donation amount"}), 400

    try:
        # Check if campaign exists
        campaign = _get_item(Campaign, id)

        if campaign is None:
            return jsonify({"error": "Campaign not found"}), 404

        campaign_id = campaign.id

        # TODO: implement user_id here. For the donation, user_id shouldnt be campaign.user_id

        # Create a new donation record
        # clean_data = _clean_data(data)
        response_data, status_code = handle_create_request(Donation, data, is_json=True)
        if status_code != 201:
            return jsonify("Unable to add donation", "error")

        return jsonify({"message": "Donation successful"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@api.get("/campaigns/donation/<int:campaign_id>/")
def get_donations_from_campaign(campaign_id):
    """Fetch all donations to a campaign

    Args:
      id - campaign id

    rType: dict
    """
    campaign = _get_item(Campaign, campaign_id)

    if campaign:
        donations = campaign.donations
        if donations:
            donation_details = [
                {
                    "amount": donation.amount,
                    "donor": donation.user.name,
                    "time": donation.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                }
                for donation in donations
            ]
    return jsonify({"donations": donation_details})


@api.delete("/campaigns/donation/<int:id>/delete")
@login_required
@jwt_required()
def delete_donation(id):
    item = delete_item(Donation, id)
    return jsonify(item)


# /////////////////////////////////////// Users Route /////////////////////


