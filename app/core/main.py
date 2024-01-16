from flask import Flask, g

from core.utils.assets import configure_assets

from core.conf.config import Config, DevConfig, ProdConfig
from core.conf.settings import settings
from core.database.database import setup_db

from core.api.APIControllers.routers import api
from core.api.APIControllers.index import index
from core.web.WebControllers.search import search
from core.web.WebControllers.campaign import views


from core.auth.auths import auths

APP_VERSION = settings.API_VERSION


# start application instance
def create_app_instance():
    app = Flask(__name__)
    app.config.from_object(DevConfig)

    # registring app_context
    with app.app_context():
        setup_db(app)
        configure_assets(app)

    @app.before_request
    def before_request():
        g.user_id = "1"
        
    # registring routes
    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(api, url_prefix="/api/{0}".format(APP_VERSION))
    app.register_blueprint(index, url_prefix="/api/{0}".format(APP_VERSION))
    app.register_blueprint(auths, url_prefix="/{0}/auth".format(APP_VERSION))
    app.register_blueprint(search, url_format="/{0}".format(APP_VERSION))

    return app
