from flask import Flask
from .database import setup_db
from src.conf.config import Config, DevConfig, ProdConfig



def create_app_instance():
    app = Flask(__name__)
    app.config.from_object(DevConfig)
    with app.app_context():
        setup_db(app)


    return app
    

