from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __init__(self, username, password, role):
        self.username = username
        self.password_hash = generate_password_hash(password)
        self.role = role

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)

def create_roles():
    roles = {
        'SUPER_ADMIN': 'super_admin',
        'ADMIN': 'admin',
        'USER': 'user',
        'MODERATOR': 'moderator',
        'OWNER': 'owner'
    }
    for r in roles:
        role = Role.query.filter_by(name=roles[r]).first()
        if role is None:
            role = Role(name=roles[r])
            db.session.add(role)
    db.session.commit()

def create_users():
    users = [
        {'username': 'super_admin', 'password': 'super_admin_password', 'role': 'SUPER_ADMIN'},
        {'username': 'admin', 'password': 'admin_password', 'role': 'ADMIN'},
        {'username': 'user', 'password': 'user_password', 'role': 'USER'},
        {'username': 'moderator', 'password': 'moderator_password', 'role': 'MODERATOR'},
        {'username': 'owner', 'password': 'owner_password', 'role': 'OWNER'}
    ]
    for user in users:
        new_user = User(username=user['username'], password=user['password'], role=Role.query.filter_by(name=user['role']).first())
        db.session.add(new_user)
    db.session.commit()