import os
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
import logging
import sys
import chromadb
from llama_index.core import VectorStoreIndex
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import StorageContext


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
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))
    index = load_index(course_id)
    query_engine = index.as_query_engine()
    response = query_engine.query(question)
    print(response)
    return response

def ask_file(pdf_id: str, question: str) -> str:
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

def add_pdf(course_id: str, pdf_id: str):
    if was_initialized(course_id):
        add_to_index(course_id, pdf_id)
    else:
        create_index(course_id, pdf_id)

def was_initialized(course_id: str) -> bool:
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM Pdf WHERE course_id = ?", (course_id,))
    pdf_ids = cursor.fetchall()

    # Check if any PDFs were found
    if pdf_ids:
        print(f"There are {len(pdf_ids)} PDF(s) associated with course ID {course_id}.")
        return True
    else:
        print(f"No PDFs are associated with course ID {course_id}.")
        return False# Replace this with your implementation

def create_index(course_id: str):
    documents = SimpleDirectoryReader("./data").load_data()

    # initialize client, setting path to save data
    db = chromadb.PersistentClient(path="./chroma_db")

    # create collection
    chroma_collection = db.get_or_create_collection(course_id)

    # assign chroma as the vector_store to the context
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    # create your index
    index = VectorStoreIndex.from_documents(
        documents, storage_context=storage_context
    )
    return index


def add_to_index(course_id: str):
    document = SimpleDirectoryReader("./data").load_data()
    index = load_index(course_id)
    index.insert(document)

