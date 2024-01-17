from datetime import datetime
from sqlalchemy import DateTime, Boolean
from flask_migrate import Migrate
from core.database.database import db


# Database ORM


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


class PerformCRUD:
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


class User(db.Model, UpdateFromDataMixin, PerformCRUD):
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
    is_active = db.Column(Boolean, default=True)
    email_verify = db.Column(Boolean, default=False)

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

    @classmethod
    def get_fields(cls):
        # Retrieve the list of fields from the class attribute
        return cls.fields


class Campaign(db.Model, UpdateFromDataMixin, PerformCRUD):
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
    is_active = db.Column(Boolean, default=False)

    def activate(self):
        """Activates the campaign if the user's email is verified."""
        if self.user.email_verify:
            self.is_active = True
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


class Donation(db.Model, UpdateFromDataMixin, PerformCRUD):
    __tablename__ = "donations"

    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
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

    @classmethod
    def get_fields(cls):
        # Retrieve the list of fields from the class attribute
        return cls.fields

    def increase_donation(self, amount):
        return self.amount + float(amount)


# database structure for contact messages
class Message(db.Model, PerformCRUD):
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
