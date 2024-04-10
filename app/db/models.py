from flask_sqlalchemy import SQLAlchemy
from .db_setup import db
from werkzeug.security import generate_password_hash, check_password_hash


__author__ = "Julia Wenkmann"
#Database models
class University(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    users = db.relationship('User', backref='university', lazy=True)
    courses = db.relationship('Course', backref='university', lazy=True)

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    university_id = db.Column(db.Integer, db.ForeignKey('university.id'), nullable=False)
    pdfs = db.relationship('Pdf', backref='course', lazy=True)
    password_hash = db.Column(db.String(128), nullable=False)
    api_key = db.Column(db.String(128), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))



class Pdf(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    data = db.Column(db.LargeBinary, nullable=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    entries = db.relationship('ChatEntry', backref='pdf', lazy=True)

class ChatEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(500), nullable=False)
    answer = db.Column(db.String(500))
    page_number = db.Column(db.Integer)
    pdf_id = db.Column(db.Integer, db.ForeignKey('pdf.id'), nullable=False)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    university_id = db.Column(db.Integer, db.ForeignKey('university.id'))  # Ensure this matches the University table name

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @property
    def is_active(self):
        """True, as all users are active."""
        return True

    @property
    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return True

    @property
    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return False

    def get_id(self):
        """Return the user id as a unicode string."""
        return str(self.id)
    