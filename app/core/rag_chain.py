import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate     # use langchain_core
from langchain_core.runnables import RunnablePassthrough  # use langchain_core
from langchain_core.output_parsers import StrOutputParser # use langchain_core
from app.core.vector_store import get_vector_store, get_mmr_retriever
from dotenv import load_dotenv
load_dotenv()

RAG_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an expert technical recruiter AI.
Analyze resumes using ONLY the provided context.
If info is absent, say: Not found in resume.
Always cite the candidate name.

Response format:
- Key Skills: [list]
- Experience Level: [junior/mid/senior]
- Relevant Experience: [2-sentence summary]
- Gap Analysis: [missing skills for this role]
- Recommendation: [hire/maybe/pass + reasoning]
"""),
    ("human", "Resume context:\n{context}\n\nQuestion: {question}")
])

def get_llm():
    return ChatGroq(
        model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
        temperature=0,
        max_tokens=1024,
    )

def format_docs(docs):
    return "\n\n---\n\n".join([
        f"[{doc.metadata.get('source','unknown')}]\n{doc.page_content}"
        for doc in docs
    ])

def build_rag_chain():
    llm = get_llm()
    store = get_vector_store()
    retriever = get_mmr_retriever(store)
    chain = (
        {"context": retriever | format_docs,
         "question": RunnablePassthrough()}
        | RAG_PROMPT
        | llm
        | StrOutputParser()
    )
    return chain