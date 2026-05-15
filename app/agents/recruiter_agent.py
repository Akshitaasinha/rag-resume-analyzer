from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from app.agents.tools import search_resumes, analyze_skill_gaps, rank_candidates
from app.core.rag_chain import get_llm

TOOLS = [search_resumes, analyze_skill_gaps, rank_candidates]

AGENT_PROMPT = PromptTemplate.from_template("""You are an expert AI recruiter.
Use tools to answer questions accurately. Verify with tools before responding.

Tools: {tools}
Tool names: {tool_names}
Question: {input}
Think step by step. {agent_scratchpad}""")

def build_recruiter_agent():
    llm = get_llm()
    agent = create_react_agent(llm, TOOLS, AGENT_PROMPT)
    return AgentExecutor(
        agent=agent,
        tools=TOOLS,
        verbose=True,
        max_iterations=5,
        handle_parsing_errors=True,
    )