from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
import secrets
from flask_cors import CORS

# Initialize Flask extensions
db = SQLAlchemy()
login_manager = LoginManager()

def create_app():

    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///coursechat.db'
    app.config['SECRET_KEY'] = secrets.token_hex(32)  # Replace with a secure key
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions with the app
    db.init_app(app)
    login_manager.init_app(app)
    migrate = Migrate(app, db)

    CORS(app)

    # Import and register blueprints
    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # Import and register other blueprints as needed
    # from .auth import auth as auth_blueprint
    # app.register_blueprint(auth_blueprint)

    return app

@login_manager.user_loader
def load_user(user_id):
    from .models import User  # Import here to avoid circular import issues
    return User.query.get(int(user_id))