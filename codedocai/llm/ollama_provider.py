"""Ollama provider — calls a local Ollama instance."""

from __future__ import annotations

import logging
import time

import httpx

from codedocai.config import OllamaConfig
from codedocai.llm.base_provider import BaseLLMProvider

logger = logging.getLogger(__name__)


class OllamaProvider(BaseLLMProvider):
    """Local LLM via Ollama HTTP API."""

    def __init__(self, config: OllamaConfig) -> None:
        self._config = config
        self._client = httpx.Client(base_url=config.base_url, timeout=config.timeout_seconds)

    def summarize(self, prompt: str) -> str:
        payload = {
            "model": self._config.model,
            "prompt": prompt,
            "stream": False,
        }
        for attempt in range(1, self._config.max_retries + 1):
            try:
                resp = self._client.post("/api/generate", json=payload)
                # 404 means model not found — don't retry
                if resp.status_code == 404:
                    logger.error("Ollama model '%s' not found (404)", self._config.model)
                    return ""
                resp.raise_for_status()
                return resp.json().get("response", "")
            except httpx.TimeoutException:
                wait = 2 ** attempt
                logger.warning("Ollama attempt %d timed out — retrying in %ds", attempt, wait)
                time.sleep(wait)
            except httpx.HTTPError as exc:
                wait = 2 ** attempt
                logger.warning("Ollama attempt %d failed: %s — retrying in %ds", attempt, exc, wait)
                time.sleep(wait)

        logger.error("Ollama: all %d attempts failed", self._config.max_retries)
        return ""

    def is_available(self) -> bool:
        """Check if Ollama is running AND the configured model is present."""
        try:
            resp = self._client.get("/api/tags")
            if resp.status_code != 200:
                return False
            models = resp.json().get("models", [])
            available = any(
                m.get("name", "").startswith(self._config.model) for m in models
            )
            if not available:
                logger.info("Ollama running but model '%s' not found", self._config.model)
            return available
        except httpx.HTTPError:
            return False
