from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import secrets
from flask_cors import CORS
from .routes.admin_routes import admin
from .routes.user_routes import user
from .routes.main_routes import main
from .db.db_setup import init_db

__author__ = "Julia Wenkmann"

def create_app():

    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///coursechat.db'
    app.config['SECRET_KEY'] = secrets.token_hex(32)  # Replace with a secure key
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions with the app
    init_db(app)
    CORS(app)
    app.register_blueprint(admin)
    app.register_blueprint(user)
    app.register_blueprint(main)

    return app