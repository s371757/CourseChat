import os

def allowed_file(filename):
    return filename.lower().endswith('.pdf')

def check_password_hash(hashed_password, password):
    return hashed_password == password

def load_pdf_to_data(pdf_data: bytes):
    print("[INFO]: Loading PDF to data")
    # Get the directory of the current script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    folder_path = os.path.join(current_dir, 'data')
    # Create the data folder if it doesn't exist
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    # Save the PDF data to a file in the data folder
    file_path = os.path.join(folder_path, 'tempfile.pdf')
    with open(file_path, 'wb') as file:
        file.write(pdf_data)
    print("[INFO]: PDF saved to data folder")
    return True


def clear_data():
    print("[INFO]: Clearing data")
    # Get the directory of the current script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    folder_path = os.path.join(current_dir, 'data')
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)
        elif os.path.isdir(file_path):
            os.rmdir(file_path)
    print("[INFO]: Data in folder deleted")
    return True

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',  1)[1].lower() in {'pdf'}

def set_api_key(api_key: str):
    os.environ['OPENAI_API_KEY'] = api_key
    print("[INFO]: API key set")
    return True 