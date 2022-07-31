from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, StringField,DateTimeField, BooleanField, PasswordField
from wtforms.validators import DataRequired, Email, URL, EqualTo, Regexp, Length


class SignUpForm(FlaskForm):
    email = StringField("email address", validators=[DataRequired(), Email()])
    password = PasswordField("password", validators=[DataRequired(), Length(min=8, message="password must be more than 8 characters")])
    confirmPassword = PasswordField("confirm password", validators=[DataRequired(), EqualTo("password", message="password not match")])
    country = StringField("country", validators=[DataRequired()])
    post_code = StringField("postcode", validators=[DataRequired()])
    first_name = StringField("first name", validators=[DataRequired()])
    last_name = StringField("last name", validators=[DataRequired()])
    about = SelectField("Who are you raising the fund for?", validators=[DataRequired()],
                        choices=[
                            (
                                "Yourself-Fund will be credited into your account","Yourself-Fund will be credited into your account"
                            ),
                            ("Someone else-You will invite a beneficiary to receive fund or distribute it yourself","Someone else-You will invite a beneficiary to receive fund or distribute it yourself")
                        ])
    amount = StringField("Your starting goal", validators=[DataRequired()])
    submit = SubmitField('continue')
    
    class SignInForm(FlaskForm):
        email = StringField("email address", validators=[DataRequired(), Email()])
        password = PasswordField("password", validators=[DataRequired(), Length(min=8, message="password must be more than 8 characters")])
        submit = SubmitField("Login")
    
    
    
class ContactForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    subject = StringField('Subject', validators=[DataRequired(), Length(min=10, max=100)])
    message = CKEditorField('Message')
    submit = SubmitField('Submit')