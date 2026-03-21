# knowledge/ingestor.py — Layer 3: RAG Knowledge Engine (fully local)
import os
import chromadb
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, StorageContext, Settings
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

from runtime.config.settings import CHROMA_PATH, NOTES_PATH

# Fully local — no OpenAI, no internet
Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
Settings.llm = None


def build_index():
    if not os.path.exists(NOTES_PATH):
        os.makedirs(NOTES_PATH)
        print("Created ~/Notes — add your .txt .md .pdf files there then run again.")
        return None

    try:
        documents = SimpleDirectoryReader(
            NOTES_PATH,
            recursive=True,
            required_exts=[".pdf", ".txt", ".md"]
        ).load_data()
    except Exception as e:
        print(f"Error reading documents: {e}")
        return None

    if not documents:
        print("No documents found in ~/Notes")
        print("Add .txt .md or .pdf files there first.")
        return None

    print(f"Found {len(documents)} documents. Building index...")

    # Delete old index and rebuild fresh
    os.makedirs(CHROMA_PATH, exist_ok=True)
    client     = chromadb.PersistentClient(path=CHROMA_PATH)

    # Delete existing collection to avoid stale data
    try:
        client.delete_collection("sameer_knowledge")
    except Exception:
        pass

    collection      = client.get_or_create_collection("sameer_knowledge")
    vector_store    = ChromaVectorStore(chroma_collection=collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context
    )

    print(f"Done. Index saved to {CHROMA_PATH}")
    print(f"Collection size: {collection.count()} chunks")
    print(f"Your AI can now answer from {len(documents)} documents.")


if __name__ == "__main__":
    build_index()