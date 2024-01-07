from flask import Flask

from core.utils.assets import configure_assets

from core.conf.config import Config, DevConfig, ProdConfig
from core.conf.settings import settings
from core.database import setup_db
from core.web.routes.index import index
from core.web.routes.search import search
from core.web.routes.campaign import campaigns


from core.auth.auths import auths


# start application instance
def create_app_instance():
    app = Flask(__name__)
    app.config.from_object(DevConfig)

    # registring app_context
    with app.app_context():
        setup_db(app)
        configure_assets(app)
    app_version = settings.API_VERSION

    # registring routes
    app.register_blueprint(campaigns, url_prefix="/")
    app.register_blueprint(index, url_prefix="/{0}/api".format(app_version))
    app.register_blueprint(auths, url_prefix="/{0}/auth".format(app_version))
    app.register_blueprint(search, url_format="/{0}".format(app_version))
    
    return app
