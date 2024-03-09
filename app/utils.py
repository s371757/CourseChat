import os
from werkzeug.security import check_password_hash

def allowed_file(filename):
    return filename.lower().endswith('.pdf')

def check_password_hash(hashed_password, password):
    return check_password_hash(hashed_password, password)