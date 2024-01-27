import json

import validators

import flask
from flask import (
    redirect,
    abort,
    Blueprint,
    flash,
    url_for,
    request,
    jsonify,
    render_template,
)
from core.models import User, Donation, Campaign
from core.utils.general import paginate
from core.utils.helpers import (
    handle_get_request,
    handle_create_request,
    handle_patch_request,
    get_item_data,
    delete_item,
    _clean_data,
)

don = Blueprint("don", __name__)


@don.post("/campaigns/<int:campaign_id>/donation")
def make_donation(campaign_id):
    """ "make donation request

    Keyword arguments:
    argument -- campaign_id
    Return: successful response
    """

    data = request.form()
    donated_amount = request.form("amount")
    # user_id = data.get('user_id')

    # Validate the donation amount
    if donated_amount <= 0.0:
        return jsonify({"error": "Invalid donation amount"}), 400
    try:
        # Check if campaign exists
        campaign = Campaign.query.filter_by(id=campaign_id).first()

        if campaign is None:
            return flash({"error": "Campaign not found"}), 404

        campaign_id = campaign.id

        # TODO: implement user_id here. For the donation, user_id shouldnt be campaign.user_id

        # Create a new donation record
        clean_data = _clean_data(data)
        response_data, status_code = handle_create_request(
            Donation, clean_data, is_json=False
        )
        if status_code != 201:
            return flash("Unable to add donation", "error")
        # Return a successful response
        return jsonify({"message": "Donation successful"}), 201
    except:
        return jsonify({"message": "Can not make donation right now"}), 400


@don.get("donations/<int:campaign_id>/")
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
