from pydantic import BaseModel, Field

class QueryRequest(BaseModel):
    question: str = Field(..., min_length=5)
    top_k: int = Field(default=5, ge=1, le=20)

class Citation(BaseModel):
    doc_id: str
    source: str
    chunk_id: int
    start: int
    end: int
    excerpt: str

class QueryResponse(BaseModel):
    answer: str
    citations: list[Citation]
    run_id: str
