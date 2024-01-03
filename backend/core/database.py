from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


db = SQLAlchemy()


# database helper class for database initialization
def setup_db(app):
    db.app = app
    db.init_app(app)
    db.create_all()
    migrate = Migrate(app, db)


def start_dependencies(app):
    pass
