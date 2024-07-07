from flask import Flask, g, redirect, url_for
from flask_login import LoginManager, current_user
from flask_jwt_extended import JWTManager
from flask_mail import Mail

from core.models import User
from core.src.Repository.repository import _get_item
from core.utils.assets import configure_assets

from core.conf.config import Logger, Config, DevConfig, ProdConfig, CeleryConfig
from core.conf.settings import settings
from core.database.database import setup_db
from core.utils.proj.celery import celery

from core.src.Controllers.webContoller import web
from core.src.Controllers.adminController import admin
from core.src.Controllers.userController import user
from core.auth.authController import auths

from core.utils.extentions import mail

APP_VERSION = settings.API_VERSION

# start application instance
def create_app_instance():
    app = Flask(__name__)
    Logger.init_app(app)
    app.config.from_object(DevConfig)

    # registring app_context
    with app.app_context():
        setup_db(app)
        mail.init_app(app)
        configure_assets(app)
        jwt = JWTManager(app)
        login_manager = LoginManager(app)

        @login_manager.user_loader
        def load_user(user_id):
            return _get_item(User, user_id)

    @app.before_request
    def before_request():
        g.user_id = current_user.get_id()
    
    @jwt.expired_token_loader
    def my_expired_token_callback(jwt_header, jwt_payload):
        return redirect(url_for('auths.get_login_page'))

    # registring routes
    app.register_blueprint(web, url_prefix="/")
    app.register_blueprint(user, url_prefix="/user")
    app.register_blueprint(admin, url_prefix="/admin")
    app.register_blueprint(auths, url_prefix="/auth")

    return app


# /api/v1/auth/register'
