from flask import jsonify, request, current_app
from flask_mail import Message

from core.utils.general import paginate
from core.utils.validators import PlatformValidator
from core.utils.general import paginate


def validate_item_data(model, data, is_json, is_create):
    """Validates item data for both JSON and form requests, including all fields."""

    validator = PlatformValidator(model, is_create=is_create)
    errors = (
        validator.validate_json_request(data)
        if is_json
        else validator.validate_form_request(data)
    )

    if "title" in data and "description" in data:
        validation_error = validator.validate_title(data["title"], data["description"])
        if validation_error:
            errors.update({"title_and_description": validation_error})

    return errors


def _get_item(model, id):
    """Retrieves an item by ID from the specified model.

    Args:
        model: The model class to query.
        id: The ID of the item to retrieve.

    Returns:
        The retrieved item, or raises a 404 error if not found.
    """

    return model.query.get_or_404(id)


def get_item_data(model, id) -> dict:
    """Retrieves item data based on id, including total donations if applicable.

    Args:
        model: The model to retrieve data from.
        id: The specific item identity.

    Returns:
        A dictionary containing the specified item and their fields,
        including total_donations if the model has a donations field.
    """

    item = _get_item(model, id)
    fields = model.get_fields()

    if "donations" in fields:
        donation_details = [
            {
                "amount": donation.amount,
                "name": donation.user.name or None,
                "time": donation.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            }
            for donation in item.donations
        ]
        total_donations = sum(
            donation.amount for donation in item.donations
        )  # Calculate total donations
        data = {
            "donations": donation_details,
            "total_donations": total_donations,
            **{
                field: getattr(item, field) for field in fields if field != "donations"
            },  # Exclude 'donations'
        }
    else:
        data = {field: getattr(item, field) for field in fields}

    return data


def handle_get_request(model, status) -> dict:
    """Retrieves items based on state

    Args:
        model: The model to retrieve data from.
        state: state specific if is_active is (True | False)

    Returns:
        A dictionary containing the specified item and their fields.
    """
    # Retrieve the page and per_page values from the request arguments
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=10, type=int)

    # Paginate the query
    pagination_data = paginate(
        model.query.filter_by(is_active=status), page=page, per_page=per_page
    )
    email = Message(
        "Hello", sender="yourId@gmail.com", recipients=["testpractical2000@gmail.com"]
    )
    email.body = "This is the email body"
    success = current_app.extensions["mail"].send(email)

    return {
        "data": pagination_data["items"],
        "pagination": pagination_data["pagination"],
    }


def handle_create_request(model, data, is_json) -> dict:
    response_data = {}

    # Validate item data
    errors = validate_item_data(model, data, is_json, is_create=True)
    if errors:
        # Return error response
        status_code = 400  # Bad Request
        response_data["message"] = errors
        current_app.logger.critical("Error on create - {0}".format(errors))
        return response_data, status_code
    try:
        item = model(**data)
        item.insert()
        response_data["message"] = f"{model.__name__} created successfully"
        response_data["item"] = item.serialize()
        status_code = 201  # Created
    except Exception as e:
        # Handle specific exceptions or log the error
        response_data["message"] = f"Failed to create {model.__name__}. {str(e)}"
        status_code = 500  # Internal Server Error
        current_app.logger.critical("Error on create | Exception - {0}".format(e))
    return response_data, status_code


def handle_patch_request(data, id, model, is_json=True):
    """Handles a PATCH request to update an item.

    Args:
        item: The item to update.
        request: The Flask request object.
        model: The model class for the item.

    Returns:
        A formatted response based on the request type (JSON or HTML).
    """
    # retrive item based on data
    item = _get_item(model, id)

    response_data = {}
    status_code = 500

    try:
        errors = validate_item_data(model, data, is_json, is_create=False)
        if errors:
            status_code = 400  # Bad Request
            response_data["message"] = errors
            current_app.logger.critical("Error on patch | - {0}".format(errors))
            return response_data, status_code

        item.update_from_request(data)
        status_code = 204
        response_data["message"] = f"Successfully updated campaign."
        response_data["item"] = item.serialize()
    except Exception as e:
        item.rollback()
        success = False
        current_app.logger.critical("Error on patch | Exception - {0}".format(e))
        response_data["message"] = f"Failed to update campaign details. {str(e)}"
    return response_data, status_code


def delete_item(model, id):
    """Deletes an item and handles potential errors gracefully.

    Args:
        mode;: The model where the item reside.
        id: id of the item to be deleted.

    Returns:
        A dictionary and status code when successful.
    """
    item = _get_item(model, id)

    response_data = {}
    response_data["item"] = item.serialize()
    status_code = 500

    try:
        item.delete()
        response_data["message"] = f"{model.__name__} deleted successfully"
        response_data["item"] = item.serialize()
        status_code = 204

    except Exception as e:
        item.rollback()
        response_data[
            "message"
        ] = f"Failed to delete {model.__name__}. Please try again."
        status_code = 204
        current_app.logger.info("Error on delete | Exception - {0}".format(e))
    return response_data, status_code


def _clean_data(data: dict) -> dict:
    """ "Clean requested data before passing submit

    Args:
        data: request data information

    returns:
        cleaned data in python dictionary
    """
    clean_data = {}
    for key, item in data.items():
        clean_data[key] = item.strip().lower()
        pass

    return clean_data
