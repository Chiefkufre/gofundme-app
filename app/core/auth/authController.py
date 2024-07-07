from flask import flash, make_response
from flask_mail import Message
import validators
from datetime import timedelta, timezone, datetime

from flask import (
    Blueprint,
    current_app,
    redirect,
    abort,
    Blueprint,
    flash,
    render_template,
    request,
    url_for,
    jsonify,
)
from flask_login import login_required, login_user, logout_user, current_user
from flask_jwt_extended import (
    create_access_token,
    set_access_cookies,
    jwt_required,
    get_jwt_identity,
    unset_jwt_cookies,
    unset_refresh_cookies,
    get_jwt,
)
from werkzeug.security import check_password_hash, generate_password_hash, gen_salt
from core.utils.ses_email_client import send_email
from core.utils.general import get_device_info, get_ip
from core.models import LoginActivity, User
from core.utils.validators import PlatformValidator
from core.utils.constants.constants import Routes
from core.utils.extentions import mail

auths = Blueprint("auths", __name__)

validators = PlatformValidator(User)

def send_mail():
    subject = "Test Email"
    body = "This is a test email from Flask using Amazon SES."
    to_addresses = ["testpractical2000@gmail.com"]
    from_address = "samuelkufrewillie@gmail.com"
    response = send_email(subject, body, to_addresses, from_address)
    if response:
        return "Email sent successfully!"
    else:
        return "Failed to send email."


@auths.get(Routes.REGISTER)
def registration_page():
    return render_template("frontend/front/register.html")


@auths.post(Routes.REGISTER)
def register_user():
    """Register new User

    :param  id: user id-auto-regenerated
    :param  name : new user name
    :type name: str
    :param email: new user email
    :type email: str
    :param password: new user password
    :type password: str
    :param bio: new user bio
    :type bio: str
    :raises HTTPException for different validation errors
    :return: new user detail
    :rtype: JSON object
    """

    # Validate if required data are passed
    email = request.form.get('email').rstrip()
    password = request.form.get('password').rstrip()
    name = request.form.get('name').rstrip()

    form_dict =  {
        "name": name,
        "email": email,
        "password": password,
        
    }

    try:
        validators.validate_json_request(form_dict)

        # Validate Email uniqueness
        request_email = form_dict["email"]

        validators.validate_email(request_email)
       
        # Regenerate hash password
        hashed_password = generate_password_hash(form_dict["password"])

        if "password" in form_dict and "email" in form_dict:
            del form_dict["password"]
            del form_dict["email"]

        # Add hash_password     
        form_dict["password"] = hashed_password
        form_dict["email"] = request_email.lower()
        # create user 
        new_user = User(**form_dict)

        # bind to db
        new_user.insert()
        flash("User account created successfully")
        return redirect(url_for('auths.get_login_page'))

    except ValueError as e:
        current_app.logger.critical("Fail to create User {0}".format(str(e)))
        flash("Fail to create User {0}".format(str(e)))
        return redirect(url_for('auths.registration_page'))
        


@auths.get(Routes.LOGIN)
def get_login_page():
    return render_template("frontend/front/login.html")


# function to handle posting to login route
@auths.post(Routes.LOGIN)
def sign_in_user():
    email = request.form.get('email').rstrip()
    password = request.form.get('password').rstrip()

    user = User.query.filter(User.email == email).first()

    if user and check_password_hash(user.password, password):

        # Login the user using Flask-Login
        login_user(user, remember=True, force=True)

        identity = {"id": user.id, "email": user.email}
        # Create and return the access token in the cookies
        access_token = create_access_token(identity=identity)

        response = make_response(redirect(url_for('user.user_dashboard')))
        set_access_cookies(response, access_token)

        response2 =send_email(subject="New Login", body="You have login successfully",
                    to_addresses=['testpractical2000@gmail.com'], from_address="samuelkufrewillie@gmail.com")
        print(response2)
        ip_address = get_ip()
        device_info = get_device_info()

        login_activity = LoginActivity(
            user_id=user.id,
            ip_address=ip_address,
            browser=device_info['browser'],
            browser_version=device_info['browser_version'],
            os=device_info['os'],
            os_version=device_info['os_version'],
            device=device_info['device'],
            is_mobile=device_info['is_mobile'],
            is_tablet=device_info['is_tablet'],
            is_pc=device_info['is_pc']
        )

        login_activity.insert()

        return response
    else:
        flash("incorrect email or password", "info")
        return render_template("frontend/front/login.html")


@auths.get('/reset-password')
def password_reset():
    return render_template('frontend/front/reset_password.html')

# Logout control center
@auths.get(Routes.LOGOUT)
@login_required
def logout():
    logout_user()
    response = jsonify({"msg": "logout successful"})
    unset_jwt_cookies(response)
    flash("Logout successful")
    return redirect(url_for('web.home'))


@auths.route("/refresh_token", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return jsonify(msg="token refresh", access_token=access_token)


# Refresh access token every 30 minutes
@auths.after_request
def refresh_expiring_jwts(response):
    try:
        exp_timestamp = get_jwt()["exp"]
        now = datetime.now(timezone.utc)
        target_timestamp = datetime.timestamp(now + timedelta(minutes=30))
        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity())
            set_access_cookies(response, access_token)
        return response
    except (RuntimeError, KeyError):
        return response
