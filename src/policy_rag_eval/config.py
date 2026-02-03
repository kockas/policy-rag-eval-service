from __future__ import annotations

from dataclasses import dataclass
from configparser import ConfigParser
from functools import lru_cache
from pathlib import Path
import logging
import os

logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class Settings:
    max_hops: int = 2
    top_k: int = 5
    openai_model: str = "gpt-5-mini"


@lru_cache
def load_settings() -> Settings:
    config_path = os.getenv("POLICY_RAG_EVAL_CONFIG")
    if config_path:
        path = Path(config_path)
    else:
        path = Path(__file__).resolve().parents[2] / "config" / "app.ini"

    parser = ConfigParser()
    if path.exists():
        parser.read(path)

    logger.info(f"App config found is: {parser}")

    max_hops = parser.getint("rag", "max_hops", fallback=Settings.max_hops)
    top_k = parser.getint("rag", "top_k", fallback=Settings.top_k)
    model = parser.get("llm", "model", fallback=Settings.openai_model)

    return Settings(max_hops=max_hops, top_k=top_k, openai_model=model)
