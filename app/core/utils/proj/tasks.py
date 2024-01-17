from core.models import Campaign, User
from core.database.database import db
from core.utils.proj.celery import app

@app.task
def activate_campaign(campaign_id) -> bool:
    """This method will activate campaign
    
    return
        bool - True | False
    """

    campaign = Campaign.query.get_or_404(campaign_id)
    campaign.activate() 


@app.task
def verify_email(state, user_id) -> bool:
    """This function will verify email address

    Args:
        state - True | False
        user_id: user identity
    
    return
      bool - True | False
    
    """
    user = User.query.get_or_404(user_id)
    user.email_verify = state
    user.is_active = state
    db.session.commit()
    return user.email_verify 