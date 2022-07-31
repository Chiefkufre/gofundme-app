from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, StringField,DateTimeField, BooleanField
from wtforms.validators import DataRequired, Email, URL, EqualTo, Regexp, Length


class SignUpForm(FlaskForm):
    country = StringField("country", validators=[DataRequired])
    post_code = StringField("postcode", validators=[DataRequired])
    first_name = StringField("first name", validators=[DataRequired])
    last_name = StringField("last name", validators=[DataRequired])
    about = SelectField("Who are you raising the fund for?", validators=[DataRequired],
                        choices=[
                            (
                                "Yourself-Fund will be credited into your account","Yourself-Fund will be credited into your account"
                            ),
                            ("Someone else-You will invite a beneficiary to receive fund or distribute it yourself","Someone else-You will invite a beneficiary to receive fund or distribute it yourself")
                        ])
    amount = StringField("Your starting goal", validators=[DataRequired])