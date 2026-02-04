from typing import List

import torch
from sentence_transformers import SentenceTransformer
from torch import Tensor
import logging

from policy_rag_eval.retrieval.model.types import Chunk, RetrievalResult

logger = logging.getLogger(__name__)

def pick_device() -> str:
    if torch.cuda.is_available():
        return "cuda"
    if torch.backends.mps.is_available() and torch.backends.mps.is_built():
        return "mps"
    return "cpu"

device = pick_device()
model_name = "sentence-transformers/all-MiniLM-L6-v2"
logger.info(f"Using '{device}' device for model '{model_name}'")
model = SentenceTransformer(model_name, device=device)

def retrieve(chunks: tuple[Tensor, list[Chunk]], question: str, top_k: int) -> List[RetrievalResult]:
    q_tensor = model.encode(question, normalize_embeddings=True, convert_to_tensor=True)
    if q_tensor is None or q_tensor.numel() == 0:
        return []

    emb, chunk_list = chunks
    scores = emb @ q_tensor
    top_idx = torch.topk(scores, k=top_k).indices

    scored: List[RetrievalResult] = [RetrievalResult(chunk=chunk_list[i], score=float(scores[i])) for i in top_idx]
    return scored
