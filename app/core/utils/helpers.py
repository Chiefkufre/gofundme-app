from flask import jsonify, request
from core.utils.general import paginate
from core.utils.validators import PlatformValidator
from core.utils.general import paginate 


def validate_item_data(model, data, is_json, is_create):
    """Validates item data for both JSON and form requests, including all fields."""

    validator = PlatformValidator(model, is_create=is_create)
    errors = validator.validate_json_request(data) if is_json else validator.validate_form_request(data)

    if "title" in data and "description" in data:
            validation_error = validator.validate_title(data['title'], data['description'])
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
    """Retrieves item data based on id

    Args:
        model: The model to retrieve data from.
        id: the specific item identity.

    Returns:
        A dictionary containing the specified item and their fields.
    """
    # Grab the item. This will alway return an item or not
    item = _get_item(model, id)

    # Retrieve item fields dynamically
    fields = model.get_fields()

    if 'donations' in fields:
        total_donations = sum(getattr(item, 'donations', []))
        return {'total_donations': total_donations}
    else:
        return {field: getattr(item, field) for field in fields}


def get(model, state) -> dict:

    """Retrieves items based on state

    Args:
        model: The model to retrieve data from.
        state: state specific if is_active is (True | False)

    Returns:
        A dictionary containing the specified item and their fields.
    """
    # Retrieve the page and per_page values from the request arguments
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=10, type=int)

    # Paginate the query
    pagination_data = paginate(
                            model.query.filter_by(is_active=state),
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

    return response_data


def handle_create_request(model, data, is_json) -> dict:
    response_data = {}

    # Validate item data
    errors = validate_item_data(model, data, is_json, is_create=True)
    if errors:
        # Return error response
        status_code = 400  # Bad Request
        response_data['message'] = errors
        return response_data, status_code
    try:
        item = model(**data)
        item.insert()
        response_data['message'] = f"{model.__name__} created successfully"
        response_data["item"] = item.serialize()
        status_code = 201  # Created
    except Exception as e:
        # Handle specific exceptions or log the error
        response_data['message'] = f"Failed to create {model.__name__}. {str(e)}"
        status_code = 500  # Internal Server Error
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
        with model.atomic():
            
            errors = validate_item_data(model, data, is_json, is_create=False)
            if errors:
                status_code = 400  # Bad Request
                response_data['message'] = errors
                return response_data, status_code
            
        item.update_from_request(**data)
        status_code = 204
        response_data["message"] = f"Successfully updated campaign."
        response_data['item'] = item.serialize()
    except Exception as e:
        item.rollback()
        # TODO: Add logging logic here
        success = False
        response_data["message"] = f"Failed to update campaign details. {str(e)}"

    return response_data, status_code
 


def delete_item(id, model):
    """Deletes an item and handles potential errors gracefully.

    Args:
        item: The item to be deleted.
        response_data: A dictionary to store response information.

    Returns:
        A tuple containing the modified response data and HTTP status code.
    """
    item  = _get_item(id, model)

    response_data = {}
    status_code = 500

    try:
        item.delete()
        response_data["message"] = "Campaign deleted successfully"
        response_data["item"] = item.serialize()
        status_code = 204

    except Exception as e:
        item.rollback()
        response_data["message"] = "Failed to delete campaign. Please try again."
        status_code = 204
    
    return response_data, status_code