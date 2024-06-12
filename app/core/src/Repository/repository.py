import os
from flask import flash, jsonify, request, current_app
from flask_login import current_user
from flask_mail import Message
from sqlalchemy import desc, asc, and_

from core.models import Campaign, Donation, Notification, User
from core.utils.general import calculate_average, calculate_percentage_changes, paginate, process_date_type, round_up_one_decimal_place
from core.utils.validators import PlatformValidator
from core.utils.general import paginate
from datetime import datetime, timedelta

def validate_item_data(model, data, is_json, is_create):
    """Validates item data for both JSON and form requests, including all fields."""

    validator = PlatformValidator(model, is_create=is_create)
   
    try:
       validator.validate_json_request(data) if is_json else validator.validate_form_request(data)

       if "title" in data and "description" in data:
          validator.validate_title(data["title"], data["description"])
       else:
           pass
    except ValueError as e:
        flash(str(e))
        


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
    """Retrieves item data based on id, including total donations if applicable.

    Args:
        model: The model to retrieve data from.
        id: The specific item identity.

    Returns:
        A dictionary containing the specified item and their fields,
        including total_donations if the model has a donations field.
    """

    item = _get_item(model, id)
    fields = model.get_fields()
    data = {}
    try:
        if "donations" in fields and "duration" in fields:
            donation_details = [
                {
                    "amount": donation.amount,
                    "name": _get_item(User, donation.donor_id).name if donation.donor_id  else "Anonymous",
                    # "name": donation.user.name if donation.user and donation.user.name else "Anonymous",
                    "time": donation.created_at.strftime("%Y-%m-%d %H:%M:%S"), 
                }
                for donation in item.donations
            ]
            total_donations = sum(
                donation.amount for donation in item.donations
            )  # Calculate total donations

            goal = float(getattr(item, fields[2]))
            percentage = round_up_one_decimal_place((float(total_donations) / goal) * 100)
            data = {
                "donations": donation_details,
                "total_donations": total_donations,
                "percentage" : percentage,
                **{
                    field: getattr(item, field) for field in fields if field != "donations"
                },  # Exclude 'donations'
            }
        else:
            data = {field: getattr(item, field) for field in fields}
    except Exception as e:
        # Handle specific exceptions or log the error
        data["message"] = f"Failed to get {model.__name__}. {str(e)}"
        status_code = 500  # Internal Server Error
        current_app.logger.critical("Error on read | Exception - {0}".format(data["message"]))
    return data


def handle_get_request(model, status=None, id=None) -> dict:
    """Retrieves items based on state

    Args:
        model: The model to retrieve data from.
        state: state specific if is_active is (True | False)

    Returns:
        A dictionary containing the specified item and their fields.
    """

    
    # Retrieve the page and per_page values from the request arguments
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=10, type=int)


    if id:
        query = model.query.filter(and_(model.id == id, model.is_active == status)).order_by(model.created_at.desc())

    else:
        query = model.query.filter_by(is_active=status).order_by(model.created_at.desc())


    pagination_data = paginate(
        query, page=page, per_page=per_page
    )

    fields = model.get_fields()
    
    if "campaigns" in fields:
        items_with_user_data = []
        for item in pagination_data["items"]:

            user = {
                'name': item['name'],
                'profile_picture': item['profile_picture'],
                'email': item['email'],
            }

            campaigns = item['campaigns']
            
            for campaign in campaigns:
                donations= [{
                            "amount": donation['amount'],
                            "id": donation['id'],
                            "campaign_id": donation['campaign_id'],
                            "donor_id": donation['donor_id'] if donation['donor_id'] else 'Anonymous',
                            "time": donation['created_at'],
                            "transaction_ref": donation['transaction_ref'],
                        } for donation in campaign['donations']]
                
                
                if len(donations) != 0:
                    amount_left =  0
                    total_amount_donated = sum(amt['amount'] for amt in donations)
                    percentage = round_up_one_decimal_place((total_amount_donated / float(campaign['goal'])) * 100)

                    if(total_amount_donated > float(campaign['goal'])):
                        amount_left = 0.0
                    elif(total_amount_donated < 1):
                        amount_left = float(campaign['goal'])
                    else:
                        amount_left = float(campaign['goal']) - total_amount_donated
                else:
                    amount_left = float(campaign['goal'])
                    percentage = 0  
                
                
                item_data = {
                    "id" : campaign['id'],
                    "title": campaign['title'],
                    'goal': campaign['goal'],
                    "type": campaign['type'],
                    "duration": campaign['duration'],
                    "description": campaign['description'],
                    "image_url": campaign['image_url'],
                    'percentage':percentage,
                    "is_active": campaign['is_active'],
                    "is_publish": campaign['is_publish'],
                    'total_donation': len(donations),
                    "donations": donations,
                    "notifications": item["notifications"],
                    'amount_left': amount_left,
                    "user": user
                }
                items_with_user_data.append(item_data)
        
            result_data = items_with_user_data
    else:
        result_data = pagination_data["items"]
    return {
        "total": len(result_data),
        "data": result_data,
        "pagination": pagination_data["pagination"],
    }



def handle_create_request(model, data, is_json) -> dict:
    response_data = {}

    try:
        validate_item_data(model, data, is_json, is_create=True)
        item = model(**data)
        item.insert()

        response_data["message"] = f"{model.__name__} created successfully"
        current_app.logger.info(response_data["message"])
        response_data["item"] = item.serialize()
        status_code = 201 
    except Exception as e:
        response_data["message"] = f"Failed to create {model.__name__}. {str(e)}"
        status_code = 500  
        current_app.logger.critical("Error on create | Exception - {0}".format(response_data["message"]))
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
        validate_item_data(model, data, is_json, is_create=False)

        item.update_from_request(data)
        status_code = 204
        response_data["message"] = f"Successfully updated campaign."
        current_app.logger.info("Successfully updated campaign.")
        response_data["item"] = item.serialize()
    except Exception as e:
        success = False
        current_app.logger.critical("Error on patch | Exception - {0}".format(e))
        response_data["message"] = f"Failed to update campaign details. {str(e)}"
    return response_data


def delete_item(model, id):
    """Deletes an item and handles potential errors gracefully.

    Args:
        mode;: The model where the item reside.
        id: id of the item to be deleted.

    Returns:
        A dictionary and status code when successful.
    """
    item = _get_item(model, id)

    fields = model.get_fields()

    response_data = {}

    try:
        if "image_url" in fields:
            image_path = os.path.join(current_app.config['CAMPAIGN_FOLDER'], item.serialize()['image_url'])
            if os.path.exists(image_path):
                os.remove(image_path)
        
        if "profile_picture" in fields:
            image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], item.serialize()['profile_picture'])
            if os.path.exists(image_path):
                os.remove(image_path)

        item.delete()
        response_data["message"] = f"{model.__name__} deleted successfully"
        flash(response_data["message"])
        current_app.logger.warning(f"{model.__name__} deleted successfully")
    except Exception as e:
        # item.rollback()
        response_data[
            "message"
        ] = f"{e}. Please try again. "
        flash(response_data["message"])
        current_app.logger.critical("Error on delete | Exception - {0}".format(e))
    return response_data["message"]


def _clean_data(data: dict) -> dict:
    """Clean requested data before passing submit

    Args:
        data: request data information

    Returns:
        Cleaned data in a Python dictionary
    """
    clean_data = {}
    for key, item in data.items():
        if isinstance(item, str):
            clean_data[key] = item.strip()
        else:
            clean_data[key] = item

    return clean_data

def fetch_user_notifications(model, user_id):

    # page = request.args.get("page", default=1, type=int)
    # per_page = request.args.get("per_page", default=10, type=int)

    query = model.query.filter_by(user_id = user_id).order_by(model.created_at.desc())

    
    pagination_data = paginate(
        query, page=1, per_page=5
    )

    # fields = model.get_fields()
    notifications = []
    notification_data = pagination_data['items']

    for notification in notification_data:
        db_date = notification['created_at']


        time, date, month, formated_month, actual_time =  process_date_type(db_date)
    
        data = {
            "id": notification["id"],
            "user_id": notification['user_id'],
            "message": notification['message'],
            "type": notification['type'],
            "read": notification['read'],
            "activity_id": notification['activity_id'],
            "date": actual_time,
            "month": month,
            "formated_month": formated_month,
        }
        notifications.append(data)
    data = notifications
    return {
        "data": data,
        "pagination": pagination_data['pagination']
    }



def calculate_dashboard_donation_data(model, user_id):

    user = model.query.filter_by(id=user_id).first()

    all_user_campaigns = user.campaigns

    donation_data = []

    for campaign in all_user_campaigns:

        for donation in campaign.donations:
            donation= {
                        "amount": donation.amount,
                        "date": donation.created_at.strftime("%Y-%m-%d"),
                    }
            donation_data.append(donation)
    
    
    start_date=None
    end_date=None
        
    daily_totals = {}
    daily_counts = {}
    weekly_totals = {}
    weekly_counts = {}
    monthly_totals = {}
    monthly_counts = {}

    current_week_start = None

    for item in donation_data:
        transaction_date = datetime.strptime(item['date'], '%Y-%m-%d')
        amount = item['amount']


        # Check if within specified date range (if provided)
        if start_date and transaction_date < start_date:
            continue
        if end_date and transaction_date > end_date:
            continue
        
        
        # Update monthly total
        month_key = transaction_date.strftime('%Y-%m')
        monthly_totals.setdefault(month_key, 0)
        monthly_totals[month_key] += amount
        monthly_counts.setdefault(month_key, 0)
        monthly_counts[month_key] += 1

        # Update daily totals
        date_str = transaction_date.strftime('%Y-%m-%d')
        daily_totals.setdefault(date_str, 0)
        daily_totals[date_str] += amount
        daily_counts.setdefault(date_str, 0)
        daily_counts[date_str] += 1

        # Update weekly totals
        week_start = transaction_date - timedelta(days=transaction_date.weekday())
        if week_start != current_week_start:
            current_week_start = week_start
            weekly_totals[week_start.strftime('%Y-%m-%d')] = 0
            weekly_counts[week_start.strftime('%Y-%m-%d')] = 0
        weekly_totals[week_start.strftime('%Y-%m-%d')] += amount
        weekly_counts[week_start.strftime('%Y-%m-%d')] += 1

    # Ensure default value for the current day
    current_day_key = datetime.now().strftime('%Y-%m-%d')
    if current_day_key not in daily_totals:
        daily_totals[current_day_key] = 0
        daily_counts[current_day_key] = 0

    # Ensure default value for the current week
    current_week_key = (datetime.now() - timedelta(days=datetime.now().weekday())).strftime('%Y-%m-%d')
    if current_week_key not in weekly_totals:
        weekly_totals[current_week_key] = 0
        weekly_counts[current_week_key] = 0

    # Ensure default value for the current month
    current_month_key = datetime.now().strftime('%Y-%m')
    if current_month_key not in monthly_totals:
        monthly_totals[current_month_key] = 0
        monthly_counts[current_month_key] = 0
    
    daily_percentage_changes = calculate_percentage_changes(daily_totals)
    weekly_percentage_changes = calculate_percentage_changes(weekly_totals)
    monthly_percentage_changes = calculate_percentage_changes(monthly_totals)

    
    daily_averages = calculate_average(daily_totals, daily_counts)
    weekly_averages = calculate_average(weekly_totals, weekly_counts)
    monthly_averages = calculate_average(monthly_totals, monthly_counts)
    

    def get_totals_for_comparison(totals):
        sorted_keys = sorted(totals.keys())
        if len(sorted_keys) < 2:
            return None, None
        recent_key = sorted_keys[-1]
        preceding_key = sorted_keys[-2]
        return totals[recent_key], totals[preceding_key]
    
    recent_daily_total, preceding_daily_total = get_totals_for_comparison(daily_totals)
    recent_weekly_total, preceding_weekly_total = get_totals_for_comparison(weekly_totals)
    recent_monthly_total, preceding_monthly_total = get_totals_for_comparison(monthly_totals)

    def is_change_positive(current, previous):
        if previous is None:
            return True  
        return current > previous

    dailyChangeIsPositive = is_change_positive(recent_daily_total, preceding_daily_total)
    weeklyChangeIsPositive = is_change_positive(recent_weekly_total, preceding_weekly_total)
    monthlyChangeIsPositive = is_change_positive(recent_monthly_total, preceding_monthly_total)

    return {
        "daily_totals": daily_totals,
        "weekly_totals": weekly_totals,
        "monthly_totals": monthly_totals,
        "daily_percentage_changes": daily_percentage_changes,
        "weekly_percentage_changes": weekly_percentage_changes,
        "monthly_percentage_changes": monthly_percentage_changes,
        "daily_averages": daily_averages,
        "weekly_averages": weekly_averages,
        "monthly_averages": monthly_averages,
        "dailyChangeIsPositive": dailyChangeIsPositive,
        "weeklyChangeIsPositive": weeklyChangeIsPositive,
        "monthlyChangeIsPositive": monthlyChangeIsPositive
    }


def fetch_user_recent_donations(user_id, donation_type, per_page, page=None):
    """Fetch recent donations either made by or received by the user.

    Args:
        user_id (int): The user ID.
        donation_type (str): "received" for donations received, "made" for donations made.
        page (int, optional): Page number for pagination. Defaults to 1.
        per_page (int, optional): Items per page for pagination. Defaults to 4.

    Returns:
        list: List of donation data dictionaries.
    """
    
    filter_key = Donation.recipient_id if donation_type == "received" else Donation.donor_id
    
    if page is None:
        page = 1
    
    query = Donation.query.filter(filter_key == user_id).order_by(Donation.created_at.desc())

    pagination_data = paginate(query, page=page, per_page=per_page)

    donations = []
    donation_data = pagination_data['items']
    pagination = pagination_data['pagination']

    donation_count = query.count()
    for donation in donation_data:
        # donation_count += 1
        donation_date = donation['created_at']
        time, date, month, formated_month, actual_time =  process_date_type(donation_date)
        donations.append(
            {
                "amount": donation['amount'],
                "name": _get_item(User, donation['donor_id']).name if donation['donor_id'] else "Anonymous",
                "campaign_title": _get_item(Campaign, donation['campaign_id']).title,
                "campaign_id": donation['campaign_id'],
                "ref_id": donation['transaction_ref'],
                "time": actual_time
            }
        )
    
    return {"donations" : donations,
            "total_donation": donation_count,
            "pagination": pagination
            }

def get_user_campaigns_by_status(user_id, status=True, page=None, per_page=None, pause=True):
     
    if pause == False:
        query = Campaign.query.filter(Campaign.user_id == user_id, 
                                Campaign.is_publish == False).order_by(
                                    Campaign.created_at.desc())
    else:
        query = Campaign.query.filter(Campaign.user_id == user_id, 
                                Campaign.is_active == status).order_by(
                                    Campaign.created_at.desc())

    pagination_data = paginate(query, page=page, per_page=per_page)

    campaigns = []
    campaign_data = pagination_data['items']
    pagination = pagination_data['pagination']
    campaign_size = query.count()
    for campaign in campaign_data:
        campaign_date = campaign['created_at']
        time, date, month, formated_month, actual_time =  process_date_type(campaign_date)
        campaigns.append({
            "id": campaign['id'],
            "title": campaign['title'],
            "is_publish": campaign['is_publish'],
            "image_url": campaign['image_url'],
            "time": date,
        })

    return {"campaigns" : campaigns,
        "total": campaign_size,
        "pagination": pagination
        }


def get_successful_campaigns(user_id, page=None, per_page=None):
    query = Campaign.query.filter_by(user_id = user_id).order_by(Campaign.created_at)

    pagination_data = paginate(query, page=page, per_page=per_page)

    successful_campaigns = []

    campaign_data = pagination_data['items']

    pagination = pagination_data['pagination']

    campaign_size = query.count()

    for campaign in campaign_data:
        donations= [{
                    "amount": donation['amount'],
                } for donation in campaign['donations']]
        
        total_amount_donated = sum(amt['amount'] for amt in donations)

        if(total_amount_donated >= float(campaign['goal'])):
            successful_campaigns.append({
            "id": campaign['id'],
            "title": campaign['title'],
            "is_publish": campaign['is_publish'],
            "image_url": campaign['image_url'],
            "raise": total_amount_donated,
            "status": "Successful🎈🎈🎈"
        })
    
    total_campaign = len(successful_campaigns)

    return {
        "campaigns": successful_campaigns,
        "total": total_campaign,
        "pagination": pagination
    }