from pydantic import BaseModel, Field

class QueryRequest(BaseModel):
    question: str = Field(..., min_length=5)
    top_k: int = Field(default=5, ge=1, le=20)

class Citation(BaseModel):
    source: str
    excerpt: str

class QueryResponse(BaseModel):
    answer: str
    citations: list[Citation]
    run_id: str
