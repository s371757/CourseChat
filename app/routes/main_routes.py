from flask import Blueprint, render_template, request, redirect, url_for, session
from flask_login import login_user, logout_user

from ..forms import LoginForm 
from ..db.models import User, Course, University   
from ..db.db_setup import db


__author__ = "Julia Wenkmann"

main = Blueprint('main', __name__)

# Routes
@main.route('/')
def index():
    courses = Course.query.all()  
    return render_template('index.html', courses=courses)

@main.route('/test')
def test():
    return render_template('latex.html')


@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if not username or not password:
            return redirect(url_for('main.register'))
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('main.login'))
    return render_template('register.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.password_hash == form.password.data:
            # The login_user function is crucial for handling user session with Flask-Login
            session['user_id'] = user.id
            login_user(user)
            
            #Assuming a super admin check with hardcoded username (not recommended for production)
            if user.id == 1:
                universities = University.query.all()
                courses = Course.query.all()
                users = User.query.all()
                return render_template('superadmin.html', universities = universities, courses = courses, users = users)
            else:
                courses = Course.query.filter_by(user_id=user.id).all()
                return render_template('admin.html', courses=courses)
    return render_template('login.html', form=form)



@main.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))