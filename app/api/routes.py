import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.api.schemas import QueryRequest, QueryResponse, IngestResponse
from app.core.ingestion import load_resume, chunk_documents
from app.core.vector_store import ingest_chunks
from app.core.rag_chain import build_rag_chain
from app.agents.recruiter_agent import build_recruiter_agent

router = APIRouter()

@router.post("/ingest", response_model=IngestResponse)
async def ingest_resume(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(400, "PDF only")
    os.makedirs("data/raw", exist_ok=True)
    save_path = f"data/raw/{file.filename}"
    with open(save_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    pages = load_resume(save_path)
    chunks = chunk_documents(pages)
    ingest_chunks(chunks)
    return IngestResponse(message="Ingested", chunks_created=len(chunks), filename=file.filename)

@router.post("/query", response_model=QueryResponse)
async def query_resumes(req: QueryRequest):
    try:
        if req.use_agent:
            agent = build_recruiter_agent()
            ans = agent.invoke({"input": req.question})["output"]
        else:
            ans = build_rag_chain().invoke(req.question)
        return QueryResponse(answer=ans)
    except Exception as e:
        raise HTTPException(500, str(e))