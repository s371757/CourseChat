import os
__author__ = "Julia Wenkmann"

def allowed_file(filename):
    return filename.lower().endswith('.pdf')


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',  1)[1].lower() in {'pdf'}



def set_api_key(api_key: str):
    os.environ["OPENAI_API_KEY"] = api_key