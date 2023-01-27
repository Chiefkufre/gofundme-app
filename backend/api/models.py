from datetime import datetime
from sqlalchemy import DateTime
from flask_migrate import Migrate
from api.database import db




# Database ORM


class User(db.Model):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    bio = db.Column(db.String(50), unique=True)
    profile_picture = db.Column(db.String(255))
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = db.Column(db.String(20), default="pending")
    campaigns = db.relationship('Campaign', backref='user', lazy=True)
    donations = db.relationship('Donation', backref='user', lazy=True)

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

class Campaign(db.Model):

    __tablename__ = 'campaigns'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    goal = db.Column(db.Float, nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'), nullable=False)
    donations = db.relationship('Donation', backref='campaign', lazy=True)


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

class Donation(db.Model):

    __tablename__ = 'donations'

    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)


    def insert(self):

        db.session.add(self)
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
class Message(db.Model):

    __tablename__ = 'messages'


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
