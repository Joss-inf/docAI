"""Tests for the scanner package."""

from pathlib import Path

from codedocai.scanner.language_detect import Language, detect_language


def test_detect_language():
    assert detect_language(Path("test.py")) == Language.PYTHON
    assert detect_language(Path("src/index.js")) == Language.JAVASCRIPT
    assert detect_language(Path("components/Button.tsx")) == Language.TYPESCRIPT
    assert detect_language(Path("main.rs")) == Language.RUST
    assert detect_language(Path("README.md")) == Language.UNKNOWN
    assert detect_language(Path("Makefile")) == Language.UNKNOWN
