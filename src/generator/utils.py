"""Utility functions for documentation generators."""

import re

def sanitize_summary(text: str) -> str:
    """Clean LLM output from markdown blocks and preambles."""
    if not text: return ""
    # Remove markdown code blocks
    text = re.sub(r"```[a-z]*\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"```", "", text)
    # Remove common LLM preambles
    text = re.sub(r"^(Here is|This file|This module|The provided code)[^.:]*[:.]\s*", "", text, flags=re.IGNORECASE)
    return text.strip()
