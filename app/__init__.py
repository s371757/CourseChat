from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import secrets

# Initialize Flask extensions
db = SQLAlchemy()
login_manager = LoginManager()

def create_app():

    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat-with-scripts.db'
    app.config['SECRET_KEY'] = secrets.token_hex(32)  # Replace with a secure key
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions with the app
    db.init_app(app)
    login_manager.init_app(app)

    # Import and register blueprints
    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # Import and register other blueprints as needed
    # from .auth import auth as auth_blueprint
    # app.register_blueprint(auth_blueprint)

    return app
