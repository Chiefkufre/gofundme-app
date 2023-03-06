from flask import Flask

from api.auth.auths import auths
from api.blog.blog import blog
from api.conf.config import Config, DevConfig, ProdConfig
from api.conf.settings import settings
from api.database import setup_db
from api.routers.search import search
from api.routers.views import views


# start application instance
def create_app_instance():
    app = Flask(__name__)
    app.config.from_object(DevConfig)

    # registring app_context
    with app.app_context():
        setup_db(app)

    app_version = settings.API_VERSION

    # registring routes
    app.register_blueprint(auths, url_prefix="/{0}/auth".format(app_version))
    app.register_blueprint(blog, url_prefix="/{0}/blog".format(app_version))
    app.register_blueprint(views, url_prefix="/{0}".format(app_version))
    app.register_blueprint(search, url_format="/{0}".format(app_version))
    
    return app
