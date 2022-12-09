from flask import Flask
from .database import setup_db
from src.conf.config import Config, DevConfig, ProdConfig
from src.conf.settings import settings


from src.api.api import api
from src.auth.auths import auths
from src.routers.views import views
from src.blog.blog import blog


def create_app_instance():
    app = Flask(__name__)
    app.config.from_object(DevConfig)

    # registring app_context
    with app.app_context():
        setup_db(app)


    app_version = settings.API_VERSION
    # registring routes

    app.register_blueprint(api, url_prefix=app_version)
    app.register_blueprint(auths, url_prefix='/auth')
    app.register_blueprint(blog, url_prefix="/blog")
    app.register_blueprint(views)

    return app
    

