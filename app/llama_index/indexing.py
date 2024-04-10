import os.path
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
)
import os
from flask import current_app
import chromadb
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import StorageContext, VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.extractors import (
    SummaryExtractor,
    QuestionsAnsweredExtractor,
    TitleExtractor,
    KeywordExtractor,
)
from llama_index.extractors.entity import EntityExtractor
from llama_index.core.ingestion import IngestionPipeline
from flask import current_app
from ..utils import set_api_key
from ..db.models import Course, Pdf

transformations = [
    SentenceSplitter(),
    TitleExtractor(nodes=5),
    QuestionsAnsweredExtractor(questions=3),
    SummaryExtractor(summaries=["prev", "self"]),
    KeywordExtractor(keywords=10),
    EntityExtractor(prediction_threshold=0.5),
]

__author__ = "Julia Wenkmann"



def create_index(course_id: str, pdf_id: str, pdf_data, api_key: str, new_course: bool = False) -> VectorStoreIndex:
    print("Entered create_index")
    try:
        with current_app.app_context():
            set_api_key(api_key)
            clear_data()
            load_pdf_to_data(pdf_data)
            document = load_documents()
            if new_course:
                course_index = create_course_index(course_id, document)
            pdf_index = create_pdf_index(pdf_id, document)
            course_index = add_to_course_index(course_id, document, pdf_index)
            return course_index, pdf_index
    except Exception as e:
        print(f"Error in create_index: {e}")


def create_course_index(course_id: str, documents):
    try: 
        with current_app.app_context():
            #print(documents)
            pipeline = IngestionPipeline(transformations=transformations)
            print("Pipeline created uccesfully")
            nodes = pipeline.run(documents=documents)
            print("Nodes created succesfully")
            print(nodes[0].metadata)
            storage_context = prepare_storage("Kurs" + str(course_id))
            print("Successfully created storage context")
            index = VectorStoreIndex(nodes=nodes, storage_context=storage_context)
            #index = VectorStoreIndex.from_documents(documents, storage_context=storage_context)
            print("Successfully created course index")
            return index
    
    except Exception as e:
        current_app.logger.error(f"Error creating index: {e}")



def create_pdf_index(pdf_id: str, documents):
    print(f"Creating index for pdf ID {pdf_id}")
    storage_context = prepare_storage("Pdf" + str(pdf_id))
    index = VectorStoreIndex.from_documents(documents, storage_context=storage_context)
    return index

def add_to_course_index(course_id: str, document, pdf_index: VectorStoreIndex):#TODO: add adding of meta-data
    try: 
        documents = load_documents()
        course_index = load_index(course_id)
        for document in documents:
            course_index.insert(document) 
        print("Successfully added to index")
        return course_index
    except Exception as e:
        print(f"Error in add_to_index: {e}")


def load_documents():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    folder_path = os.path.join(current_dir, 'data')
    documents = SimpleDirectoryReader(folder_path).load_data()
    return documents


def load_pdf_to_data(pdf_data: bytes):
    print("[INFO]: Loading PDF to data")
    # Get the directory of the current script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    folder_path = os.path.join(current_dir, 'data')
    # Create the data folder if it doesn't exist
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    # Save the PDF data to a file in the data folder
    current_millisec = str(int(time.time() * 1000))
    file_name = 'tempfile' + current_millisec + '.pdf'
    file_path = os.path.join(folder_path, file_name)
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

def load_all_pdfs_of_course(course_id: str):
    pdfs = Pdf.query.filter_by(course_id=course_id).all()
    return pdfs

def load_index(indexname: str) -> VectorStoreIndex:    
    db = chromadb.PersistentClient(path="./index_db")
    chroma_collection = db.get_or_create_collection(indexname)
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    index = VectorStoreIndex.from_vector_store(
        vector_store, storage_context=storage_context
    )
    print(f"Index loaded for ID {id}")
    return index

def prepare_storage(id: str):
    # initialize client, setting path to save data
    db = chromadb.PersistentClient(path="./index_db")
    # create collection
    index_id = "Index" + str(id)
    chroma_collection = db.get_or_create_collection(index_id)
    # assign chroma as the vector_store to the context
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    return storage_context

def delete_course_index(course_id, pdfs):
    db = chromadb.PersistentClient(path="./index_db")
    course_id = "Index" + "Kurs" + str(course_id)
    chroma_collection = db.get_or_create_collection(course_id)
    chroma_collection.delete(ids=course_id)
    for pdf in pdfs:
        delete_pdf_index(pdf.id)

def delete_pdf_index(pdf_id): 
    db = chromadb.PersistentClient(path="./index_db")
    index_id = "Index" + str(id)
    chroma_collection = db.get_or_create_collection(index_id)
    chroma_collection.delete(ids=pdf_id)
