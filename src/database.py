from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_ckeditor import CKEditor


db = SQLAlchemy()
ckeditor = CKEditor()



# database helper class with some app config
def setup_db(app):
    db.app = app
    db.init_app(app)
    db.create_all()
    migrate = Migrate(app, db)

def start_dependencies(app):
    ckeditor.init_app(app)


