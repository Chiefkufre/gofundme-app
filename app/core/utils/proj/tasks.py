from core.models import Campaign, User
from core.database.database import db
from .celery import celery


@celery.task
def activate_campaign(campaign_id, state) -> bool:
    """This method will activate campaign

    return
        bool - True | False
    """
    print("calling task.........")
    campaign = Campaign.query.get_or_404(campaign_id)
    campaign.activate(state)
    print(".....done.........")
    return campaign.is_active


@celery.task
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
