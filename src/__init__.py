import bcrypt
from flask import Flask, jsonify, abort, redirect, render_template,flash, url_for
from .models import setup_db
from flask_ckeditor import CKEditor
from flask_bcrypt import Bcrypt


bcrypt = Bcrypt()
def main_app():
    app = Flask(__name__)
    bcrypt.init_app(app)
    setup_db(app)
    
   
    from .views import views
    app.register_blueprint(views, url_prefix=("/"))
    
    return app