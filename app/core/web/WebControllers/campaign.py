import json
import logging

from flask import (
    redirect,
    abort,
    Blueprint,
    flash,
    url_for,
    request,
    render_template,
    g,
    jsonify
)
from core.models import User, Campaign
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
from core.web.Forms.forms import CampaignForm

views = Blueprint("views", __name__)



@views.get("/campaigns/")
def listing():
    response_data = handle_get_request(Campaign, True)
    return render_template("front/listing.html", data=response_data)



@views.get("/campaigns/create")
def get_campaign_view():
     form = CampaignForm()
     return render_template(
        "user/create.html", form=form)


@views.post("/campaigns/create")
def create_campaign():
    if request.method == 'POST':
        try:
            data = request.form
            _clData = _clean_data(data)
            _clData['user_id'] = g.user_id
            response_data, status_code = handle_create_request(Campaign, _clData, is_json=False)
            if status_code == 201:
                return response_data
            else:
                # Handle other status codes
                flash("Error creating campaign", "error")
        except Exception as e:
            # Log the error for debugging
            # app.logger.error(f"Error creating campaign: {str(e)}")
            flash("Unable to create campaign", "error")
    else:
        return "Invalid request method", 405
    return render_template('user/create.html')    
   



@views.get("/campaigns/<int:id>/")
def get_campaign_by_id(id: int) -> dict:
    item = get_item_data(Campaign, id)
    return render_template("front/single_listing.html", data=item)


@views.delete("/campaigns/<int:id>/")
def delete_campaign_by_id(id: int):
    item = delete_item(Campaign, id)
    return redirect(url_for("views.retrieve_campaign"))


@views.patch("/campaigns/<int:id>/")
def update_campaign(id: int):
    data = request.get_json()
    item = handle_patch_request(data, id, Campaign)
    return redirect(url_for("views.listing"))


@views.post("/campaigns/<int:id>/status")
def toggle_status(id):
    status = request.form['status']
    item = _get_item(Campaign, id)
    if item:
        item.activate(status)
        logging.info(f"Campaign is now {status}")
    return redirect(url_for('get_campaign_by_id'))




@views.errorhandler(404)
def page_not_found():
    return render_template('error/404.html');

