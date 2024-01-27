from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    TextAreaField,
    FloatField,
    IntegerField,
    BooleanField,
    SubmitField,
    PasswordField,
)
from wtforms.validators import DataRequired, Length, Email, EqualTo


class CampaignForm(FlaskForm):
    title = StringField("title", validators=[DataRequired(), Length(max=100)])
    description = TextAreaField(
        "description", validators=[DataRequired(), Length(max=1000)]
    )
    goal = FloatField("goal", validators=[DataRequired()])
    duration = IntegerField("duration", validators=[DataRequired()])
    is_active = BooleanField("False")
    submit = SubmitField("Create Campaign")


class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(max=50)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=50)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("password")]
    )
    bio = TextAreaField("Bio", validators=[Length(max=50)])
    submit = SubmitField("Create User")
