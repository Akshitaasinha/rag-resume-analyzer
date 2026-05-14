from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
import os


app = FastAPI(title="RAG Resume Analyzer", version="1.0.0")
ORIGINS = os.getenv("ALLOWED_ORIGINS","http://localhost:5173").split(",")
app.add_middleware(CORSMiddleware, allow_origins=ORIGINS, allow_methods=["*"], allow_headers=["*"])
app.include_router(router, prefix="/api/v1")

@app.get("/health")
async def health(): return {"status":"ok"}

# Start: uvicorn main:app --reload --port 8000
# Docs:  http://localhost:8000/docs