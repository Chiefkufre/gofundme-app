from datetime import datetime
from flask import ( Blueprint, current_app, flash, 
                   jsonify, redirect, request, 
                   render_template, url_for
                   )
from core.utils.general import get_arrow_attributes
from core.src.Repository.repository import ( 
    _get_item, calculate_dashboard_donation_data, delete_item, fetch_user_notifications, 
    fetch_user_recent_donations, get_item_data, get_successful_campaigns, get_user_campaigns_by_status,
      handle_get_request, handle_patch_request
        )
from core.utils.constants.constants import Routes
from core.models import Campaign, Donation, Notification, User

from flask_login import current_user, login_required, login_user

from flask_jwt_extended import (
    jwt_required,
)

user = Blueprint("user", __name__)

@user.get('/dashboard')
@login_required
@jwt_required(locations=['cookies'])
def user_dashboard():
    
    user = current_user

    user_data = _get_item(User, user.id)
    dashboard_data = calculate_dashboard_donation_data(User, user.id)

    daily_totals = dashboard_data["daily_totals"]
    weekly_totals = dashboard_data["weekly_totals"]
    monthly_totals = dashboard_data["monthly_totals"]
    
    daily_percentage_changes = dashboard_data["daily_percentage_changes"]
    weekly_percentage_changes = dashboard_data["weekly_percentage_changes"]
    monthly_percentage_changes = dashboard_data["monthly_percentage_changes"]

    daily_averages = dashboard_data["daily_averages"]
    weekly_averages = dashboard_data["weekly_averages"]
    monthly_averages = dashboard_data["monthly_averages"]

    dailyArrowDirectionClass, dailyArrowIcon = get_arrow_attributes(dashboard_data["dailyChangeIsPositive"])
    weeklyArrowDirectionClass, weeklyArrowIcon = get_arrow_attributes(dashboard_data["weeklyChangeIsPositive"])
    monthlyArrowDirectionClass, monthlyArrowIcon = get_arrow_attributes(dashboard_data["monthlyChangeIsPositive"])

    notifications = fetch_user_notifications(Notification, user.id)

    donations_received = fetch_user_recent_donations(user_id=current_user.id, donation_type="received", per_page=4)
    donations_made = fetch_user_recent_donations(user_id=current_user.id, donation_type="made",per_page=4)

    active_campaign = get_user_campaigns_by_status(user.id, True, page=1, per_page=3)
    inactive_campaign = get_user_campaigns_by_status(user.id, False, page=1, per_page=3)
    paused_campaign = get_user_campaigns_by_status(user.id, page=1, per_page=3, pause=False)
    successful_campaigns = get_successful_campaigns(user.id, page=1, per_page=5)

    current_month_year = datetime.now().strftime("%B, %Y")
    return render_template('backend/user/index.html', 
                           user=user_data, notifications=notifications['data'], 
                            daily_totals=daily_totals, 
                            daily_percentage_changes=daily_percentage_changes,
                            daily_averages=daily_averages,
                            weekly_totals=weekly_totals, 
                            weekly_percentage_changes=weekly_percentage_changes, 
                            weekly_averages=weekly_averages,
                            monthly_totals=monthly_totals, 
                            monthly_percentage_changes=monthly_percentage_changes,
                            monthly_averages=monthly_averages,
                            dailyArrowDirectionClass= dailyArrowDirectionClass,
                            dailyArrowIcon=dailyArrowIcon,
                            weeklyArrowDirectionClass=weeklyArrowDirectionClass, 
                            weeklyArrowIcon=weeklyArrowIcon,
                            monthlyArrowDirectionClass=monthlyArrowDirectionClass,
                            monthlyArrowIcon=monthlyArrowIcon,
                             current_month_year= current_month_year,
                             donations_received=donations_received['donations'],
                             donations_made=donations_made['donations'],
                             active_campaign=active_campaign,
                             inactive_campaign=inactive_campaign,
                             successful_campaigns=successful_campaigns
                             )


@user.get('/dasboard/campaigns')
@login_required
def user_campaigns():
    user = current_user
    _data = handle_get_request(User, False, user.id)
    notifications = fetch_user_notifications(Notification, user.id)
    return render_template('backend/user/campaigns.html', user= user, data=_data["data"], 
                           total_campaigns = _data['total'],
                           pagination=_data["pagination"], notifications=notifications['data'])

@user.get('/dasboard/campaigns-list')
@login_required
def user_campaigns_list():
    user = current_user
    _data = handle_get_request(User, False, user.id)
    notifications = fetch_user_notifications(Notification, user.id)
    return render_template('backend/user/campaigns-list.html',user=user, data=_data["data"], 
                           total_campaigns = _data['total'],
                           pagination=_data["pagination"], notifications=notifications['data'])

@user.get('/dasboard/campaigns/create')
@login_required
def user_create_campaign():
    user = current_user
    notifications = fetch_user_notifications(Notification, user.id)
    return render_template('backend/user/create.html', user=user, notifications=notifications['data'])


@user.get('/dasboard/campaigns/<id>/edit')
@login_required
def user_edit_campaign(id):
    user = current_user
    data = get_item_data(Campaign, id)
    notifications = fetch_user_notifications(Notification, user.id)
    return render_template('backend/user/edit-campaign.html', campaign=data, user=user, notifications=notifications['data'])

@user.get('dashboard/donations/history')
@login_required
def user_donation_history():
    page = request.args.get("page", default=1, type=int)
    
    user = current_user
    notifications = fetch_user_notifications(Notification, user.id)
    donations_received = fetch_user_recent_donations(user_id=current_user.id, donation_type="received", per_page=5, page=page)
    donations_made = fetch_user_recent_donations(user_id=current_user.id, donation_type="made", per_page=5, page=page)
    
    total_donation = donations_received["total_donation"]
    return render_template('backend/user/donation-history.html', user=user, 
                           donations=donations_received['donations'], total_donation=total_donation, 
                           pagination=donations_received['pagination'], notifications=notifications['data'])


@user.get('/profile/<name>/<id>/<section>')
@login_required
def user_profile(name, id, section):
    user = _get_item(User, id)
    # notifications = fetch_user_notifications(Notification, user.id)
    return render_template(f'backend/user/profile/{section}.html', user=user,
                            # notifications=notifications['data']
                            )


@user.get('/dashboard/invoices')
@login_required
def user_invoices():
    user = current_user
    notifications = fetch_user_notifications(Notification, user.id)
    return render_template('backend/user/invoice-list.html',user=user, notifications=notifications['data'])

@user.get('/donation/invoice')
@login_required
def user_invoice():
    user = current_user
    notifications = fetch_user_notifications(Notification, user.id)
    return render_template('backend/user/invoice.html', user=user, notifications=notifications['data'])

@user.get('/dashboard/messages')
@login_required
def user_messages():
    user = current_user
    return render_template('backend/user/messages.html', user=user)




@user.post(Routes.CAMPAIGN_PUBLISH)
@login_required
@jwt_required()
def publish_campaign(id):
    req = request.form.get("is_publish")
    status = False
    if req == 'true':
        status = True
    message = ""
    try:
        item = _get_item(Campaign, id)
        if item:
            res = item.publish(status)
            if(res == True):
                message = "Campaign has been publish"
                current_app.logger.info(
                    f"Campaign - {item.serialize()['title']} has been publish"
                )
                flash(message)
            else:
                message = "Campaign has been unpublish"
                current_app.logger.info(
                    f"Campaign - {item.serialize()['title']} has been unpublish"
                )
                flash(message)
    except Exception as e:
        current_app.logger.info(
            f" fail to update campaign now-{e}"
        )
        flash(message)
    
    return redirect(url_for('user.user_campaigns_list'))


@user.post('/campaigns/<id>/delete')
@login_required
@jwt_required()
def delete_campaign_by_id(id):
    if request.form.get('_method') == 'DELETE':
        response = delete_item(Campaign, id)
        message = response
        flash(message)
    else:
        flash('method not allowed')
    return redirect(url_for('user.user_campaigns_list'))



@user.patch(Routes.EDIT_USER)
@login_required
@jwt_required()
def update_user_detail(id):
    data = request.get_json()
    user = _get_item(User, id)
    if user:
        response = handle_patch_request(data, id, User)
    return jsonify(response)


