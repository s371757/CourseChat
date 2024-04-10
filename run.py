__author__ = "Julia Wenkmann"
from app import create_app
from llama_index.core import (
    Settings,
)
from llama_index.core import Settings
from llama_index.llms.openai import OpenAI
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.embeddings.openai import OpenAIEmbedding
app = create_app()

MODEL_TYPE = "ollama"


def set_model(type: str):
    if type == "ollama":
        Settings.llm = Ollama(model="llama2", request_timeout=60.0)
        Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
    elif type == "openai":
        Settings.llm = OpenAI(temperature=0.2, model="gpt-3.5-turb")
        embed_model = OpenAIEmbedding(embed_batch_size=10)
        Settings.embed_model = embed_model


if __name__ == '__main__':
    set_model(MODEL_TYPE)
    app.run(debug=True)
