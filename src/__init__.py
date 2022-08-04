import bcrypt
from flask import Flask
from .models import setup_db
from flask_ckeditor import CKEditor
from flask_bcrypt import Bcrypt


bcrypt = Bcrypt()

#all application configuration is handled from the models.py file
def main_app():
    app = Flask(__name__)
    bcrypt.init_app(app)
    setup_db(app)
    
   
    from .views import views
    
    #register for routes 
    app.register_blueprint(views, url_prefix=("/"))
    
    return app