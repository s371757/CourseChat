# routes.py
from flask import Blueprint, render_template, request, flash, redirect, url_for, Response, jsonify, session, abort, send_file, make_response, send_from_directory
from flask_login import login_user, logout_user, login_required, current_user, UserMixin
import pandas as pd
from io import BytesIO
from werkzeug.security import check_password_hash

from .forms import LoginForm , PasswordForm
from .utils import allowed_file
from .api import ask_pdf, add_pdf_index, load_index
from .models import User, Course, Pdf, ChatEntry , University   
from . import db
import base64
import json
import traceback
import os

main = Blueprint('main', __name__)

# Routes
@main.route('/')
def index():
    courses = Course.query.all()  
    print("Courses")
    print(courses)
    return render_template('index.html', courses=courses)


@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if not username or not password:
            flash('Username and password required.')
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
            flash('Logged in successfully.')
            
            # Assuming a super admin check with hardcoded username (not recommended for production)
            if user.id == 1:
                flash("Super Admin logged in.")  # Just an example, adjust based on your actual logic
                return render_template('superadmin.html')  # Assuming you have a separate template for super admin
            else:
                return redirect(url_for('main.admin'))  # Redirect to a general admin page or dashboard
                
        else:
            flash('Invalid username or password.')
    return render_template('login.html', form=form)



@main.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))

@main.route('/admin')
#@login_required
def admin():
    user_id = session.get('user_id')
    if user_id is None:
        return "Not logged in", 401
    user = User.query.get(user_id)
    if user is None:
        return "User not found", 404
    if user_id == 1:
        universities = University.query.all()
        courses = Course.query.all()
        return render_template('superadmin.html', universities=universities, courses = courses)
    courses = Course.query.filter_by(user_id=user_id).all()
    return render_template('admin.html', courses=courses)


@main.route('/superadmin')
#@login_required
def superadmin():
    user_id = session.get('user_id')
    if user_id is None:
       return "Not logged in", 401
    user = User.query.get(user_id)
    if user is None:
       return "User not found", 404
    if user_id != 2:
       return "Not authorized", 403
    universities = University.query.all()
    courses = Course.query.all()
    return render_template('superadmin.html', universities=universities, courses = courses)


@main.route('/add_university', methods=['POST'])
#@login_required
def add_university():
    name = request.form.get('university_name')
    if current_user is not None:
        new_university = University(name = name)
        db.session.add(new_university)
        db.session.commit()
    else: print("Not logged in")
    return redirect(url_for('main.superadmin'))

@main.route('/add_user', methods=['POST'])
# @login_required
def add_user():
    university_id = request.form['university']
    username = request.form.get('user_name')
    password_hash = request.form.get('password')
    new_user = User(username=username, password_hash=password_hash, university_id=university_id)
    db.session.add(new_user)
    db.session.commit()
    flash('User added successfully', 'success')
    return redirect(url_for('main.superadmin'))

 

@main.route('/add_course', methods=['POST'])
#@login_required
def add_course():
    user_id = session.get('user_id')
    if user_id is None:
        return "Not logged in", 401
    user = User.query.get(user_id)
    if user is None:
        return "User not found", 404
    title = request.form.get('title')
    password_hash = request.form.get('course_password')
    api_key = request.form.get('api_key')
    university_id = user.university_id
    new_course = Course(title=title, university_id=university_id, password_hash=password_hash, api_key=api_key, user_id=user_id)
    db.session.add(new_course)
    db.session.commit()
    return redirect(url_for('main.admin'))

@main.route('/delete_course', methods=['POST'])
#@login_required
def delete_course():
    user_id = session.get('user_id')
    if user_id is None:
        return "Not logged in", 401
    user = User.query.get(user_id)
    if user is None:
        return "User not found", 404
    course_id = request.form['course_del'] 
    course = Course.query.get(course_id)
    if course:
        db.session.query(Pdf).filter_by(course_id=course_id).delete()
        db.session.delete(course)
        db.session.commit()
        #TODO add cleanup for index 
    return redirect(url_for('main.admin'))

@main.route('/course_overview/<int:course_id>')
@login_required
def course_overview(course_id):
    course = Course.query.get_or_404(course_id)

    # Ensure the current user is the creator of the course
    if course.user_id != current_user.id:
        abort(403)

    # Query for PDFs associated with this course
    pdfs = Pdf.query.filter_by(course_id=course_id).all()

    return render_template('course_overview.html', course=course, pdfs=pdfs)


@main.route('/upload_pdf', methods=['POST'])
# @login_required
def upload_pdf():
    try:
        if 'pdf' not in request.files:
            flash('No file part', 'danger')
            return redirect(url_for('main.admin'))

        file = request.files['pdf']
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(url_for('main.admin'))

        if file and allowed_file(file.filename):
            pdf_data = file.read()
            course_id = request.form['course']  
            pdf_id = Pdf.query.count() + 1
            add_pdf_index(pdf_id, pdf_data)
            #add_course_index(course_id, pdf_data)
            new_pdf = Pdf(title=file.filename, data=pdf_data, course_id=course_id)
            db.session.add(new_pdf)
            db.session.commit()
            flash('PDF uploaded successfully', 'success')
            return redirect(url_for('main.admin'))
        else:
            flash('Invalid file type', 'danger')
            return redirect(url_for('main.admin'))

    except Exception as e:
        flash(f'An error occurred: {e}', 'danger')
        return redirect(url_for('main.admin'))

 
@main.route('/course/<int:course_id>', methods=['GET', 'POST'])
def course_details(course_id):
    course = Course.query.get_or_404(course_id)
    form = PasswordForm()
    if form.validate_on_submit():
        # Assuming you store hashed passwords in 'password_hash'
        if course.password_hash == form.password.data:
            pdfs = Pdf.query.filter_by(course_id=course_id).all()
            return render_template('course_details.html', course=course, pdfs=pdfs, form=form)
        else:
            flash('Incorrect password. Please try again.', 'danger')
    return render_template('verify_password.html', form=form, course_id=course_id)

@main.route('/pdf/<int:pdf_id>')#TODO also add course_id
def pdf_details(pdf_id):
    pdf = Pdf.query.get_or_404(pdf_id)
    pdf_data_base64 = base64.b64encode(pdf.data).decode('utf-8')
    entries = ChatEntry.query.filter_by(pdf_id=pdf_id).all()
    return render_template('pdf_details.html', pdf_id=pdf_id, pdf_title = pdf.title, pdf_data_base64=pdf_data_base64, entries=entries)


@main.route('/log_chat_entry', methods=['POST'])
def log_chat_entry():
    # Get the data from the request
    data = request.get_json()
    question = data.get('question')
    answer = data.get('answer')
    page_number = data.get('page_number')
    pdf_id = data.get('pdf_id')
    # Create a new ChatEntry instance
    chat_entry = ChatEntry(
        question=question,
        answer=answer,
        page_number=page_number,
        pdf_id=pdf_id
    )
    db.session.add(chat_entry)
    db.session.commit()
    return jsonify({'status': 'success', 'message': 'Chat entry logged successfully'}),  200

def get_pdf_data_from_db(pdf_id):
    pdf = db.session.query(Pdf).filter_by(id=pdf_id).first()
    return pdf.data if pdf else None

@main.route('/get_answer', methods=['POST'])
def get_answer():
    try: 
        print("Entered routes: get_answer")
        # Extract data from the request
        data = request.get_json()
        question = data.get('question')
        pdf_id = data.get('pdf_id')
        page_number = data.get('page_number')
        print(f"Question: {question}")
        print(f"Pdf_Id: {pdf_id}")
        # Get the answer
        #answer = ask_pdf(question, pdf_id)
        answer = get_static_answer()
        #TODO add page numbers
        if answer:
            new_entry = ChatEntry(question=question, answer=answer, page_number=page_number, pdf_id=pdf_id)
            db.session.add(new_entry)
            db.session.commit()
            print("ChatEntry logged succesfully")
        else: 
            print("No answer found")    
        return jsonify({'answer': answer})
    except Exception as e:
        print(f"Error in routes: get_answer: {e}")

def get_static_answer():
    return "This is a static answer to your question."

@main.route('/download-pdf-entries/<int:pdf_id>')
def download_pdf_entries(pdf_id):
    try:
        # Use SQLAlchemy to fetch the entries directly from the database
        entries_query = ChatEntry.query.filter_by(pdf_id=pdf_id).all()

        # Transform the SQLAlchemy objects into a list of dictionaries
        entries = [
            {
                'page_number': entry.page_number, 
                'question': entry.question, 
                'answer': entry.answer
            } for entry in entries_query
        ]

        # Convert entries to a pandas DataFrame
        df = pd.DataFrame(entries)

        # Create a BytesIO buffer to save the Excel file
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='PDF Entries')

        # Rewind the buffer
        output.seek(0)

        # Create a response object with the Excel file content
        response = Response(output.getvalue(), mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        
        # Set headers to prompt for download with a specific filename
        response.headers['Content-Disposition'] = f'attachment; filename=entries_{pdf_id}.xlsx'

        return response
    except Exception as e:
        # If anything goes wrong, print the error message and return a 500 response
        print(f"Error generating Excel file: {e}")
        return Response("Error generating Excel file", status=500)

########################################################Debugging############################################

@main.errorhandler(403)
def forbidden(error):
    return render_template('403.html'), 403
