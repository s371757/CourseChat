# routes.py
from flask import Blueprint, render_template, request, flash, redirect, url_for, Response, session, abort
from flask_login import login_required, current_user
import pandas as pd
from io import BytesIO

from ..db.db_management import check_superadmin, check_admin, delete_course_by_id, delete_user_by_id, delete_pdf_by_id, delete_university_by_id
from ..utils import allowed_file
from ..llama_index.indexing import create_index
from ..db.models import User, Course, Pdf, ChatEntry , University   
from ..db.db_setup import db
from flask import jsonify

__author__ = "Julia Wenkmann"

admin = Blueprint('admin', __name__)

ADMIN_URL = 'admin.admin_page'
SUPERADMIN_URL = 'admin.superadmin_page'



# Routes
@admin.route('/admin')
@login_required
def admin_page():
    user_id = session.get('user_id')
    check_admin(user_id)
    courses = Course.query.filter_by(user_id=user_id).all()
    pdfs_by_course = {}
    for course in courses:
        pdfs = Pdf.query.filter_by(course_id=course.id).all()
        pdfs_by_course[course.id] = [(pdf.id, pdf.title) for pdf in pdfs]
    return render_template('admin.html', courses=courses, pdfs_by_course=pdfs_by_course)


@admin.route('/superadmin')
@login_required
def superadmin_page():
    user_id = session.get('user_id')
    check_superadmin(user_id)
    universities = University.query.all()
    courses = Course.query.all()
    users = User.query.all()
    return render_template('superadmin.html', universities=universities, courses = courses, users = users)


@admin.route('/add_university', methods=['POST'])
@login_required
def add_university():
    user_id = session.get('user_id')
    check_superadmin(user_id)
    name = request.form.get('university_name')
    if current_user is not None:
        new_university = University(name = name)
        db.session.add(new_university)
        db.session.commit()
    else: print("Not logged in")
    return redirect(url_for(SUPERADMIN_URL))


@admin.route('/delete_university', methods=['POST'])
@login_required
def delete_university():
    user_id = session.get('user_id')
    check_superadmin(user_id)
    university_id = request.form['del_university'] 
    delete_university_by_id(university_id)
    return redirect(url_for(SUPERADMIN_URL))

@admin.route('/add_user', methods=['POST'])
@login_required
def add_user():
    user_id = session.get('user_id')
    check_superadmin(user_id)
    university_id = request.form['university']
    username = request.form.get('user_name')
    password_hash = request.form.get('password')
    new_user = User(username=username, password_hash=password_hash, university_id=university_id)
    db.session.add(new_user)
    db.session.commit()
    return redirect(url_for(SUPERADMIN_URL))


@admin.route('/delete_user', methods=['POST'])
@login_required
def delete_user():
    user_id = session.get('user_id')
    check_superadmin(user_id)
    user_id_to_delete = request.form['del_user'] 
    delete_user_by_id(user_id_to_delete)
    return redirect(url_for(SUPERADMIN_URL))


@admin.route('/add_course', methods=['POST'])
@login_required
def add_course():
    user_id = session.get('user_id')
    check_admin(user_id)
    print(f"User_id: {user_id}")
    user = User.query.get(user_id)
    title = request.form.get('title')
    password_hash = request.form.get('course_password')
    api_key = request.form.get('api_key')
    university_id = user.university_id
    new_course = Course(title=title, university_id=university_id, password_hash=password_hash, api_key=api_key, user_id=user_id)
    db.session.add(new_course)
    db.session.commit()
    return redirect(url_for(ADMIN_URL))


@admin.route('/delete_course', methods=['POST'])
@login_required
def delete_course():
    user_id = session.get('user_id')
    check_admin(user_id)
    course_id = request.form['course_del'] 
    delete_course_by_id(course_id)
    return redirect(url_for(ADMIN_URL))


@admin.route('/upload_pdf', methods=['POST'])
@login_required
def upload_pdf():
    print("Entered upload_pdf function")
    try:
        if 'pdf' not in request.files:
            return redirect(url_for(ADMIN_URL))
        file = request.files['pdf']
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(url_for(ADMIN_URL))
        if file and allowed_file(file.filename):
            pdf_data = file.read()
            course_id = request.form['course']  
            pdf_id = Pdf.query.count() + 1
            new_pdf = Pdf(title=file.filename, data=pdf_data, course_id=course_id)
            db.session.add(new_pdf)
            db.session.commit()
            print(f"PDF uploaded successfully for course ID: {course_id}")
            api_key = Course.query.get(course_id).api_key
            new_course = check_new_course(course_id)
            print(f"New course created: {new_course}")
            create_index(course_id, pdf_id, pdf_data, api_key, new_course)
            flash('PDF uploaded successfully', 'success')
            return redirect(url_for(ADMIN_URL))
        else:
            flash('Invalid file type', 'danger')
            return redirect(url_for(ADMIN_URL))
    except Exception as e:
        flash(f'An error occurred: {e}', 'danger')
        return redirect(url_for(ADMIN_URL))


@admin.route('/delete_pdf', methods=['POST'])
@login_required
def delete_pdf():
    user_id = session.get('user_id')
    check_admin(user_id)
    pdf_id = request.form['pdf_del'] 
    delete_pdf_by_id(pdf_id)
    return redirect(url_for(ADMIN_URL))


@admin.route('/get_pdfs/<int:course_id>', methods=['GET'], strict_slashes=False)
@login_required
def get_pdfs(course_id):
    pdfs = Pdf.query.filter_by(course_id=course_id).all()
    pdfs_list = [(pdf.id, pdf.title) for pdf in pdfs]
    return jsonify(pdfs_list)


@admin.route('/course_logging/<int:course_id>')
@login_required
def course_logging(course_id):
    user_id = session.get('user_id')
    check_admin(user_id)
    course = Course.query.get_or_404(course_id)
    # Ensure the current user is the creator of the course
    if course.user_id != current_user.id:
        abort(403)
    # Query for PDFs associated with this course
    pdfs = Pdf.query.filter_by(course_id=course_id).all()
    return render_template('course_chat_entries.html', course=course, pdfs=pdfs)


@admin.route('/download-pdf-entries/<int:pdf_id>')
def download_pdf_entries(pdf_id):
    user_id = session.get('user_id')
    check_admin(user_id)
    try:
        entries_query = ChatEntry.query.filter_by(pdf_id=pdf_id).all()
        # Transform the SQLAlchemy objects into a list of dictionaries
        entries = [
            {
                'page_number': entry.page_number, 
                'question': entry.question, 
                'answer': entry.answer
            } for entry in entries_query
        ]
        df = pd.DataFrame(entries)
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


@admin.errorhandler(403)
def forbidden(error):
    return render_template('403.html'), 403


def get_pdf_data_from_db(pdf_id):
    pdf = db.session.query(Pdf).filter_by(id=pdf_id).first()
    return pdf.data if pdf else None


def check_new_course(course_id):
    num_pdfs_of_course = Pdf.query.filter_by(course_id=course_id).count()
    if num_pdfs_of_course == 0: 
        new_course = True
    else: 
        new_course = False
    return new_course