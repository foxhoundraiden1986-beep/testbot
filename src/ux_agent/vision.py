from __future__ import annotations

from ux_agent.models import Screen


class ScreenRecognizer:
    """Minimal recognizer abstraction.

    In production this can merge OCR, icon classification, and UI tree parsing.
    Here we operate on pre-collected text/icon tokens for deterministic tests.
    """

    def contains(self, screen: Screen, keyword: str) -> bool:
        normalized = keyword.strip().lower()
        return any(normalized in token.lower() for token in screen.visible_texts + screen.visible_icons)
