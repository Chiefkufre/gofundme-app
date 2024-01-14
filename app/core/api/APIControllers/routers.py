import json

import validators

from flask import redirect, abort, Blueprint, flash, url_for, request, jsonify, render_template
from flask.views import MethodView
from core.models import User, Campaign, Donation, Message
from core.utils.general import paginate
from core.utils.helpers import handle_get_request, handle_create_request, handle_patch_request, get_item_data, delete_item, _clean_data


api = Blueprint("api", __name__)

@api.get("/campaigns/")
def retrieve_campaign():
    response_data = handle_get_request(Campaign, True)
    return response_data


@api.post("/campaigns/create")
def create_campaign():
    json_data = request.get_json()
    _clData = _clean_data(json_data)
    response_data, status_code = handle_create_request(Campaign, _clData, is_json=True)
    return response_data, status_code

@api.get('/campaigns/<int:id>/')
def get_campaign_by_id(id:int) -> dict:
    item = get_item_data(Campaign, id)
    return jsonify(item) 

@api.delete('/campaigns/<int:id>/')
def delete_campaign_by_id(id:int) -> tuple:
    item = delete_item(Campaign, id)
    return jsonify(item)

@api.patch('/campaigns/<int:id>/')
def update_campaign(id:int) -> tuple:
    data = request.get_json()
    item = handle_patch_request(data, id, Campaign)
    return jsonify(item)






   