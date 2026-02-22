from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Platform(str, Enum):
    ANDROID = "android"
    IOS = "ios"


@dataclass
class Screen:
    """Normalized screen observation built from OCR/UI tree/CV models."""

    id: str
    visible_texts: list[str] = field(default_factory=list)
    visible_icons: list[str] = field(default_factory=list)


@dataclass
class Step:
    action: str
    target: str


@dataclass
class UXRule:
    """A declarative UX assertion bound to an entry condition."""

    name: str
    when_screen_contains: str
    when_image_contains: str
    then_first_page_must_contain: str


@dataclass
class RunResult:
    passed: bool
    summary: str
    evidence: list[str] = field(default_factory=list)
