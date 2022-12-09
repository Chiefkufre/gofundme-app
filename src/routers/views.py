import email
from hashlib import sha256
from unicodedata import category

import flask
import validators

from flask import redirect, render_template, abort, Blueprint, flash, url_for, jsonify
from src.models import Users, Contacts, Campaigns
from src.forms import ContactForm


views = Blueprint("views", __name__)


@views.route("/")
def home():
    return render_template("pages/home.html")


@views.get("/contact")
def contact_us():
    form = ContactForm()

    return render_template("forms/contact.html", form=form)


@views.post("/contact")
def message_us():
    form = ContactForm()

    try:
        message = form.message.data
        email = form.email.data
        subject = form.subject.data

        if len(message) < 5:
            flash(
                "Your message length must be longer than five characters",
                category="error",
            )

        if not validators.email(email):
            flash("Please enter a valid email address")

        elif form.validate_on_submit():
            message = Contacts(email=email, subject=subject, message=message)
            message.insert()

    except:
        message.rollback()
        flash("Something went wrong.Please try again", category="error")
        return redirect(url_for("views.message_us"))
    finally:
        message.close()

    return render_template("pages/home.html")
