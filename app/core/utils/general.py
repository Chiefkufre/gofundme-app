# application pagination class

from math import ceil
from flask import request, url_for, render_template, jsonify


def paginate(query, page=1, per_page=10):
    total = query.count()
    pages = int(ceil(total / float(per_page)))
    start = (page - 1) * per_page
    end = start + per_page
    items = [item.serialize() for item in query.slice(start, end)]

    prev_url = None
    next_url = None
    if page > 1:
        prev_url = url_for(request.endpoint, page=page - 1)
    if page < pages:
        next_url = url_for(request.endpoint, page=page + 1)

    return {
        "items": items,
        "pagination": {
            "total": total,
            "pages": pages,
            "page": page,
            "per_page": per_page,
            "prev_url": prev_url,
            "next_url": next_url,
        },
    }

def calculate_percentage(expected_donation:float, donated_amt:float)->float:
    """function to calcualte the current donation percentage
    
    Args:
        expected_donation->float: The amount expected.
        donated_ant->float: The amount donated so far.

    Returns: percentage_donation (percenatge | float)
        
     
    """
    donation_in_percentage = (donated_amt / expected_donation ) * 100
    return donation_in_percentage
