from datetime import datetime
from sqlalchemy import DateTime
from flask_migrate import Migrate
from api.database import db




# Database ORM

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, nullable=False)    
    first_name = db.Column(db.String, nullable=False, unique=True)
    last_name = db.Column(db.String, nullable=False, unique=True)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    campaign = db.relationship(
        "Campaigns", backref="User", lazy=False, cascade="all, delete-orphan"
    )
    created_at = db.Column(db.DateTime, default=datetime.now())
    # simple helper method to persist data into the database
    def insert(self):
        db.session.add(self)
        db.session.commit()

    # simple helper method to update data into the database
    def update(self):
        db.session.commit()

    def rollback(self):
        db.session.rollback()

    def close(self):
        db.session.close()

    # simple helper method to delete data into the database
    def delete(self):
        db.session.delete(self)
        db.session.commit()


# Class to handle campaign details
class Campaign(db.Model):

    __tablename__ = "campaigns"

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    country = db.Column(db.String, nullable=False, unique=False)
    post_code = db.Column(db.Integer, nullable=False)
    amount_to_raise = db.Column(db.Integer, nullable=False)
    campaign_owner = db.Column(db.String, nullable=False)
    describe_campaign = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"))
    created_at = db.Column(DateTime, default=datetime.now())


    def __init__(
        self, country, post_code, amount_to_raise, campaign_owner, describe_campaign
    ):
        self.country = country
        self.post_code = post_code
        self.amount_to_raise = amount_to_raise
        self.Campaign_owner = campaign_owner
        self.describe_campaign = describe_campaign

    def insert(self):
        db.session.add(self)
        db.session.commit()

    # simple helper method to update data into the database
    def update(self):
        db.session.commit()

    def rollback(self):
        db.session.rollback()

    def close(self):
        db.session.close()

    # simple helper method to delete data into the database
    def delete(self):
        db.session.delete(self)
        db.session.commit()


# database structure for contact messages
class Contact(db.Model):

    __tablename__ = 'contacts'


    id = db.Column(db.Integer, primary_key=True, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    subject = db.Column(db.String, nullable=False, unique=True)
    message = db.Column(db.Text, nullable=False, unique=True)
    created_at = db.Column(DateTime, default=datetime.now())


    def __init__(self, email, subject, message):
        self.email = email
        self.subject = subject
        self.message = message

    # simple helper method to persist data into the database
    def insert(self):
        db.session.add(self)
        db.session.commit()

    # simple helper method to update data into the database
    def update(self):
        db.session.commit()

    # simple helper method to delete data into the database
    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def rollback(self):
        db.session.rollback()

    def close(self):
        db.session.close()
