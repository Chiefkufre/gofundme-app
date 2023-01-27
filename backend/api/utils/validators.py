
from api.models import User, Campaign, Donation, Message



def validate_title(title, description):
    title  = Campaign.query.filter(Campaign.title == title).first()

    if title:
        raise ValueError("Title already exist. Please rename")
    elif len(title) < 10:
       raise ValueError("Title must be at least 10 characters long")
    elif len(description) < 20:
        raise ValueError("Description must be at least 20 characters long")

def validate_user(user_id):
   user = Campaign.query.filter(Campaign.title == title).first()
   if not user:
     raise ValueError("Please create an account")

