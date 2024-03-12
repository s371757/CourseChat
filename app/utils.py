def allowed_file(filename):
    return filename.lower().endswith('.pdf')

def check_password_hash(hashed_password, password):
    return True

def load_pdf_to_data(pdf_id: str):
    print("[INFO]: Loading PDF to data")

    return True


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',  1)[1].lower() in {'pdf'}