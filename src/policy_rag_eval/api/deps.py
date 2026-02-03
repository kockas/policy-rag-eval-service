from functools import lru_cache
import os

from fastapi import Depends, HTTPException

from policy_rag_eval.config import Settings, load_settings
from policy_rag_eval.llm.openai import OpenAIClient


@lru_cache
def get_settings() -> Settings:
    return load_settings()


def get_llm(settings: Settings = Depends(get_settings)):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY is not set")
    return OpenAIClient(api_key=api_key, model=settings.openai_model)
