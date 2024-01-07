from core.models import User, Campaign, Donation, Message


class Validator:
    def __init__(self, model=None, create=False):
        self.model = model
        self.create = create

    def validate_title(self, title, description):
        """Validates title length, uniqueness (for creation), and description length."""
        if len(description) < 20:
            raise ValueError("Description must be at least 20 characters long")

        if len(title) < 10:
            raise ValueError("Title must be at least 10 characters long")

        if self.create and self.model.query.filter(self.model.title == title).first():
            raise ValueError("Title already exists. Please rename.")

    def validate_user(self, user_id):
        """Validates user existence."""
        if not User.query.filter(User.id == user_id).first():
            raise ValueError("User Not found. Please create an account")

    def validate_email(self, email):
        """Validates email uniqueness."""
        if User.query.filter(User.email == email).first():
            raise ValueError("Email is already registered to another account")

    def validate_title_on_update(self, title, description):
        """Validates title and description lengths for updates."""
        self.validate_title(title, description)  # Reuse title validation logic

    def validate_json_request(self, data):
        """Validates required fields in a JSON request."""
        errors = {}
        for field in self.model_fields:
            if field not in data:
                errors[field] = f"Field '{field}' is required."
        return errors

    def validate_form_request(self, form_data):
        """Validates required fields in a form request."""
        errors = {}
        for field in self.model_fields:
            if field not in form_data:
                errors[field] = f"Field '{field}' is required in the form."
        return errors

    @property
    def model_fields(self):
        return getattr(self.model, 'get_fields', lambda: [])()



