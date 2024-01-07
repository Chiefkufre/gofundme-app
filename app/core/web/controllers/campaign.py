import json

import validators

import flask
from flask import redirect, abort, Blueprint, flash, url_for, request, jsonify, render_template
from flask.views import MethodView
from core.models import User, Campaign, Donation, Message
from core.utils.general import paginate, format_response, generate_validator
from core.utils.validators import validate_title, validate_user, validate_title_on_update


views = Blueprint("views", __name__)

# Content negotiation logic
# @campaigns.before_request
# def content_negotiation():
#     # Set request.is_json based on the content type in the Accept header
#     request.is_json = request.accept_mimetypes.best_match(['application/json', 'text/html']) == 'application/json'

#     # Check if the request's content type is JSON or form-urlencoded
#     if not request.is_json:
#         request.is_json = request.content_type == 'application/x-www-form-urlencoded'




class ItemAPI(MethodView):
    init_every_request = False

    def __init__(self, model):
        self.model = model
        self.validator = generate_validator(model)
        self.template_name = None  # Initialize to None

    def dispatch_request(self, *args, **kwargs):
        self.template_name = kwargs.get('template_name', None)
        return super().dispatch_request(*args, **kwargs)

    def update_item(self, item, data):
        success = False
        message = "";
        try:
            item.update_from_request(data)
            item.update()
            success = True
            message = f"Successfully updated campaign."
        except Exception as e:
            item.rollback()
            # TODO: Add logging logic here
            success = False
            message = f"Failed to update campaign details. {str(e)}"
        return success, message
        
    def delete_item(self, item, response_data):
        """Deletes an item and handles potential errors gracefully.

        Args:
            item: The item to be deleted.
            response_data: A dictionary to store response information.

        Returns:
            A tuple containing the modified response data and HTTP status code.
        """

        try:
            item.delete()
            response_data["message"] = "Campaign deleted successfully"
            return response_data, 204

        except Exception as e:
            item.rollback()
            # logger.error(f"Failed to delete campaign. {e}")  # Log the error
            response_data["message"] = "Failed to delete campaign. Please try again."
            return response_data, 500



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
        
        print("test=", self.template_name)
        return format_response(response_data, template_name=self.template_name)

    def patch(self, id):
        """Updates an item with the given ID.

        Args:
            id: The ID of the item to update.

        Returns:
            A formatted response based on the request type (JSON or HTML).
        """

        # TODO: Validate user identity

        item = self._get_item(id)
        response_data = {}
        status_code = 500  # Default status for unexpected errors
        template_name = None

        if request.is_json:
            try:
                errors = self.validator.validate_json_request(request.json)
                if errors:
                    return jsonify(errors), 400

                validate_title_on_update(request.json['title'], request.json['description'])  # Validate directly
                success, message = self.update_item(item, request.json)
                response_data["message"] = message
                response_data["item"] = item.serialize()
                status_code = 200

            except ValueError as e:
                response_data["message"] = str(e)  # Capture validation error messages
                status_code = 400

        else:  # Handling form request (similar structure as JSON case)
            try:

                errors = self.validator.validate_form_request(request.form)
                if errors:
                    response_data['message'] = f"Failed to update {self.model.__name__}. {str(errors)}"
                    status_code = 400
                    if "title" in request.form and "description" in request.form:
                        validate_title_on_update(request.form['title'], request.form['description'])
                    success, message = self.update_item(item, request.form)
                    template_name = self.template_name
                    response_data['message'] = message
                    response_data["item"] = item.serialize()
            except ValueError as e:
                response_data["message"] = str(e)  # Capture validation error messages
                status_code = 400
        response_data['s']
        return format_response(response_data, status_code, template_name=template_name) 
    

    def delete(self, id):
        """Handles deletion of an item with the given ID.

        Args:
            id: The ID of the item to delete.

        Returns:
            A formatted response based on the request type (JSON or HTML).
        """

        item = self._get_item(id)
        response_data = {}

        if request.is_json:
            template_name = None
        else:
            template_name = self.template_name

        if item:
            response_data, status_code = self.delete_item(item, response_data)

            # Only include serialized item in response if deletion was successful
            if status_code == 204:
                response_data['item'] = item.serialize()

        return format_response(response_data, status_code, template_name)



class GroupAPI(MethodView):
    init_every_request = False

    def __init__(self, model, template_name=None):
        self.model = model
        self.validator = generate_validator(model, create=True)
        self.template_name = None  # Initialize to None

    
    def dispatch_request(self, *args, **kwargs):
        self.template_name = kwargs.get('template_name', None)
        return super().dispatch_request(*args, **kwargs)
    
    def create_item(self, data, is_json):
        response_data = {}

        # Validate JSON or form request
        errors = self.validator.validate_json_request(data) if is_json else self.validator.validate_form_request(data)

        if errors:
            # Include form validation errors in the message
            error_message = f"Failed to create {self.model.__name__}. Please check the form for errors:\n"
            error_message += "\n".join(errors.values())
            response_data['message'] = error_message
            status_code = 400  # Bad Request
        else:
            # No form errors, proceed with creating the item
            if "title" in data and "description" in data:
                validation_error = validate_title_on_update(data['title'], data['description'])
                if validation_error:
                    response_data["message"] = validation_error
                    status_code = 400

            try:
                item = self.model(**data)
                item.insert()
                response_data['message'] = f"{self.model.__name__} created successfully"
                response_data["item"] = data
                status_code = 201  # Created
            except Exception as e:
                # Handle specific exceptions or log the error
                response_data['message'] = f"Failed to create {self.model.__name__}. {str(e)}"
                status_code = 500  # Internal Server Error
            print(self.template_name)
        # return response_data, status_code
        return format_response(response_data, status_code=status_code, template_name=self.template_name)
    

    
    def get(self):
        # Retrieve the page and per_page values from the request arguments
        page = request.args.get('page', default=1, type=int)
        per_page = request.args.get('per_page', default=10, type=int)

        # Paginate the query
        pagination_data = paginate(
                                self.model.query.filter_by(is_active=True),
                                page=page, 
                                per_page=per_page
                                )

        # Construct a response data dictionary
        response_data = {
            'items': pagination_data['items'],
            'pagination': {
                'page': pagination_data['page'],
                'per_page': pagination_data['per_page'],
                'total_pages': pagination_data['pages'],
                'total_items': pagination_data['total'],
                'prev_url': pagination_data['prev_url'],
                'next_url': pagination_data['next_url'],
            }
        }

        # Use the format_response function to handle content negotiation
        return format_response(response_data, template_name=self.template_name)

  

    def post(self):
        if request.is_json:
            response_data, status_code = self.create_item(request.json, is_json=True)
        else:
            response_data, status_code = self.create_item(request.form, is_json=False)
        print(self.template_name)
        return format_response(response_data, status_code=status_code, template_name=self.template_name)




# Define your routes and template names
routes = [
    {"url": "/campaigns/create", "template": "create.html", "methods": [ "POST",]},
    {"url": "/campaigns/", "template": "front/listing.html", "methods": ["GET"]},
    {"url": "/campaigns/<int:id>", "template": "front/single_listing.html", "methods": ["GET", "PATCH", "DELETE"]},

    {"url": "/users/", "template": "user/dashboard.html", "methods": ["GET"]},
    {"url": "/users/<int:id>", "template": "profile.html", "methods": ["GET", "DELETE", "PATCH"]},
]



# Register API routes
def register_api(app, model, name, routes):
    group = GroupAPI.as_view(f"{name}-group", model=model)
    item = ItemAPI.as_view(f"{name}-item", model=model)

    for route in routes:
        if "id" in route["url"]:
            app.add_url_rule(route["url"], view_func=item, methods=route["methods"])
        else:
            app.add_url_rule(route["url"], view_func=group, methods=route["methods"])

# Example usage (assuming `app` is the Flask app instance)
register_api(views, Campaign, "campaigns", routes[0:3])  # Register routes for campaigns
register_api(views, User, "users", routes[3:])  # Register routes for users

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