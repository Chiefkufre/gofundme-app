import json

import validators

import flask
from flask import redirect, abort, Blueprint, flash, url_for, request, jsonify
from core.models import Campaign


search = Blueprint("search", __name__)




@search.get("/search/<q>")
def search_app(q):
    data = request.args.get("q")

    # print(data)

    # query = data.replace(" ", "").lower()

    campaigns = Campaign.query.filter(or_(Campaign.title.ilike("%" + query + "%"), Campaign.description.ilike("%" + query + "%"))).all()

    results = []
    for campaign in campaigns:
        results.append({
            "id": campaign.id,
            "title": campaign.title,
            "description": campaign.description,
            "goal": campaign.goal,
            "duration": campaign.duration
        })
    return {"results": results}