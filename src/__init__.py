from flask import Flask, jsonify, abort, redirect, render_template,flash, url_for
# from .models import setup_db


def main_app():
    app = Flask(__name__)
    # setup_db(app)
    
    @app.route("/")
    def home():
        
        return render_template("pages/home.html")
    
    
    return app