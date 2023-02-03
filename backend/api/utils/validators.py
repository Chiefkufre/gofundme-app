from api.models import User, Campaign, Donation, Message


def validate_title(title, description):

    if len(description) < 20:
        raise ValueError("Description must be at least 20 characters long")

    elif len(title) < 10:
        raise ValueError("Title must be at least 10 characters long")
    else:
        title = Campaign.query.filter(Campaign.title == title).first()
        if title:
            raise ValueError("Title already exist. Please rename")


def validate_user(user_id):
    user = User.query.filter(User.id == user_id).first()
    if not user:
        raise ValueError("Please create an account")


def validate_email(email):
    user = User.query.filter(User.email == email).first()
    if user:
        raise ValueError("Email is already registered to another account")
