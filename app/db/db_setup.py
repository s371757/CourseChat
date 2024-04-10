__author__ = "Julia Wenkmann"
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

db = SQLAlchemy()
login_manager = LoginManager()

def init_db(app):
    db.init_app(app)
    Migrate(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'


@login_manager.user_loader
def load_user(user_id):
    from .models import User 
    return User.query.get(int(user_id))