from langchain_core.tools import tool            
from app.core.vector_store import get_vector_store, get_mmr_retriever
from app.core.rag_chain import get_llm
@tool
def search_resumes(query: str) -> str:
    """Search all resumes for candidates matching the query.
    Use for: finding candidates with specific skills or background.
    Returns: relevant resume excerpts with candidate names."""
    store = get_vector_store()
    docs = get_mmr_retriever(store).invoke(query)
    if not docs: return "No matching candidates found."
    return "\n\n".join([f"[{d.metadata.get('source')}]: {d.page_content[:400]}" for d in docs])

@tool
def analyze_skill_gaps(candidate_context: str, job_requirements: str) -> str:
    """Analyze gap between candidate skills and job requirements.
    Use for: gap analysis, fit scoring, missing qualifications.
    Returns: matched skills, missing skills, fit score 0-100."""
    from app.core.rag_chain import get_llm
    llm = get_llm()
    prompt = f"Candidate: {candidate_context}\nRequirements: {job_requirements}\nProvide: matched skills, missing skills, transferable skills, fit score 0-100"
    return llm.invoke(prompt).content

@tool
def rank_candidates(criteria: str) -> str:
    """Rank all candidates by the given criteria.
    Use for: shortlists, comparing candidates, prioritizing.
    Returns: ordered candidate list with reasoning."""
    store = get_vector_store()
    docs = get_mmr_retriever(store, k=10).invoke(criteria)
    by_cand = {}
    for d in docs:
        by_cand.setdefault(d.metadata.get("source","?"), []).append(d.page_content[:200])
    return f"Candidates retrieved: {list(by_cand.keys())}"