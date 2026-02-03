from pydantic import BaseModel, Field

from policy_rag_eval.retrieval.model.types import Chunk

class GraphState(BaseModel):
    model_config = {"arbitrary_types_allowed": True}
    question: str = ""                                      # original user question
    queries: list[str]   = Field(default_factory=list)      # list of retrieval queries used so far (multi-hop)
    docs: list[Chunk]  = Field(default_factory=list)        # retrieved chunks for current hop
    citations: list[dict] = Field(default_factory=list)     # structured citations derived from docs
    answer: str = ""                                        # final answer text
    sufficient: bool = False                                # whether evidence is enough to answer
    suggested_query: str = ""                               # next query suggestion if insufficient
    hops: int = 0                                           # how many hops have been executed
    max_hops: int = 2                                       # max hops allowed before stopping
    top_k: int = 5                                          # number of chunks to retrieve per hop
