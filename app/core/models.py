import uuid
import random
from datetime import datetime
from sqlalchemy import DateTime, Boolean

from sqlalchemy.dialects.postgresql import UUID as pgUUID
from sqlalchemy.dialects.sqlite import TEXT as sqliteTEXT
from sqlalchemy.types import TypeDecorator, CHAR

from flask_migrate import Migrate
from core.utils.general import generate_transaction_reference
from core.database.database import db


# Database ORM

from enum import Enum


class Role(Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    USER = "user"
    MODERATOR = "moderator"
    # Add more roles as needed


class GUID(TypeDecorator):
    """Platform-independent GUID type.
    
    Uses PostgreSQL's UUID type, otherwise uses CHAR(32), storing as stringified hex values.
    """
    impl = CHAR
    cache_ok = True  

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(pgUUID())
        else:
            return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                value = uuid.UUID(value)
            return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return str(uuid.UUID(value))
    
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

    def clean(self):
        db.session.rollback(self)

    def close(self):
        db.session.close(self)

    # simple helper method to delete data into the database
    def delete(self):
        db.session.delete(self)
        db.session.commit()

class User(db.Model, UpdateFromDataMixin, CrudMixin):
    __tablename__ = "users"

    id = db.Column(GUID(), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    bio = db.Column(db.String(500), unique=False)
    address = db.Column(db.String(500), unique=False)
    profile_picture = db.Column(db.String(255))
    password = db.Column(db.String(200), nullable=False)
    user_status = db.Column(db.String(20), default="pending")
    is_active = db.Column(Boolean, default=False)
    email_verify = db.Column(Boolean, default=False)
    notifications = db.relationship('Notification', backref='user', lazy=True, cascade="all, delete-orphan")
    campaigns = db.relationship("Campaign", backref="user", lazy=True, cascade="all, delete-orphan")
    # donations = db.relationship("Donation", backref="user", lazy=True, cascade="all, delete-orphan")
    
    donations_made = db.relationship("Donation", foreign_keys="Donation.donor_id", back_populates="donor", lazy="dynamic")
    donations_received = db.relationship("Donation", foreign_keys="Donation.recipient_id", back_populates="recipient", lazy="dynamic")
    
    comments = db.relationship("Comment", backref="user", lazy=True, cascade="all, delete-orphan")
    user_type = db.Column(db.String(50), default="user")

    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(
        db.DateTime, default=datetime.now, onupdate=datetime.now
    )
    
    __mapper_args__ = {
        'polymorphic_identity': 'user',
        'polymorphic_on': user_type
    }
    @staticmethod
    def is_authenticated(self):
        return True

        # return self.email_verify

    @staticmethod
    def _is_active(self):
        return self.is_active

    @staticmethod
    def is_anonymous(self):
        return False

    @staticmethod
    def is_admin(self):
        return self.user_type == "admin"

    @staticmethod
    def is_superAmin(self):
        return self.user_type == "super_admin"

    @staticmethod
    def is_user(self):
        return self.user_type == "user"

    def get_id(self):
        # Retrieve the list of fields from the class attribute
        return str(self.id)

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "bio": self.bio,
            "profile_picture": self.profile_picture,
            "campaigns": [camp.serialize() for camp in self.campaigns],
            "donations": [donate.serialize() for donate in self.donations_received],
            "donations_made": [donate.serialize() for donate in self.donations_made],
            "created_at": self.created_at.strftime("%Y-%m-%d"),
            "isActive": self.is_active,
            "role": self.user_type,
            "address": self.address, 
            "notifications": self.notifications,

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
        "donations_received",
        "donations_made",
        "comments",
        "notifications",
        "is_active",
        "address",
        
    ]

    required = [
        "name",
        "email",
        "password",
    ]

    @classmethod
    def get_fields(cls):
        # Retrieve the list of fields from the class attribute
        return cls.fields

    @classmethod
    def required_fields(cls):
        return cls.required

class Admin(User):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    permissions = db.Column(db.Text)

    __mapper_args__ = {
        'polymorphic_identity': 'admin',
    }

    def __repr__(self):
        return f'<Admin: {self.name}>'
    

class Campaign(db.Model, UpdateFromDataMixin, CrudMixin):
    __tablename__ = "campaigns"

    id = db.Column(GUID(), primary_key=True, default=uuid.uuid4)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(2000), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    goal = db.Column(db.String(50), nullable=False)
    duration = db.Column(db.String(50), nullable=False)
    image_url = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    donations = db.relationship("Donation", backref="campaign", lazy=True, cascade="all, delete-orphan")
    comments = db.relationship('Comment', backref='campaign', lazy=True, cascade="all, delete-orphan")
    is_publish = db.Column(Boolean, default=False)
    is_active = db.Column(Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(
        db.DateTime, default=datetime.now, onupdate=datetime.now
    )


    def publish(self, state):
        if state != self.is_publish:
            self.is_publish = state
            self.insert()
        return self.is_publish

    def toggle(self, status):
        """Activates the campaign if the user's email is verified."""
        # if self.user.email_verify:
        self.is_active = status
        self.insert()
        return self.is_active

    def serialize(self):
        return {
            "id": self.id,
            "title": self.title,
            "goal": self.goal,
            "duration": self.duration,
            "description": self.description,
            "donations": [donate.serialize() for donate in self.donations],
            "user_id": self.user_id,
            "created_at": self.created_at.strftime("%Y-%m-%d-%H:%M:%S"),
            "is_active": self.is_active,
            "is_publish": self.is_publish,
            "type": self.type,
            "image_url": self.image_url,
        }

    fields = [
        "id",
        "title",
        "goal",
        "duration",
        "description",
        "user_id",
        "donations",
        "comments",
        "created_at",
        "is_active",
        "is_publish",
        "type",
        "image_url",
    ]

    required = [
        "title",
        "goal",
        "duration",
        "description",
        "user_id",
        "image_url",
        
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

    id = db.Column(GUID(), primary_key=True, default=uuid.uuid4)
    amount = db.Column(db.Float, nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    donor_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True, default=0)
    campaign_id = db.Column(db.Integer, db.ForeignKey("campaigns.id"), nullable=False)
    transaction_ref = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
   

    donor = db.relationship("User", foreign_keys=[donor_id], back_populates="donations_made")
    recipient = db.relationship("User", foreign_keys=[recipient_id], back_populates="donations_received")

    def __init__(self, *args, **kwargs):
        super(Donation, self).__init__(*args, **kwargs)
        self.transaction_ref = self.generate_transaction_ref()

    def generate_transaction_ref(self):
        return generate_transaction_reference()

    def serialize(self):
        return {
            "id": self.id,
            "amount": self.amount,
            "donor_id": self.donor_id,
            "recipient_id": self.recipient_id,
            "campaign_id": self.campaign_id,
            "transaction_ref": self.transaction_ref,
            "created_at": self.created_at.strftime("%Y-%m-%d-%H:%M:%S"),
        }

    fields = [
        "id",
        "amount",
        "donor_id",
        "recipient_id",
        "campaign_id",
    ]

    required = [
        "amount",
        "campaign_id",
        "recipient_id",
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


class Notification(db.Model, CrudMixin):
    __tablename__ = "notifications"

    id = db.Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), default=0)
    activity_id = db.Column(db.Integer, nullable=False)
    type = db.Column(db.String(50), nullable=False)
    message = db.Column(db.Text, nullable=True)
    read = db.Column(db.Boolean, default=False) 
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(
        db.DateTime, default=datetime.now, onupdate=datetime.now
    )

    def __init__(self, user_id, activity_id, type, message) -> None:
        self.user_id = user_id
        self.activity_id = activity_id
        self.type = type
        self.message = message

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "activity_id": self.activity_id,
            "type": self.type,
            "message": self.message,
            "read": self.read,
            "created_at": self.created_at.strftime("%Y-%m-%d-%H:%M:%S"),
            "update_at": self.updated_at
        }

    fields = [
        "id",
        "user_id",
        "activity_id",
        "type",
        "message",
        "read",
        "created_at",
        "update_at"
    ]

    required_fields = [
        "user_id",
        "activity_id",
        "type",
        "message",
    ]

    @classmethod
    def get_fields(cls):
        # Retrieve the list of fields from the class attribute
        return cls.fields

    @classmethod
    def required_fields(cls):
        return cls.required

class Comment(db.Model, CrudMixin):
    __tablename__ = "comments"

    id = db.Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), default=0)
    campaign_id = db.Column(db.Integer, db.ForeignKey("campaigns.id"), nullable=False)
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(
        db.DateTime, default=datetime.now, onupdate=datetime.now
    )

    def __init__(self, user_id, campaign_id, comment) -> None:
        self.user_id = user_id
        self.campaign_id = campaign_id
        self.comment = comment
       

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "campaign_id": self.campaign_id,
            "comment": self.comment,
            "created_at": self.created_at,
            "update_at": self.updated_at
        }

    fields = [
        "id",
        "user_id",
        "campaign_id",
        "comment",
        "created_at",
        "update_at"
    ]

    required_fields = [
        "user_id",
        "campaign_id",
        "comment",
    ]

    @classmethod
    def get_fields(cls):
        # Retrieve the list of fields from the class attribute
        return cls.fields

    @classmethod
    def required_fields(cls):
        return cls.required

# database structure for contact messages
class Message(db.Model, CrudMixin):
    __tablename__ = "messages"

    id = db.Column(GUID(), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    subject = db.Column(db.String, nullable=False)
    message = db.Column(db.Text, nullable=True)
    created_at = db.Column(DateTime, default=datetime.now())

    def __init__(self, email, name, subject, message):
        self.email = email
        self.name = name
        self.subject = subject
        self.message = message

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "subject": self.subject,
            "message": self.message,
            "created_at": self.created_at.strftime("%Y-%m-%d"),
        }

    fields = [
        "id",
        "name",
        "email",
        "subject",
        "message",
        "created_at",
    ]

    required = [
        "email",
        "subject",
    ]

    @classmethod
    def get_fields(cls):
        # Retrieve the list of fields from the class attribute
        return cls.fields


class Setting(db.Model, UpdateFromDataMixin, CrudMixin):
    __tablename__ = "settings"

    id = db.Column(GUID(), primary_key=True, default=uuid.uuid4)
    app_name = db.Column(db.String, nullable=False)
    created_at = db.Column(DateTime, default=datetime.now())
    app_description = db.Column(db.String(1000), nullable=False)
    site_address = db.Column(db.String, nullable=False)
    admin_email = db.Column(db.String, nullable=False)
    copyright = db.Column(db.String, nullable=False)
    default_role = db.Column(db.String, default="member")
    maintenance_mode = db.Column(Boolean, default=False)

    # Smtp Email settings
    smtp_email = db.Column(db.String, nullable=True)
    smtp_host = db.Column(db.String, nullable=True)
    smtp_password = db.Column(db.String, nullable=True)
    smtp_encryption = db.Column(db.String, nullable=True)
    smtp_port = db.Column(db.String, nullable=True)

    def serialize(self):
        return {
            "id": self.id,
            "app_name": self.app_name,
            "app_description": self.app_description,
            "site_address": self.site_address,
            "admin_email": self.admin_email,
            "copyright": self.copyright,
            "default_role": self.default_role,
            "maintenance_mode": self.maintenance_mode,
            "smtp_email": self.smtp_email,
            "smtp_host": self.smtp_host,
            "smtp_password": self.smtp_password,
            "smtp_encryption": self.smtp_encryption,
            "smtp_port": self.smtp_port,
            "created_at": self.created_at.strftime("%Y-%m-%d"),
        }

    fields = [
        "id",
        "app_name",
        "app_description",
        "site_address",
        "admin_email",
        "copyright",
        "default_role",
        "maintenance_mode",
        "smtp_email",
        "smtp_host",
        "smtp_password",
        "smtp_encryption",
        "smtp_port",
        "created_at",
    ]

    required = [
        "app_name",
        "admin_email",
    ]

    @classmethod
    def get_fields(cls):
        # Retrieve the list of fields from the class attribute
        return cls.fields

class LoginActivity(db.Model, CrudMixin):
    id = db.Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), default=0)
    ip_address = db.Column(db.String(45))
    browser = db.Column(db.String(50))
    browser_version = db.Column(db.String(20))
    os = db.Column(db.String(50))
    os_version = db.Column(db.String(20))
    device = db.Column(db.String(50))
    is_mobile = db.Column(db.Boolean)
    is_tablet = db.Column(db.Boolean)
    is_pc = db.Column(db.Boolean)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    fields = [
        "id",
        "user_id",
        "ip_address",
        "browser",
        "browser_version",
        "os",
        "os_version",
        "device",
        "is_mobile",
        "is_tablet",
        "is_pc",
        "timestamp",
    ]

    required = [
        "user_id",
        "ip_address",
    ]

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "ip_address": self.ip_address,
            "browser": self.browser,
            "browser_version": self.browser_version,
            "os": self.os,
            "os_version": self.os_version,
            "device": self.device,
            "is_mobile": self.is_mobile,
            "is_tablet": self.is_tablet,
            "is_pc": self.is_pc,
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        }

    @classmethod
    def get_fields(cls):
        return cls.fields