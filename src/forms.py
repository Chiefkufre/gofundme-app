from flask_wtf import FlaskForm
from wtforms import FileField,SelectField, SubmitField, StringField,DateTimeField, BooleanField, PasswordField, IntegerField
from wtforms.validators import DataRequired, Email, URL, EqualTo, Regexp, Length
from flask_wtf.file import FileField, FileAllowed, FileRequired
from flask_ckeditor import CKEditorField


class SignUpForm(FlaskForm):
    email = StringField("email address", validators=[DataRequired(), Email()])
    password = PasswordField("password", validators=[DataRequired(), Length(min=8, message="password must be more than 8 characters")])
    confirmPassword = PasswordField("confirm password", validators=[DataRequired(), EqualTo("password", message="password not match")])
    userImage = FileField("profile Picture", validators=[FileAllowed(["jpg","png"]), FileRequired("file was empty")])
    country = StringField("country", validators=[DataRequired()])
    post_code = IntegerField("postcode", validators=[DataRequired()])
    first_name = StringField("first name", validators=[DataRequired()])
    last_name = StringField("last name", validators=[DataRequired()])
    about = SelectField("Who are you raising the fund for?", validators=[DataRequired()],
                        choices=[
                            (
                                "Yourself-Fund will be credited into your account","Yourself-Fund will be credited into your account"
                            ),
                            ("Someone else-You will invite a beneficiary to receive fund or distribute it yourself","Someone else-You will invite a beneficiary to receive fund or distribute it yourself")
                        ])
    amount = IntegerField("Your starting goal", validators=[DataRequired()])
    submit = SubmitField('continue')
    
    class SignInForm(FlaskForm):
        email = StringField("email address", validators=[DataRequired(), Email()])
        password = PasswordField("password", validators=[DataRequired(), Length(min=8, message="password must be more than 8 characters")])
        submit = SubmitField("Login")
    
    
    
class ContactForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    subject = StringField('Subject', validators=[DataRequired(), Length(min=10, max=100)])
    message = CKEditorField('Message',validators=[DataRequired(), Length(min=5)])
    submit = SubmitField('Send')