import json

import validators

import flask
from flask import redirect, abort, Blueprint, flash, url_for, request, jsonify, render_template
from flask.views import MethodView
from core.models import User, Campaign, Donation, Message
from core.utils.general import paginate, format_response, generate_validator
from core.utils.validators import validate_title, validate_user, validate_title_on_update


campaigns = Blueprint("campaigns", __name__)

# Content negotiation logic
@campaigns.before_request
def content_negotiation():
    if request.accept_mimetypes.best_match(['application/json', 'text/html']) == 'application/json':
        request.is_json = True
    else:
        request.is_json = False


class ItemAPI(MethodView):
    init_every_request = False

    def __init__(self, model, template_name):
        self.model = model
        self.validator = generate_validator(model)
        self.template_name = template_name

    def update_item(self, item, data):
        try:
            item.update_from_request(data)
            item.update()
            return True, f"Successfully updated {item} details"
        except Exception as e:
            item.rollback()
            # TODO: Add logging logic here
            return False, f"Failed to update {item} details. {str(e)}"


    def _get_item(self, id):
        return self.model.query.get_or_404(id)

    def get(self, id):
        item = self._get_item(id)

        # Retrieve fields dynamically
        fields = self.model.get_fields()

        if 'donations' in fields:
            total_donations = sum(getattr(item, 'donations', []))
            response_data = {'total_donations': total_donations}
        
        else:
            # If 'donations' field is not present, return all fields
            response_data = {field: getattr(item, field) for field in fields}
        
        
        return format_response(response_data, template_name=self.template_name)

    def patch(self, id):
        # TODO: Validate user identity user_id = get_jwt_identity()

        item = self._get_item(id)

        response_data = {}


        if request.is_json:
            # Handle JSON request
            errors = self.validator.validate_json_request(self, request.json)

            if errors:
                return jsonify(errors), 400

            if "title" in request.json and "description" in request.json:
                validate_title_on_update(request.json['title'], request.json['description'])
            success, message = self.update_item(item, request.json)
            template_name = None
        
        else:
            # Handle form request
            errors = self.validator.validate_form(self, request.form)

            if errors:
                return jsonify(errors), 400

            if "title" in request.form and "description" in request.form:
                validate_title_on_update(request.form['title'], request.form['description'])

            success, message = self.update_item(item, request.json)
            template_name = self.template_name
            
        response_data['message'] = message
        return format_response(response_data, status_code=500, template_name=template_name) if not success else format_response(response_data, template_name=template_name)
    

# Create campaign endpoint
@campaigns.post("/campaigns/create")
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

        response_data = {
            "message": "Campaign created successfully",
            "id": campaign.id,
            "title": campaign.title,
            "goal": campaign.goal,
            "description": campaign.description,
            "created_at": campaign.created_at.strftime("%Y-%m-%d")
        }

        if request.accept_mimetypes.best_match(['application/json', 'text/html']) == 'application/json':
            return jsonify(response_data), 201
        else:
            return render_template('user/campaigns.html', data=response_data), 201

    except ValueError as e:
        return jsonify({"message": str(e)}), 400

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
@campaigns.get("/campaigns")
def get_campaign():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 1, type=int)

    campaigns = Campaign.query.filter(Campaign.isActive == True).all()

    campaign_list = []

    for campaign in campaigns:
        donations = [donation.amount for donation in campaign.donations]
        total_amount_raised = sum(donations)

        campaign_data = {
            "id": campaign.id,
            "title": campaign.title,
            "goal": campaign.goal,
            "amt_raised": total_amount_raised,
            "duration": campaign.duration,
            "description": campaign.description,
            "user_id": campaign.user_id,
            "created_at": campaign.created_at.strftime("%Y-%m-%d"),
            "isActive": campaign.isActive,
        }

        campaign_list.append(campaign_data)

    response_data = {"campaigns": campaign_list}

    if request.accept_mimetypes.best_match(['application/json', 'text/html']) == 'application/json':
        return jsonify(response_data)
    else:
        return render_template("front/listing.html", data=response_data)





#  Endpoint to delete campaign
@campaigns.delete("/campaigns/<int:campaign_id>/delete")
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




# ----------------Router for handling donation requests--------------

# Endpoint to make donation

@campaigns.post("/campaigns/<int:campaign_id>/donate")
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


@campaigns.get("donations/<int:campaign_id>/")
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
@campaigns.get("/users")
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


   

@campaigns.delete("users/<int:user_id>/delete")
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


"""Update"""
# "/campaigns/<int:campaign_id>/update" - campaign
# "users/<int:user_id>/update" - user
#  "/campaigns/<int:campaign_id>/activate" - activate campaign

"""Get"""
# users/<int:user_id>" -user