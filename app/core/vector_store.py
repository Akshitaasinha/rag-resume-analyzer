import os
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.schema import Document
from dotenv import load_dotenv
load_dotenv()

CHROMA_DIR = os.getenv("CHROMA_PERSIST_DIR", "./data/chroma_db")
COLLECTION = os.getenv("COLLECTION_NAME", "resumes")

def get_embedding_model():
    """Free local embeddings — runs on CPU, no API key."""
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )

def get_vector_store() -> Chroma:
    return Chroma(
        collection_name=COLLECTION,
        embedding_function=get_embedding_model(),
        persist_directory=CHROMA_DIR,
    )

def ingest_chunks(chunks: list[Document]) -> Chroma:
    store = Chroma.from_documents(
        documents=chunks,
        embedding=get_embedding_model(),
        collection_name=COLLECTION,
        persist_directory=CHROMA_DIR,
    )
    print(f"Ingested {len(chunks)} chunks")
    return store

def get_mmr_retriever(store: Chroma, k: int = 5, fetch_k: int = 20):
    """MMR = diverse + relevant results, not just top-similar."""
    return store.as_retriever(
        search_type="mmr",
        search_kwargs={"k": k, "fetch_k": fetch_k, "lambda_mult": 0.7}
    )