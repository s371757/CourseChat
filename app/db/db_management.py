__author__ = "Julia Wenkmann"
from .models import User, Course, Pdf, ChatEntry , University   
from .db_setup import db
from ..llama_index.indexing import delete_pdf_index, delete_course_index

def check_superadmin(user_id):
    if user_id is None:
       return "Not logged in", 401
    user = User.query.get(user_id)
    if user is None:
       return "User not found", 404
    if user_id != 1:
       return "Not authorized", 403
    
def check_admin(user_id):
    if user_id is None:
        return "Not logged in", 401
    user = User.query.get(user_id)
    if user is None:
        return "User not found", 404
    


def delete_university_by_id(university_id):
    university = University.query.get(university_id)
    if university: 
        users =User.query.filter_by(university_id=university.id).all()
        for user in users: 
            delete_user_by_id(user.id)
        db.session.delete(university)
        db.session.commit()

def delete_user_by_id(user_id):
    user = User.query.get(user_id)
    if user:
        courses = db.session.query(Course).filter_by(user_id=user_id)
        for course in courses:
            delete_course_by_id(course.id)
        db.session.delete(user)
        db.session.commit()
    

def delete_course_by_id(course_id):
    course = Course.query.get(course_id)
    if course: 
        pdfs = db.session.query(Pdf).filter_by(course_id=course.id)
        for pdf in pdfs:
            delete_pdf_by_id(pdf.id)
        delete_course_index(course_id, pdfs)
        db.session.delete(course)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               
                                                                                                                                                                                                                                                                                                                                                                         
        db.session.commit()

def delete_pdf_by_id(pdf_id):
    pdf = Pdf.query.get(pdf_id)
    if pdf: 
        db.session.query(ChatEntry).filter_by(pdf_id=pdf_id).delete()
        db.session.delete(pdf)
        delete_pdf_index(pdf.id)
        db.session.commit()