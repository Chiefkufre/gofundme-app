import json
import logging
import os
import uuid
from flask import redirect, abort, Blueprint, send_from_directory, url_for, request, jsonify, current_app, render_template, flash
from werkzeug.utils import secure_filename
from core.auth.jwt import jwt
from flask_login import login_required, current_user
from flask_jwt_extended import jwt_required, get_jwt_identity
from core.models import Notification, User, Campaign, Donation, Message
from core.utils.proj.tasks import activate_campaign
from core.utils.general import allowed_file, calculate_time_interval, paginate
from core.utils.constants.constants import Routes
from core.src.Repository.repository import (
    fetch_user_notifications,
    handle_get_request,
    handle_create_request,
    handle_patch_request,
    _get_item,
    get_item_data,
    delete_item,
    _clean_data,
)


web = Blueprint("web", __name__)

@web.get("")
def home():
    return render_template("frontend/front/home.html")

@web.get(Routes.COMPAIGNS_ALL)
def retrieve_campaign():
    """Return all campaign in db

    Args: None

    rType: json(Dict)
    """
    response_data = handle_get_request(Campaign, False)
    return render_template('frontend/front/listing.html', campaigns=response_data)


@web.post(Routes.CAMPAIGN_CREATE)
@login_required
@jwt_required(locations='cookies')
def create_campaign():
    """Create a single unit of campaign in db

    Args: Send json payLoad

    rType: json(List[Dict])
    """ 

    form_data_dict = dict(request.form)

    image_url = ""
    
    if "is_publish" in form_data_dict:
        del form_data_dict['is_publish']
    

    form_data_dict['is_publish'] = True


    time_remaining = calculate_time_interval(form_data_dict['duration'])

    if 'file' not in request.files:
        flash('Please add image')
        return redirect(url_for('user.user_create_campaign'))
    
    file = request.files['file']


    if file.filename.lower() == '':
        flash('No selected file')
        return redirect(url_for('user.user_create_campaign'))
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename.lower())
        image_url = f"{uuid.uuid4().hex}_{filename}"
        file.save(os.path.join(current_app.config['CAMPAIGN_FOLDER'], image_url))
    
    campaign_data = {
        "title": form_data_dict['title'].strip(),
        'description': form_data_dict['description'].strip(),
        'type': form_data_dict['type'].strip(),
        'goal': form_data_dict['goal'].strip(),
        'duration': time_remaining,
        'is_publish': form_data_dict['is_publish'],
        'image_url': image_url,
    }

    campaign_data["user_id"] = get_jwt_identity()["id"]
    response_data, status_code = handle_create_request(Campaign, campaign_data, is_json=True)
    if status_code == 201:
        notification_data = {
            "user_id": campaign_data["user_id"],
            "activity_id": response_data["item"]['id'],
            "type": "Campaign",
            "message": f"New Campaign created successfully"
        }

        new_notification = Notification(**notification_data)
        new_notification.insert()
    message = response_data['message']
    flash(message)
    return redirect(url_for('user.user_create_campaign'))


@web.get(Routes.CAMPAIGN_BY_ID)
@login_required
def get_campaign_by_id(id) -> dict:
    item = get_item_data(Campaign, id)
    # if identity["id"] != item["user_id"]:
    #     item = {"msg": "You have not created any campaign yet"}

    donations = {}

    if len(item['donations']) > 0:
        recent_donation = 0
        donation_size = len(item['donations'])
        if donation_size > 1:
            recent_donation = len(item['donations']) - 1
        else:
            recent_donation = 0
        donations = {
            "numberOfDonation": len(item['donations']),
            "recentDonorName": item['donations'][recent_donation]['name'],
            "recentDonorAmount": item['donations'][recent_donation]['amount'],
        }
    else:
        donations = donations
    creator = _get_item(User, item['user_id'])
    return render_template('frontend/front/single_listing.html', 
                           item=item, creator=creator, 
                           donations=donations)





@web.post(Routes.CAMPAIGN_UPDATE)
@login_required
@jwt_required()
def update_campaign(id):
    if request.form.get('_method') == 'PATCH':
    
        
        data_dict = dict(request.form)

        image_url = ""
        

        original_time = request.form.get('originalTime')

        form_time = request.form.get('duration')

        time_remaining = ""

        file = request.files['file']
        try:

            if(original_time != form_time):
                time_remaining = calculate_time_interval(form_time)
            else:
                time_remaining = form_time

            if not file:
                image_url =  data_dict['image_url']
                del data_dict['image_url'] 
            
            if file and allowed_file(file.filename):

                image_path = os.path.join(current_app.config['CAMPAIGN_FOLDER'], request.form.get('image_url'))
                if os.path.exists(image_path):
                    os.remove(image_path)
                del data_dict['image_url']


                filename = secure_filename(file.filename.lower())
                image_url = f"{uuid.uuid4().hex}_{filename}"
                file.save(os.path.join(current_app.config['CAMPAIGN_FOLDER'], image_url))
            
            _clData = {
                "title": data_dict['title'],
                "description": data_dict['description'],
                "duration": time_remaining,
                'goal': data_dict['goal'],
                'type': data_dict['type'],
                'image_url': image_url
            }
            _new_item = _clean_data(_clData)
            handle_patch_request(_new_item, id, Campaign)
            flash("campaign updated successfully")
        except Exception as e:
            flash("unable to update file now. Please try again later")
        return redirect(url_for('user.user_campaigns_list'))
    else:
        flash('method not allowed')


# ////////////////////////////// Donations Routes ///////////////////////////////////////
@web.post(Routes.CAMPAIGN_DONATION)
def make_donation(id):
    """ "Process Donation creation

    Args:
        argument -- campaign_id

    rType: successful | Error response
    For donations, user_id is the id of the donor. It allows us to track the doner. It could be donor

    """
    data = request.get_json()

    donated_amount = request.get_json()["amount"]

    # Validate the donation amount
    if donated_amount <= 0.0:
        return jsonify({"error": "Invalid donation amount"}), 400

    try:
        # Check if campaign exists
        campaign = _get_item(Campaign, id)

        if campaign is None:
            return jsonify({"error": "Campaign not found"}), 404

 
        data['recipient_id'] = campaign.user_id #this allows us to tag the campaign owner identity of each donations

        response_data, status_code = handle_create_request(Donation, data, is_json=True)
        if status_code == 201:
            notification_data = {
                "user_id": campaign.user_id,
                "activity_id": response_data["item"]['campaign_id'],
                "type": "Donation",
                "message": f"You have recieved a new donation"
            }

            new_notification = Notification(**notification_data)
            new_notification.insert()
        
        return jsonify({"message": "Donation successful"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@web.get(Routes.CAMPAIGN_DONATION_FETCH)
# @login_required
# @jwt_required()
def get_donations_from_campaign(campaign_id):
    """Fetch all donations to a campaign

    Args:
      id - campaign id

    rType: dict
    """
    campaign = _get_item(Campaign, campaign_id)

    if campaign:
        donations = campaign.donations
        if donations:
            donation_details = [
                {
                    "amount": donation.amount,
                    "donor": donation.user.name,
                    "time": donation.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                }
                for donation in donations
            ]
    return jsonify({"donations": donation_details})


@web.delete(Routes.CAMPAIGN_DONATION_DELETE)
@login_required
@jwt_required()
def delete_donation(id):
    item = delete_item(Donation, id)
    return jsonify(item)


@web.delete('notification/<id>/delete')
def delete_notification(id):
    user = current_user
    notification = delete_item(Notification, id)
    current_app.logger.info(f"Notification {id} deleted successfully.")
    
    # fetch_user_notifications(Notification, user.id)
    return jsonify({"success": True, "message": "Notification deleted"}), 200
    
@web.get(Routes.DOC)
def doc():
    return render_template("web/doc.html")


@web.get(Routes.ABOUT)
def about():
    return render_template("frontend/front/about.html")


@web.get(Routes.CONTACT)
def contact():
    return render_template("frontend/front/contact.html")


@web.post(Routes.CONTACT)
def message():
    form_data = request.form
    form_data_dict = dict(form_data)
    _clData = _clean_data(form_data_dict)
    # new_message = Message(**_clData)
    # new_message.insert()
    response =  handle_create_request(Message, _clData, is_json=True)
    flash(response['message'])
    return redirect(url_for("web.contact"))


@web.route('/download/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(current_app.config['CAMPAIGN_FOLDER'], filename, as_attachment=True)

# @web.errorhandler()
# def page_not_found(error):
#         return 'This page does not exist', 404
