from ast import Return
import email
from tkinter.tix import Form
from unicodedata import category

import flask
import validators
from . import bcrypt, ckeditor
from flask import redirect, render_template, abort, Blueprint, flash, url_for, jsonify
from flask_login import login_required, login_user, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from .forms import SignUpForm, ContactForm, SignInForm
from .models import Users, Contacts, Campaigns, db



views = Blueprint('views', __name__)


@views.route("/")
def home():
    return render_template("pages/home.html")


@views.get('/contact')
def contact_us():
    form = ContactForm()
    
    return render_template('forms/contact.html', form=form)

@views.post('/contact')
def message_us():
    form = ContactForm()
    
    try:
        message = form.message.data
        email = form.email.data
        subject = form.subject.data
        
        if len(message) < 5:
            flash('Your message length must be longer than five characters', category='error')
            
        if not validators.email(email):
            flash('Please enter a valid email address')
            
        elif form.validate_on_submit():
            message = Contact(email=email, subject=subject, message=message)
            message.insert()   
        
    except:
         message.rollback()
         flash('Something went wrong.Please try again', category='error')
         return redirect(url_for('views.message_us'))
    finally:
     message.close()
            
    return render_template('pages/home.html')

@views.get('/login')
def login_form():
    form = SignInForm()
    
    return render_template('forms/login.html', form=form)

@views.post('/login')
def login_user():
    form =  SignInForm()
    
    try:
        email = form.email.data
        password = form.password.data
        
        user = Users.query.filter_by(email=email).first()
        
        if user:
            is_password_correct = check_password_hash(user.password, password)
            
            if is_password_correct:
                flash('Login successful', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Password is not correct. Please try again', category='failure')
        else:
            flash("Email doesn't match any account", category='failure')
    except:
        flash('Something is wrong. Please try again', category='failure')
        return redirect(url_for('views.home'))
        
    return render_template('pages/login.html', user = current_user) 


                                    # email 
                                    # password 
                                    # confirmPassword 
                                    # userImage 
                                    # country
                                    # post_code 
                                    # first_name 
                                    # last_name 
                                    # about =    amount 
                                    # submit 
    
        
    