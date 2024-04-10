# routes.py
from flask import Blueprint, render_template, request, flash, jsonify

from ..forms import PasswordForm
from ..llama_index.questioning import ask_pdf, ask_course
from ..db.models import Course, Pdf, ChatEntry
from ..db.db_setup import db
import base64
import json


__author__ = "Julia Wenkmann"

user = Blueprint('user', __name__)

# Routes
@user.route('/course/<int:course_id>', methods=['GET', 'POST'])
def course_details(course_id):
    course = Course.query.get_or_404(course_id)
    form = PasswordForm()
    if form.validate_on_submit():#TODO make that secure
        # Assuming you store hashed passwords in 'password_hash'
        if course.password_hash == form.password.data:
            pdfs = Pdf.query.filter_by(course_id=course_id).all()
            return render_template('course_details.html', course=course, pdfs=pdfs, form=form)
        else:
            flash('Incorrect password. Please try again.', 'danger')
    return render_template('verify_password.html', form=form, course_id=course_id)

@user.route('/pdf/<int:pdf_id>')
def chat_with_pdf(pdf_id):
    pdf = Pdf.query.get_or_404(pdf_id)
    api_key = pdf.course.api_key
    pdf_data_base64 = base64.b64encode(pdf.data).decode('utf-8')
    entries = ChatEntry.query.filter_by(pdf_id=pdf_id).all()
    course_id = pdf.course_id
    return render_template('chat_with_pdf.html', pdf_id=pdf_id, pdf_title = pdf.title, course_id = course_id, pdf_data_base64=pdf_data_base64, entries=entries, api_key=api_key)



@user.route('/coursechat/<int:course_id>')
def chat_with_course(course_id):
    course = Course.query.get_or_404(course_id)
    api_key = course.api_key
    pdfs = Pdf.query.filter_by(course_id=course_id).all()
    
    # Extract PDF data in base64 format for each PDF
    pdf_data_map = {}
    pdf_titles = []
    for pdf in pdfs:
        if pdf.data:
            pdf_data_base64 = base64.b64encode(pdf.data).decode('utf-8')
            pdf_data_map[pdf.id] = pdf_data_base64
            pdf_titles.append((pdf.id, pdf.title))
            print("pdf_id: ", pdf.id, ", pdf_title: ", pdf.title)
    pdf_data_json = json.dumps(pdf_data_map)
    return render_template('chat_with_course.html', course_id=course_id, pdf_titles=pdf_titles, pdf_data_json=pdf_data_json, api_key=api_key)



@user.route('/get_answer_from_pdf', methods=['POST'])
def get_answer_from_pdf():
    try: 
        print("Entered routes: get_answer_from_pdf")
        # Extract data from the request
        data = request.get_json()
        question = data.get('question')
        pdf_id = data.get('pdf_id')
        page_number = data.get('page_number')
        api_key = data.get('api_key')
        print(f"Question: {question}")
        print(f"Pdf_Id: {pdf_id}")
        # Get the answer
        answer = ask_pdf(question, pdf_id, api_key)
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



@user.route('/get_answer_from_course', methods=['POST'])
def get_answer_from_course():
    try: 
        print("Entered routes: get_answer_from_course")
        # Extract data from the request
        data = request.get_json()
        question = data.get('question')
        course_id = data.get('course_id')
        pdf_id = data.get('pdf_id')
        page_number = data.get('page_number')
        api_key = data.get('api_key')
        print(f"Question: {question}")
        print(f"Course_Id: {pdf_id}")
        print(f"Pdf_Id: {pdf_id}")
        # Get the answer
        answer = ask_course(question, course_id, api_key)
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
    test = "x^2"

    return test



@user.route('/log_chat_entry', methods=['POST'])
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


########################################################Debugging############################################

@user.errorhandler(403)
def forbidden(error):
    return render_template('403.html'), 403


def get_pdf_data_from_db(pdf_id):
    pdf = db.session.query(Pdf).filter_by(id=pdf_id).first()
    return pdf.data if pdf else None