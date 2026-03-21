# knowledge/retriever.py — Layer 3: RAG Query Engine (fully local)
import os
import chromadb
from llama_index.core import VectorStoreIndex, Settings
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

from runtime.config.settings import CHROMA_PATH

Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
Settings.llm = None

# Minimum similarity score — below this we say "no relevant notes found"
SIMILARITY_THRESHOLD = 0.5


def query(question: str) -> str:
    if not os.path.exists(CHROMA_PATH):
        return "empty"

    try:
        client       = chromadb.PersistentClient(path=CHROMA_PATH)
        collection   = client.get_or_create_collection("sameer_knowledge")

        if collection.count() == 0:
            return "empty"

        vector_store = ChromaVectorStore(chroma_collection=collection)
        index        = VectorStoreIndex.from_vector_store(vector_store)

        retriever = VectorIndexRetriever(
            index=index,
            similarity_top_k=1
        )
        nodes = retriever.retrieve(question)

        if not nodes:
            return "empty"

        # Check similarity score — reject irrelevant results
        top_node = nodes[0]
        score = top_node.score if top_node.score is not None else 0

        if score < SIMILARITY_THRESHOLD:
            return "empty"

        return top_node.text.strip()

    except Exception:
        return "empty"