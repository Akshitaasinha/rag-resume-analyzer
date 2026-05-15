import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from dotenv import load_dotenv

load_dotenv()

CHROMA_DIR = os.getenv("CHROMA_PERSIST_DIR", "./data/chroma_db")
COLLECTION  = os.getenv("COLLECTION_NAME", "resumes")

def get_embedding_model():
    """
    Google Gemini Embeddings — free via Google AI Studio API key.
    No local download, no RAM spike, no cold start, no 404 errors.
    768-dimensional vectors, excellent quality for resume text.
    """
    return GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        task_type="RETRIEVAL_DOCUMENT",
    )

def get_query_embedding_model():
    """Separate task_type for queries vs documents — improves retrieval quality."""
    return GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        task_type="RETRIEVAL_QUERY",
    )

def get_vector_store() -> Chroma:
    return Chroma(
        collection_name=COLLECTION,
        embedding_function=get_query_embedding_model(),
        persist_directory=CHROMA_DIR,
    )

def ingest_chunks(chunks: list[Document]) -> Chroma:
    store = Chroma.from_documents(
        documents=chunks,
        embedding=get_embedding_model(),   # RETRIEVAL_DOCUMENT for ingestion
        collection_name=COLLECTION,
        persist_directory=CHROMA_DIR,
    )
    print(f"Ingested {len(chunks)} chunks into ChromaDB")
    return store

def get_mmr_retriever(store: Chroma, k: int = 5, fetch_k: int = 20):
    return store.as_retriever(
        search_type="mmr",
        search_kwargs={"k": k, "fetch_k": fetch_k, "lambda_mult": 0.7},
    )