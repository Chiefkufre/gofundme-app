# application pagination class

from functools import wraps
from flask import request, jsonify


# to impliment, decorate required endpiont with the pagniate function
def paginate(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 2))
        start = (page - 1) * per_page
        end = start + per_page

        # Call the original function with pagination arguments
        result = fn(start=start, end=end, *args, **kwargs)

        # Construct the response object with pagination metadata
        response = {
            'data': result[start:end],
            'page': page,
            'per_page': per_page,
            'total': len(result),
            'total_pages': int(len(result) / per_page) + (1 if len(result) % per_page > 0 else 0)
        }

        return jsonify(response)

    return wrapper
