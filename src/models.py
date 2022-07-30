from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

def setup_db(app):
    db.app = app
    db.init_app(app)
    
    
    
