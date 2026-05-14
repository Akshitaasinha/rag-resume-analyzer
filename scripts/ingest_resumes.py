import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from app.core.ingestion import load_resume, chunk_documents
from app.core.vector_store import ingest_chunks

def main():
    pdf_files = list(Path("data/raw").glob("*.pdf"))
    if not pdf_files:
        print("Add PDF resumes to data/raw/ first"); return
    all_chunks = []
    for pdf in pdf_files:
        pages = load_resume(str(pdf))
        chunks = chunk_documents(pages)
        all_chunks.extend(chunks)
    store = ingest_chunks(all_chunks)
    print(f"Done. Total chunks: {store._collection.count()}")

if __name__ == "__main__":
    main()

# Run: python scripts/ingest_resumes.py