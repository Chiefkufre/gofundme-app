import json

import validators

import flask
from flask import redirect, abort, Blueprint, flash, url_for, request, jsonify
from api.models import Campaign


search = Blueprint("search", __name__)




@search.post("/search/<str:q>")
def search_app(q):

    data = request.args_json()


