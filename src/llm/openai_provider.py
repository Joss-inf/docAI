"""OpenAI-compatible provider — works with any OpenAI-compatible API."""

from __future__ import annotations

import logging
import time
import httpx
from src.config import OpenAIConfig
from src.llm.base_provider import BaseLLMProvider

logger = logging.getLogger(__name__)


class OpenAIProvider(BaseLLMProvider):
    """External LLM via OpenAI-compatible chat completions API."""

    def __init__(self, config: OpenAIConfig) -> None:
        self._config = config
        self._client = httpx.Client(
            base_url=config.base_url,
            timeout=config.timeout_seconds,
            headers={"Authorization": f"Bearer {config.api_key}"},
        )

    def summarize(self, prompt: str) -> str:
        payload = {
            "model": self._config.model,
            "messages": [
                {"role": "system", "content": "You are a technical documentation writer. Write concise, accurate summaries."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.3,
        }
        for attempt in range(1, self._config.max_retries + 1):
            try:
                resp = self._client.post("/chat/completions", json=payload)
                resp.raise_for_status()
                data = resp.json()
                return data["choices"][0]["message"]["content"]
            except (httpx.HTTPError, httpx.TimeoutException, KeyError) as exc:
                wait = 2 ** attempt
                logger.warning("OpenAI attempt %d failed: %s — retrying in %ds", attempt, exc, wait)
                time.sleep(wait)

        logger.error("OpenAI: all %d attempts failed", self._config.max_retries)
        return ""

    def is_available(self) -> bool:
        try:
            resp = self._client.get("/models")
            return resp.status_code == 200
        except httpx.HTTPError:
            return False
