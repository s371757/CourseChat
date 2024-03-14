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
import os.path
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage,
)
import os
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import Settings



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
    Settings.llm = Ollama(model="llama2", request_timeout=60.0)
    Settings.embed_model = HuggingFaceEmbedding(
    model_name="BAAI/bge-small-en-v1.5"
    )
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
    base_path = "./chroma_db" 
    index_name = "Kurs" + course_id # Adjust this path to where your indexes are stored
    index_path = os.path.join(base_path, index_name)
    # Check if the directory for this index exists
    if os.path.isdir(index_path):
        print(f"There exists a index associated with course ID {course_id}.")
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
        coursetitle ="Kurs"+ course_id
        print(coursetitle)
        chroma_collection = db.get_or_create_collection(coursetitle)
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
        coursetitle = "Kurs" +course_id
        index = load_index(coursetitle)
        print(index)
        for document in documents:
            index.insert(document) 
        print("Successfully added to index")
        return index
    except Exception as e:
        print(f"Error in add_to_index: {e}")


    # Either way we can now query the index
    query_engine = index.as_query_engine()
    response = query_engine.query("What is the paper about?")
    print(response)
    return response

