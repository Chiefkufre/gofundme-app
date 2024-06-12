from flask_jwt_extended import JWTManager, get_jwt_identity
from core.models import User

jwt = JWTManager(add_context_processor=True)


@jwt.user_identity_loader
def user_identity_lookup(user):
    return {
        "id": user.id,
        "email": user.email,
    }


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    user_id = jwt_data.get("id")

    if user_id:
        return User.query.get(user_id)
    else:
        return User.query.filter_by(id=identity).one_or_none()
