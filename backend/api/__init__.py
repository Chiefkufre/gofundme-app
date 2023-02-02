# from flask import Flask
# from .models import setup_db
# from flask_ckeditor import CKEditor
# from flask_bcrypt import Bcrypt


# bcrypt = Bcrypt()
# ckeditor = CKEditor()

# # all application configuration is handled from the models.py file
# def main_app():
#     app = Flask(__name__)
#     bcrypt.init_app(app)
#     ckeditor.init_app(app)
#     setup_db(app)

#     from .views import views
#     from .auths import auths

#     # register for routes
#     app.register_blueprint(views, url_prefix=("/"))
#     app.register_blueprint(auths, url_prefix=("/"))

#     return app
