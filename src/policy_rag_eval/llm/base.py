from typing import Protocol

class LLM(Protocol):
    def complete(self, messages: list[dict]) -> str: ...