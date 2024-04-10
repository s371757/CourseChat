import os.path
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage,
    Settings,
)
import os
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import logging
import sys
import chromadb
from llama_index.vector_stores.chroma import ChromaVectorStore
from app.llama_index.questioning import add_course_index, ask_course

def load_index(id: str) -> VectorStoreIndex:    
    courseindex = "Index" +id
    db = chromadb.PersistentClient(path="./index_db")
    chroma_collection = db.get_or_create_collection(courseindex)
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    index = VectorStoreIndex.from_vector_store(
        vector_store, storage_context=storage_context
    )
    return index


def add_pdf_index(course_id: str):
    Settings.llm = Ollama(model="llama2", request_timeout=60.0)
    Settings.embed_model = HuggingFaceEmbedding(
    model_name="BAAI/bge-small-en-v1.5"
    )
    if load_index(course_id):
        print(f"Adding to index for course ID {course_id}")
        index = add_to_index(course_id)
    else:
        print(f"Creating index for course ID {course_id}")
        index = create_index(course_id)
    return index

def create_index(course_id: str):
    print("Entered create_index")
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        folder_path = os.path.join(current_dir, 'app/data')
        documents = SimpleDirectoryReader(folder_path).load_data()
        # initialize client, setting path to save data
        db = chromadb.PersistentClient(path="./index_db")
        # create collection
        courseindex ="Index"+ course_id
        chroma_collection = db.get_or_create_collection(courseindex)
        # assign chroma as the vector_store to the context
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        index = VectorStoreIndex.from_documents(
            documents, storage_context=storage_context
        )
        print("Cretaed Index:")
        print(index)
        return index
    except Exception as e:
        print(f"Error in create_index: {e}")


def add_to_index(course_id: str):
    try: 
        current_dir = os.path.dirname(os.path.abspath(__file__))
        folder_path = os.path.join(current_dir, 'app/data')
        documents = SimpleDirectoryReader(folder_path).load_data()
        index = load_index(course_id)
        for document in documents:
            index.insert(document) 
        print("Successfully added to index")
        return index
    except Exception as e:
        print(f"Error in add_to_index: {e}")


def ask_pdf(pdf_id: str, question: str):
    print("Asking course")
    Settings.llm = Ollama(model="llama2", request_timeout=20000.0)
    Settings.embed_model = HuggingFaceEmbedding(
    model_name="BAAI/bge-small-en-v1.5"
    )
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))
    index = load_index(pdf_id)
    print(f"Successfully loaded {index}")
    query_engine = index.as_query_engine()
    response = query_engine.query(question)
    print(response)
    return response


if __name__ == "__main__":
    #add_pdf_index("1234")
    #print("Done")   
    #ask_pdf("17", "Warum Videos?")
    add_course_index("1")
    ask_course("1", "Worum geht es in diesem Kurs?")
    print("Done")