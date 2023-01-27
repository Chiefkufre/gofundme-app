from flask import Flask
from .database import setup_db
from api.conf.config import Config, DevConfig, ProdConfig
from api.conf.settings import settings

from api.auth.auths import auths
from api.routers.views import views
from api.blog.blog import blog


def create_app_instance():
    app = Flask(__name__)
    app.config.from_object(DevConfig)

    # registring app_context
    with app.app_context():
        setup_db(app)


    app_version = settings.API_VERSION

    # registring routes
    app.register_blueprint(auths, url_prefix='/{app_version}/auth')
    app.register_blueprint(blog, url_prefix="/{app_version}/blog")
    app.register_blueprint(views,url_prefix="/{app_version}/views")

    return app
    

