from datetime import datetime
from sqlalchemy import DateTime, Boolean
from flask_migrate import Migrate
from core.database.database import db


# Database ORM

from enum import Enum

class Role(Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = 'admin'
    USER = 'user'
    MODERATOR = 'moderator'
    # Add more roles as needed


class UpdateFromDataMixin:
    def update_from_data(self, data):
        # Update model attributes from data (JSON or form data)
        for key, value in data.items():
            if hasattr(self, key):
                if key == "created_at":
                    # Convert 'created_at' to datetime before setting
                    value = datetime.strptime(value, "%Y-%m-%d")
                setattr(self, key, value)

        # Commit changes after updating all attributes
        db.session.commit()

    def update_from_request(self, request_data):
        # Delegate to the generic update method
        self.update_from_data(request_data)


class CrudMixin:
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


class User(db.Model, UpdateFromDataMixin, CrudMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    bio = db.Column(db.String(500), unique=False)
    profile_picture = db.Column(db.String(255))
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    user_status = db.Column(db.String(20), default="pending")
    campaigns = db.relationship("Campaign", backref="user", lazy=True)
    donations = db.relationship("Donation", backref="user", lazy=True)
    email_verify = db.Column(Boolean, default=False)
    role = db.Column(db.String(50), nullable=False, default="user")
    is_active = db.Column(Boolean, default=False)


    @staticmethod
    def is_authenticated(self):
        return self.is_active

        # return self.email_verify

    @staticmethod
    def _is_active(self):
        return self.is_active
    
    @staticmethod
    def is_anonymous(self):
        return False
    
    @staticmethod
    def is_admin(self):
        return self.role == "admin"
    
    @staticmethod
    def is_superAmin(self):
        return self.role == "super_admin"
    
    @staticmethod
    def is_user(self):
        return self.role == "user"
    
    def get_id(self):
        # Retrieve the list of fields from the class attribute
        return self.id

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "bio": self.bio,
            "profile_picture": self.profile_picture,
            "campaigns": [camp.serialize() for camp in self.campaigns],
            "donations": [donate.serialize() for donate in self.donations],
            "created_at": self.created_at.strftime("%Y-%m-%d"),
            "isActive": self.is_active,
            "role": self.role,
        }

    fields = [
        "id",
        "name",
        "email",
        "bio",
        "profile_picture",
        "password",
        "created_at",
        "updated_at",
        "user_status",
        "campaigns",
        "donations",
        "is_active",
    ]

    required = [ ]
   
    @classmethod
    def get_fields(cls):
        # Retrieve the list of fields from the class attribute
        return cls.fields
   
    @classmethod
    def required_fields(cls):
        return cls.required


class Campaign(db.Model, UpdateFromDataMixin, CrudMixin):
    __tablename__ = "campaigns"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(1000), nullable=False)
    goal = db.Column(db.Float, nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    donations = db.relationship("Donation", backref="campaign", lazy=True)
    is_publish = db.Column(Boolean, default=False)
    is_active = db.Column(Boolean, default=False)

    def publish(self, state):
        if state != self.is_publish:
            self.is_publish = state
            db.session.commit
        return self.is_publish

    def activate(self, status):
        """Activates the campaign if the user's email is verified."""
        if self.user.email_verify:
            self.is_active = status
        db.session.commit()

    def serialize(self):
        return {
            "id": self.id,
            "title": self.title,
            "goal": self.goal,
            "duration": self.duration,
            "description": self.description,
            "donations": [donate.serialize() for donate in self.donations],
            "created_by": self.user_id,
            "created_at": self.created_at.strftime("%Y-%m-%d"),
            "is_active": self.is_active,
            "is_publish": self.is_publish,
        }

    fields = [
        "id",
        "title",
        "goal",
        "duration",
        "description",
        "user_id",
        "donations",
        "created_at",
        "is_active",
        "is_publish",
    ]

    required = [
        "title",
        "goal",
        "duration",
        "description",
        "user_id",
    ]

    @classmethod
    def get_fields(cls):
        # Retrieve the list of fields from the class attribute
        return cls.fields

    @classmethod
    def required_fields(cls):
        return cls.required


class Donation(db.Model, UpdateFromDataMixin, CrudMixin):
    __tablename__ = "donations"

    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), default=0)
    campaign_id = db.Column(db.Integer, db.ForeignKey("campaigns.id"), nullable=False)

    # def __init__(self, amount):
    #     self.amount = amount

    def serialize(self):
        return {
            "id": self.id,
            "amount": self.amount,
            "user_id": self.user_id,
            "campaign_id": self.campaign_id,
            "created_at": self.created_at.strftime("%Y-%m-%d"),
        }

    fields = [
        "id",
        "amount",
        "user_id",
        "campaign_id",
    ]

    required = [
        "amount",
        "campaign_id",
    ]

    def anonymous_donor(self):
        if self.user_id == 0:
            self.user.name = "anonymous"
            db.session.commit()
        return self.user_id

    @classmethod
    def get_fields(cls):
        # Retrieve the list of fields from the class attribute
        return cls.fields

    @classmethod
    def required_fields(cls):
        return cls.required

    def increase_donation(self, amount):
        return self.amount + float(amount)


# database structure for contact messages
class Message(db.Model, CrudMixin):
    __tablename__ = "messages"

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    subject = db.Column(db.String, nullable=False, unique=True)
    message = db.Column(db.Text, nullable=False, unique=True)
    created_at = db.Column(DateTime, default=datetime.now())

    def __init__(self, email, subject, message):
        self.email = email
        self.subject = subject
        self.message = message

    fields = [
        "id",
        "email",
        "subject",
        "message",
        "created_at",
    ]

    @classmethod
    def get_fields(cls):
        # Retrieve the list of fields from the class attribute
        return cls.fields
