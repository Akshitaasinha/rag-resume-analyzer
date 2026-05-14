from pydantic import BaseModel, Field

class QueryRequest(BaseModel):
    question: str = Field(..., min_length=5)
    use_agent: bool = Field(default=False)

class QueryResponse(BaseModel):
    answer: str
    sources: list[str] = []

class IngestResponse(BaseModel):
    message: str
    chunks_created: int
    filename: str