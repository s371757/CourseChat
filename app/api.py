import os
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
import logging
import sys
import chromadb
from llama_index.core import VectorStoreIndex
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import StorageContext
from . import db
from .models import Course, Pdf
from .utils import clear_data, load_pdf_to_data

#TODO: Add the OpenAI API key to the environment variables depending on the course ID 
def load_openai_key() -> str:
    key = os.environ.get("OPENAI_API_KEY")
    if key is None:
        key = os.environ.get("OPENAI_API_KEY")
        if key is None:
            raise ValueError(
                "[ERROR]:  OPENAI_API_KEY"
            )
    return key


def ask_course(course_id: str, question: str):
    print("Asking course")
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))
    course = Course.query.get(course_id)
    course_title = course.title
    index = load_index(course_title)
    print(index)
    query_engine = index.as_query_engine()
    response = query_engine.query(question)
    print(response)
    return response

def ask_file(pdf_id: str, question: str) -> str:
    print("Asking file")
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))
    index = load_index(pdf_id)
    query_engine = index.as_query_engine()
    response = query_engine.query(question)
    print(response)
    return response

def load_index(id: str) -> VectorStoreIndex:
    # initialize client
    db = chromadb.PersistentClient(path="./chroma_db")

    # get collection
    chroma_collection = db.get_or_create_collection(id)

    # assign chroma as the vector_store to the context
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    # load your index from stored vectors
    index = VectorStoreIndex.from_vector_store(
        vector_store, storage_context=storage_context
    )
    return index

def add_pdf_index(course_id: str, pdf_data: str):
    clear_data()
    load_pdf_to_data(pdf_data)
    if was_initialized(course_id):
        print(f"Adding to index for course ID {course_id}")
        index = add_to_index(course_id)
    else:
        print(f"Creating index for course ID {course_id}")
        index = create_index(course_id)
    return index

def was_initialized(course_id: str) -> bool:
    pdfs = Pdf.query.filter_by(course_id=course_id).all()
    # Check if any PDFs were found 
    #TODO potential error
    if pdfs:
        print(f"There are {len(pdfs)} PDF(s) associated with course ID {course_id}.")
        return True
    else:
        print(f"No PDFs are associated with course ID {course_id}.")
        return False# Replace this with your implementation

def create_index(course_id: str):
    print("Entered create_index")
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        folder_path = os.path.join(current_dir, 'data')
        documents = SimpleDirectoryReader(folder_path).load_data()
        # initialize client, setting path to save data
        db = chromadb.PersistentClient(path="./chroma_db")
        # create collection
        course = Course.query.get(course_id)
        course_title = course.title
        chroma_collection = db.get_or_create_collection(course_title)
        print(chroma_collection)
        # assign chroma as the vector_store to the context
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)

        # create your index
        index = VectorStoreIndex.from_documents(
            documents, storage_context=storage_context
        )
        print("Index:")
        print(index)
        return index
    except Exception as e:
        print(f"Error in create_index: {e}")


def add_to_index(course_id: str):
    try: 
        current_dir = os.path.dirname(os.path.abspath(__file__))
        folder_path = os.path.join(current_dir, 'data')
        documents = SimpleDirectoryReader(folder_path).load_data()
        course = Course.query.get(course_id)
        course_title = course.title
        index = load_index(course_title)
        print(index)
        for document in documents:
            index.insert(document) 
        print("Successfully added to index")
        return index
    except Exception as e:
        print(f"Error in add_to_index: {e}")

