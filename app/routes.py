# routes.py
from flask import Blueprint, render_template, request, flash, redirect, url_for, Response, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from tempfile import NamedTemporaryFile
import os

from .forms import LoginForm 
from .utils import allowed_file, check_password_hash
from .api import generate_answer, ask_file, load_openai_key, load_recommender
from .models import User, Course, Pdf, ChatEntry    
from . import db

main = Blueprint('main', __name__)

# Routes
@main.route('/')
def index():
    courses = Course.query.all()  
    return render_template('index.html', courses=courses)


@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if not username or not password:
            flash('Username and password required.')
            return redirect(url_for('register'))
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None and not check_password_hash(user.password, form.password.data):
            flash('Invalid username or password.')
            print("Invalid password")
            return redirect(url_for('login'))
        if user is not None and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('Logged in successfully.')
            return redirect(url_for('admin'))
        else:
            flash('Invalid username or password.')
    return render_template('login.html', form=form)         

@main.route('/logout')
#@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@main.route('/admin')
#@login_required
def admin():
    courses = Course.query.all()
    return render_template('admin.html', courses=courses)

@main.route('/add_course', methods=['POST'])
#@login_required
def add_course():
    title = request.form.get('title')
    if current_user is not None:
        university_id = 1 #current_user.university_id
    else: university_id = 1
    new_course = Course(title=title, university_id=university_id)
    db.session.add(new_course)
    db.session.commit()
    return redirect(url_for('admin'))


@main.route('/upload_pdf', methods=['POST'])
# @login_required
def upload_pdf():
    try:
        if 'pdf' not in request.files:
            flash('No file part', 'danger')
            return redirect(url_for('admin'))

        file = request.files['pdf']
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(url_for('admin'))

        if file and allowed_file(file.filename):
            pdf_data = file.read()
            course_id = request.form['course']  # Correct way to get course_id
            new_pdf = Pdf(title=file.filename, data=pdf_data, course_id=course_id)
            db.session.add(new_pdf)
            db.session.commit()
            flash('PDF uploaded successfully', 'success')
            return redirect(url_for('admin'))
        else:
            flash('Invalid file type', 'danger')
            return redirect(url_for('admin'))

    except Exception as e:
        flash(f'An error occurred: {e}', 'danger')
        return redirect(url_for('admin'))


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',  1)[1].lower() in {'pdf'}
 

@main.route('/course/<int:course_id>')
def course_details(course_id):
    course = Course.query.get_or_404(course_id)
    pdfs = Pdf.query.filter_by(course_id=course_id).all()
    return render_template('course_details.html', course=course, pdfs=pdfs)


@main.route('/pdf/<int:pdf_id>')
def pdf_details(pdf_id):
    pdf = Pdf.query.get_or_404(pdf_id)
    entries = ChatEntry.query.filter_by(pdf_id=pdf_id).all()
    return render_template('pdf_details.html', pdf=pdf, entries=entries)

@main.route('/serve_pdf/<int:pdf_id>')
def serve_pdf(pdf_id):
    pdf = Pdf.query.get_or_404(pdf_id)
    return Response(pdf.data, mimetype='application/pdf')

@main.route('/submit_question', methods=['POST'])
def submit_question():
    question = request.form.get('question')
    page_number = request.form.get('page_number')
    pdf_id = request.form.get('pdf_id')

    # Logic to determine the answer
    # This is a placeholder and should be replaced with your actual logic
    answer = "This is a placeholder answer."

    new_entry = ChatEntry(question=question, answer=answer, page_number=page_number, pdf_id=pdf_id, user_id=current_user.id)
    db.session.add(new_entry)
    db.session.commit()

    return redirect(url_for('show_pdf', pdf_id=pdf_id))

@main.route('/ask_url', methods=['GET'])
def ask_url_flask():
    pdf_id = request.args.get('pdf_id')
    question = request.args.get('question')
    if not id or not question:
        return jsonify({"error": "ID and question are required."}),   400
    # Retrieve the PDF data from the SQLite database using the ID
    pdf_data = get_pdf_data_from_db(pdf_id)
    if not pdf_data:
        return jsonify({"error": "ID not found in the database."}),   404
    # Save the PDF data to a temporary file
    with NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
        tmp.write(pdf_data)
        tmp_path = tmp.name
    # Process the temporary file as if it were a downloaded PDF
    load_recommender(tmp_path)
    openai_key = load_openai_key()
    answer = generate_answer(question, openai_key)
    # Clean up the temporary file
    os.remove(tmp_path)
    return answer

@main.route('/ask_file', methods=['POST'])
def ask_file_flask():
    if 'file' not in request.files:
        return "Error: No file part in the request.",  400
    file = request.files['file']
    question = request.form.get('question')
    if not file or not question:
        return "Error: File and question are required.",  400
    return ask_file(file, question)  


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
