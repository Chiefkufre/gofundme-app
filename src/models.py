from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import false


db = SQLAlchemy()

def setup_db(app):
    db.app = app
    db.init_app(app)
    
    
    
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, nullable=false, unique=True)
    first_name = db.Column(db.String, nullable=False, unique=True)
    last_name = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    