from __future__ import annotations

import httpx
import logging

logger = logging.getLogger(__name__)

class OpenAIClient:
    def __init__(self, api_key: str, model: str, base_url: str = "https://api.openai.com/v1", timeout: float = 30.0) -> None:
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def complete(self, messages: list[dict]) -> str:
        payload = {
            "model": self.model,
            "input": messages,
        }

        logger.info("LLM request model=%s messages=%s", self.model, messages)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.post(f"{self.base_url}/responses", json=payload, headers=headers)

        logger.info("LLM response status=%s body=%s", resp.status_code, resp.text)

        resp.raise_for_status()
        data = resp.json()
        return _extract_text(data)


def _extract_text(data: dict) -> str:
    output = data.get("output", [])
    texts: list[str] = []
    for item in output:
        if item.get("type") != "message":
            continue
        for content in item.get("content", []):
            if content.get("type") == "output_text":
                texts.append(content.get("text", ""))
    return "".join(texts).strip()
