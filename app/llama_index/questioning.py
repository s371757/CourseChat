__author__ = "Julia Wenkmann"
import logging
import sys
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.extractors import (
    SummaryExtractor,
    QuestionsAnsweredExtractor,
    TitleExtractor,
    KeywordExtractor,
)
from llama_index.extractors.entity import EntityExtractor

transformations = [
    SentenceSplitter(),
    TitleExtractor(nodes=5),
    QuestionsAnsweredExtractor(questions=3),
    SummaryExtractor(summaries=["prev", "self"]),
    KeywordExtractor(keywords=10),
    EntityExtractor(prediction_threshold=0.5),
]
from .indexing import load_index
from ..utils import set_api_key



def ask_pdf(question: str, pdf_id: str, api_key: str) -> str:
    print("Asking Pdf")
    set_api_key(api_key)
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))
    index = load_index("Pdf" + str(pdf_id))
    query_engine = index.as_query_engine()
    response = query_engine.query(question)
    print(response)
    return response


def ask_course(question: str, course_id: str, api_key: str) -> str:
    print("Asking course")
    set_api_key(api_key)
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))
    index = load_index("Kurs" + str(course_id))
    query_engine = index.as_query_engine()
    response = query_engine.query(question)
    print(response)
    return response

