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
def format_response(response_data, status_code=200, template_name=None):
    if request.is_json:
        return jsonify(response_data), status_code
    else:
        return render_template(template_name + '.html', data=response_data), status_code
   
    


def generate_validator(model, create=False):
    class Validator:
        def __init__(self):
            self.model_fields = getattr(model, 'get_fields', lambda: [])()


        def validate_json_request(self, data):
            errors = {}

            # Check for required fields
            for field in self.model_fields:
                if field not in data:
                    errors[field] = f"Field '{field}' is required."

            # Additional validation logic can be added here

            return errors
        
        
        def validate_form_request(self, form_data):
            errors = {}

            # Check for required form fields
            for field in self.model_fields:
                if field not in form_data:
                    errors[field] = f"Field '{field}' is required in the form."

            return errors

    return Validator()


