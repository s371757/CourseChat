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
from .utils import clear_data, load_pdf_to_data, set_api_key
from llama_index.core import StorageContext, VectorStoreIndex

def load_index(id: str) -> VectorStoreIndex:    
    courseindex = "Index" +str(id)
    db = chromadb.PersistentClient(path="./index_db")
    chroma_collection = db.get_or_create_collection(courseindex)
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    index = VectorStoreIndex.from_vector_store(
        vector_store, storage_context=storage_context
    )
    print(f"Index loaded for ID {id}")
    return index



def add_pdf_index(pdf_id: str, pdf_data):
    Settings.llm = Ollama(model="llama2", request_timeout=60.0)
    Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
    clear_data()
    load_pdf_to_data(pdf_data)
    if False:
        print(f"Adding to index for pdf ID {pdf_id}")
        index = add_to_index(pdf_id)
    else:
        print(f"Creating index for pdf ID {pdf_id}")
        index = create_index(pdf_id)
    return index

def create_index(id: str):
    print("Entered create_index")
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        folder_path = os.path.join(current_dir, 'data')
        documents = SimpleDirectoryReader(folder_path).load_data()
        # initialize client, setting path to save data
        db = chromadb.PersistentClient(path="./index_db")
        # create collection
        courseindex = "Index" + str(id)
        chroma_collection = db.get_or_create_collection(courseindex)
        # assign chroma as the vector_store to the context
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        index = VectorStoreIndex.from_documents(
            documents, storage_context=storage_context
        )
        print("Successfully created index")
        return index
    except Exception as e:
        print(f"Error in create_index: {e}")


def add_to_index(id: str):
    try: 
        current_dir = os.path.dirname(os.path.abspath(__file__))
        folder_path = os.path.join(current_dir, 'data')
        documents = SimpleDirectoryReader(folder_path).load_data()
        index = load_index(id)
        for document in documents:
            index.insert(document) 
        print("Successfully added to index")
        return index
    except Exception as e:
        print(f"Error in add_to_index: {e}")


def ask_pdf(question: str, id: str) -> str:
    print("Asking course")
    Settings.llm = Ollama(model="llama2", request_timeout=200.0)
    Settings.embed_model = HuggingFaceEmbedding(
    model_name="BAAI/bge-small-en-v1.5"
    )
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))
    index = load_index(id)
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

