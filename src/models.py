from email import message
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import false
from flask_migrate import Migrate


db = SQLAlchemy()

#database helper class with some app config
def setup_db(app):
    app.config.from_object('config.DevConfig')
    db.app = app
    db.init_app(app)
    db.create_all()
    migrate = Migrate(app, db)
    
    
    #structure for user table
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, nullable=False, unique=True)
    last_name = db.Column(db.String, nullable=False, unique=True)
    email = db.Column(db.String, nullable=false, unique=True)
    password = db.Column(db.String, nullable=False)
    campaign = db.relationship("Campaigns", backref="Artists", lazy=False, cascade="all, delete-orphan")
    
    
    
     #simple helper method to persist data into the database
    def insert(self):
        db.session.add(self)
        db.session.commit()

    #simple helper method to update data into the database
    def update(self):
        db.session.commit()
    
    def rollback(self):
        db.session.rollback()
    
    def close(self):
        db.session.close()

    #simple helper method to delete data into the database
    def delete(self):
        db.session.delete(self)
        db.session.commit()


#Class to handle campaign details
class Campaigns(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String, nullable=False, unique=False)
    post_code = db.Column(db.Integer, nullable=False)
    amount_to_raise = db.Column(db.Integer, nullable=False)
    Campaign_owner = db.Column(db.String, nullable=False)
    describe_campaign = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", on_delete="CASCADE") )
    
    def __init__(self, country, post_code, amount_to_raise, campaign_owner, describe_campaign):
        self.country = country
        self.post_code = post_code
        self.amount_to_raise = amount_to_raise
        self.Campaign_owner = campaign_owner
        self.describe_campaign = describe_campaign
        
    
    def insert(self):
        db.session.add(self)
        db.session.commit()
    
    #simple helper method to update data into the database
    def update(self):
        db.session.commit()
    
    def rollback(self):
        db.session.rollback()
    
    def close(self):
        db.session.close()

    #simple helper method to delete data into the database
    def delete(self):
        db.session.delete(self)
        db.session.commit()
    
    

#database structure for contact messages
class Contacts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, nullable=False, unique=True)
    subject = db.Column(db.String, nullable=false, unique=True)
    message = db.Column(db.Text, nullable=False, unique=True)
    
    def __init__(self, email, subject, message):
        self.email = email
        self.subject = subject
        self.message = message
        
        
    
    #simple helper method to persist data into the database
    def insert(self):
        db.session.add(self)
        db.session.commit()

    #simple helper method to update data into the database
    def update(self):
        db.session.commit()

    #simple helper method to delete data into the database
    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def rollback(self):
        db.session.rollback()
    
    def close(self):
        db.session.close()
    
    
   