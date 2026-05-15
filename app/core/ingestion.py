from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader  # changed
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

def load_resume(file_path: str) -> list[Document]:
    loader = PyPDFLoader(file_path)          # was PyPDF2Loader
    pages = loader.load()
    for page in pages:
        page.metadata["source"] = Path(file_path).stem
        page.metadata["file_type"] = "resume"
    print(f"Loaded {len(pages)} pages from {file_path}")
    return pages

def chunk_documents(documents: list[Document]) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
        separators=["\n\n", "\n", ".", " ", ""],
        length_function=len,
    )
    chunks = splitter.split_documents(documents)
    print(f"Created {len(chunks)} chunks")
    return chunks