# rag-resume-analyzer
AI Resume Analyzer | Python · FastAPI · LangChain · Groq · ChromaDB · React
# RAG Resume Analyzer

An AI-powered recruitment tool that lets you query a database of candidate resumes using plain English — built on a proper RAG pipeline, not keyword search.

Instead of ctrl+F through PDFs, you ask things like *"find Python engineers who've worked in fintech"* or *"which candidates have Docker experience but lack ML background?"* and get structured, reasoned answers back. The system retrieves semantically relevant chunks from resumes, passes them to an LLM, and returns analysis you can actually act on.

Built as a portfolio project targeting AI engineer roles. Every architectural decision was made deliberately — documented below so you can understand the reasoning, not just the code.

---

## What it does

- **Semantic resume search** — finds candidates based on meaning, not exact keywords. A resume saying "scripting in CPython" matches a query for "Python experience."
- **Gap analysis** — compare a candidate's profile against a job description and get a structured breakdown of matched skills, missing skills, and a fit score.
- **Candidate ranking** — rank all indexed candidates against a set of criteria in one query.
- **ReAct agent** — for complex multi-step questions, a reasoning agent breaks the task into sub-queries, calls the right tools, and synthesizes a final answer.
- **Drag-and-drop ingestion** — upload PDFs through the UI, they get chunked and indexed into ChromaDB automatically.

---

## Tech stack

**Backend**
- Python 3.11
- FastAPI — async REST API, chosen over Flask because LLM calls take 8–15 seconds and a synchronous server would block under any real load
- LangChain 0.3.x (LCEL) — the pipe-based chain syntax that's become the standard in production RAG systems
- ChromaDB — persistent local vector store with MMR retrieval
- Groq + Llama 3.3 70B — free LLM inference, no OpenAI dependency
- sentence-transformers (all-MiniLM-L6-v2) — local embeddings, runs on CPU, zero API cost
- LangSmith — observability and tracing for every LLM call

**Frontend**
- React + Vite
- Tailwind CSS
- react-dropzone for file upload

**Deployment**
- Backend → Render (free tier)
- Frontend → Vercel (free tier)
- Total monthly cost: $0

---

## Architecture

```
PDF resumes
    │
    ▼
PyPDFLoader → RecursiveCharacterTextSplitter (500 tokens, 100 overlap)
    │
    ▼
HuggingFaceEmbeddings (all-MiniLM-L6-v2, local CPU)
    │
    ▼
ChromaDB (persistent vector store)
    │
    ├── Simple query → MMR retriever → RAG chain → Groq LLM → structured answer
    │
    └── Complex query → ReAct agent → tool selection → search/gap/rank tools → synthesized answer
```

**Why MMR over standard cosine similarity?** A verbose resume produces many near-identical chunks. Standard similarity search returns all of them — you get six chunks about the same Python project. MMR (Maximal Marginal Relevance) enforces diversity: you get a Python chunk, a leadership chunk, an education chunk. The `lambda_mult=0.7` parameter means 70% weight on relevance, 30% on diversity — tuned by testing retrieval quality on sample queries.

**Why 500-token chunks?** Shorter chunks produce sharper embedding vectors. A 1000-token chunk mixing Python skills, leadership experience, and education creates a blurry averaged vector that retrieves imprecisely. A 500-token chunk about one topic retrieves the right candidates for the right reasons. The 100-token overlap prevents retrieval gaps at chunk boundaries.

---

## Project structure

```
rag-resume-analyzer/
├── app/
│   ├── api/
│   │   ├── routes.py          # FastAPI endpoints: /ingest, /query
│   │   └── schemas.py         # Pydantic request/response models
│   ├── core/
│   │   ├── ingestion.py       # PDF loading and chunking
│   │   ├── vector_store.py    # ChromaDB + MMR retriever
│   │   └── rag_chain.py       # LCEL RAG chain with Groq
│   └── agents/
│       ├── tools.py           # search_resumes, analyze_skill_gaps, rank_candidates
│       └── recruiter_agent.py # ReAct agent executor
├── data/raw/                  # Drop PDF resumes here
├── scripts/
│   ├── ingest_resumes.py      # One-time ingestion script
│   └── evaluate.py            # Retrieval quality checks
├── frontend/                  # React + Vite application
├── main.py                    # FastAPI app entry point
├── requirements.txt
└── .env.example
```

---

## Getting started

### Prerequisites

- Python 3.11
- Node.js 18+
- A free [Groq API key](https://console.groq.com) — no credit card needed
- A free [LangSmith account](https://smith.langchain.com) — for observability

### Backend setup

```bash
# Clone and open
git clone https://github.com/YOUR_USERNAME/rag-resume-analyzer.git
cd rag-resume-analyzer

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Open .env and fill in your API keys
```

### Environment variables

```env
GROQ_API_KEY=gsk_your_key_here
GROQ_MODEL=llama-3.3-70b-versatile
LANGSMITH_API_KEY=ls__your_key_here
LANGSMITH_TRACING=true
LANGSMITH_PROJECT=rag-resume-analyzer
CHROMA_PERSIST_DIR=./data/chroma_db
COLLECTION_NAME=resumes
ALLOWED_ORIGINS=http://localhost:5173
```

### Ingest resumes

Drop PDF resumes into `data/raw/` then run:

```bash
python scripts/ingest_resumes.py
```

This loads each PDF, splits it into chunks, embeds them locally, and saves everything to ChromaDB. Run this once — or again whenever you add new resumes.

### Start the backend

```bash
uvicorn main:app --reload --port 8000
```

API docs available at `http://localhost:8000/docs` — you can test every endpoint there without the frontend.

### Start the frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173` — upload PDFs and start querying.

---

## API reference

### `POST /api/v1/ingest`

Upload a PDF resume. Chunks it and adds to the vector store.

```bash
curl -X POST http://localhost:8000/api/v1/ingest \
  -F "file=@candidate.pdf"
```

```json
{
  "message": "Ingested",
  "chunks_created": 14,
  "filename": "candidate.pdf"
}
```

### `POST /api/v1/query`

Query indexed resumes. Set `use_agent: true` for complex multi-step questions.

```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"question": "Find candidates with Python and ML experience", "use_agent": false}'
```

```json
{
  "answer": "- Key Skills: Python, TensorFlow, scikit-learn...\n- Experience Level: mid\n...",
  "sources": []
}
```

### `GET /api/v1/health`

```json
{"status": "ok"}
```

---

## Observability

LangSmith traces every LLM call automatically once the env vars are set. Every query shows:

- Input and output tokens
- Latency per step
- Which chunks were retrieved
- The full prompt sent to the LLM

This is how you catch problems like "the agent is calling the wrong tool" or "this prompt is using 3x more tokens than it should." During development, tracing gap analysis queries showed they used significantly more tokens than skill searches — which prompted a prompt rewrite that reduced token usage noticeably.

---

## Deployment

### Backend → Render

1. Push to GitHub
2. New Web Service → connect repo
3. Build: `pip install -r requirements.txt`
4. Start: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add all env vars in the Render dashboard

Note: Render's free tier has ephemeral storage, so ChromaDB on disk won't survive redeployments. For a persistent setup, swap in [Chroma Cloud](https://trychroma.com) (also free) or re-run the ingestion script on startup.

### Frontend → Vercel

1. Import repo in Vercel
2. Set root directory to `frontend`
3. Add env var: `VITE_API_URL=https://your-render-url.onrender.com/api/v1`
4. Deploy

---

## Design decisions worth mentioning

**Why not Flask?** Flask is synchronous — while one 10-second LLM call is running, every other request waits. FastAPI runs on asyncio, so concurrent requests don't block each other. For an LLM application this isn't optional.

**Why Groq over OpenAI?** The whole stack runs free. Groq's LPU hardware is also genuinely fast — Llama 3.3 70B inference is often faster than GPT-4o-mini despite being a larger model. For this kind of structured text analysis task, the quality difference is minimal.

**Why local embeddings over OpenAI embeddings?** Zero cost, zero latency dependency on an external API, and all-MiniLM-L6-v2 is well-suited for short professional text. The 384-dimensional vectors are smaller and faster to search than OpenAI's 1536-dimensional ones, with negligible quality difference on this domain.

**Why ReAct over a simple chain for complex queries?** A plain RAG chain answers one question. A ReAct agent breaks "find senior Python engineers who lack Docker, ranked by ML depth" into sub-tasks, uses the right tool for each, and synthesizes. The verbose mode shows the full reasoning chain — which is also useful for debugging.

---

## Known limitations

- ChromaDB on Render free tier doesn't persist across deploys (see deployment note above)
- Render free tier cold starts take ~30 seconds after idle — expected for a portfolio project
- The local embedding model downloads ~90MB on first run; cached after that
- No authentication on the API — fine for a portfolio demo, would need JWT or API keys for production

---

## What I'd do differently at production scale

- Switch ChromaDB to a managed vector database (Pinecone or Weaviate) with proper indexing
- Add an embedding cache to avoid re-embedding the same chunks after code changes
- Implement streaming responses so the frontend shows text as it generates instead of waiting for the full response
- Add proper auth, rate limiting, and per-user resume namespacing in the vector store
- Set up CI/CD with GitHub Actions to run the evaluation script on every push

---

## License

MIT
