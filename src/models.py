from email import message
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import false
from flask_migrate import Migrate


db = SQLAlchemy()

def setup_db(app):
    app.config.from_object('config.DevConfig')
    db.app = app
    db.init_app(app)
    db.create_all()
    migrate = Migrate(app, db)
    
    
    #structure for user table
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, nullable=False, unique=True)
    last_name = db.Column(db.String, nullable=False, unique=True)
    email = db.Column(db.String, nullable=false, unique=True)
    password = db.Column(db.String, nullable=False)
    country = db.Column(db.String, nullable=False, unique=False)
    post_code = db.Column(db.Integer, nullable=False)
    about = db.Column(db.Text, nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    
    
    
    
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




#database structure for contact messages
class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, nullable=false, unique=True)
    subject = db.Column(db.String, nullable=false, unique=True)
    message = db.Column(db.Text, nullable=false, unique=True)
    
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

    
    
   