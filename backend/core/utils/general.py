# application pagination class

from math import ceil
from flask import request, url_for, render_template, jsonify

def paginate(query, page=1, per_page=10):
    total = query.count()
    pages = int(ceil(total / float(per_page)))
    start = (page - 1) * per_page
    end = start + per_page
    prev_url = None
    next_url = None
    if page > 1:
        prev_url = url_for(request.endpoint, page=page-1)
    if page < pages:
        next_url = url_for(request.endpoint, page=page+1)
    return {
        'items': [item.serialize() for item in query.slice(start, end)],
        'prev_url': prev_url,
        'next_url': next_url,
        'total': total,
        'pages': pages,
        'page': page,
        'per_page': per_page
    }


# Response formatting function for content negotiation
def format_response(data, status_code=200, template_name=None):
    if request.is_json:
        return jsonify(data), status_code
    elif template_name:
        return render_template(template_name, data=data), status_code
    else:
        # Default template if no specific template is provided
        return render_template('default.html', data=data), status_code
    


def generate_validator(model, create=False):
    class Validator:
        def __init__(self):
            pass

        def validate(self, data):
            errors = {}

            # Get the list of fields from the model
            model_fields = getattr(model, 'get_fields', lambda: [])()

            # Check for required fields
            for field in model_fields:
                if field not in data:
                    errors[field] = f"Field '{field}' is required."

            # Additional validation logic can be added here

            return errors

    return Validator()


