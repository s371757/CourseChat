# routes.py
from flask import Blueprint, render_template, request, flash, redirect, url_for, Response, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user

from .forms import LoginForm 
from .utils import allowed_file, check_password_hash, load_pdf_to_data
from .api import ask_file, ask_course, add_pdf_index
from .models import User, Course, Pdf, ChatEntry , University   
from . import db
import base64

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
        if user is not None and not check_password_hash(user.password_hash, form.password.data):
            flash('Invalid username or password.')
            print("Invalid password")
            return redirect(url_for('main.login'))
        if user is not None and check_password_hash(user.password_hash, form.password.data):
            session['user_id'] = user.id
            flash('Logged in successfully.')
            if user == "admin" and user.password == "admin":
                print("Super Admin")
                return render_template('superadmin.html')
            else: return redirect(url_for('main.admin'))
        else:
            flash('Invalid username or password.')
    return render_template('login.html', form=form)         



@main.route('/logout')
#@login_required
def logout():#TODO
    logout_user()
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
    if user_id == 2:
        universities = University.query.all()
        courses = Course.query.all()
        return render_template('superadmin.html', universities=universities, courses = courses)
    courses = Course.query.all()
    return render_template('admin.html', courses=courses)

@main.route('/superadmin')
#@login_required
def superadmin():
    user_id = session.get('user_id')
    #if user_id is None:
    #    return "Not logged in", 401
    #user = User.query.get(user_id)
    #if user is None:
    #    return "User not found", 404
    #if user_id != 2:
    #    return "Not authorized", 403
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
            #add_pdf_index(course_id, pdf_data)
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

 

@main.route('/course/<int:course_id>')
def course_details(course_id):
    course = Course.query.get_or_404(course_id)
    pdfs = Pdf.query.filter_by(course_id=course_id).all()
    return render_template('course_details.html', course=course, pdfs=pdfs)


@main.route('/pdf/<int:pdf_id>')#TODO also add course_id
def pdf_details(pdf_id):
    pdf = Pdf.query.get_or_404(pdf_id)
    pdf_data_base64 = base64.b64encode(pdf.data).decode('utf-8')
    entries = ChatEntry.query.filter_by(pdf_id=pdf_id).all()
    return render_template('pdf_details.html', pdf_title = pdf.title, pdf_data_base64=pdf_data_base64, entries=entries)


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
        print("Getting answer")
        # Extract data from the request
        data = request.get_json()
        question = data.get('question')
        pdf_id = data.get('pdf_id')
        course_id = data.get('course_id')
        user_id = session.get('user_id')
        print(f"Question: {question}")
        print(f"PDF ID: {pdf_id}")
        print(f"Course ID: {course_id}")
        # Get the answer
        #answer = ask_course(course_id, question)
        answer = get_static_answer()

        #TODO implement logging
        #TODO add page numbers
        new_entry = ChatEntry(question=question, answer=answer, page_number=1, pdf_id=pdf_id)
        db.session.add(new_entry)
        db.session.commit()
        print("ChatEntry logged succesfully")
        return jsonify({'answer': answer})
    except Exception as e:
        print(f"Error in get_answer: {e}")

def get_static_answer():
    return "This is a static answer to your question."

########################################################Debugging############################################

@main.route('/chat')
#@login_required
def chat():
    pdf_id = 1,
    course_id = 1
    return render_template('chat.html', pdf_id = pdf_id, course_id = course_id)