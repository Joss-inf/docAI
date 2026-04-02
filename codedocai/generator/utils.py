"""Shared utilities for documentation generators."""

import re

def role_icon(role: str) -> str:
    """Return a simple text marker for a module role."""
    markers = {
        "controller": "[CTRL]",
        "service": "[SVC]",
        "repository": "[REPO]",
        "model": "[MODEL]",
        "utility": "[UTIL]",
        "config": "[CONF]",
        "test": "[TEST]",
        "generic": "[FILE]",
    }
    return markers.get(role, "[FILE]")


def sanitize_summary(text: str) -> str:
    """Strip LLM preambles, internal tokens, and code blocks."""
    if not text:
        return ""
    
    # 1. Remove markdown code blocks
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    
    # 2. Remove common LLM preambles
    preambles = [
        r"^Here's a factual behavioral description.*?:",
        r"^Okay, here is.*?:",
        r"^Sure, here is.*?:",
        r"^Based on the provided IR.*?:",
        r"^This module.*?:",
        r"^The code.*?:",
    ]
    for p in preambles:
        text = re.sub(p, '', text, flags=re.IGNORECASE | re.MULTILINE)
    
    # 3. Remove internal tokens
    text = text.replace("/no_think", "")
    text = text.replace("[WHO]", "").replace("[WHAT]", "").replace("[HOW]", "")
    text = re.sub(r'SYMBOL WHITELIST:.*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'while adhering to the provided whitelist.*', '', text, flags=re.IGNORECASE)
    
    return text.strip()
