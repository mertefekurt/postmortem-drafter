from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Event:
    timestamp: str
    kind: str
    summary: str
    owner: str = ""
    impact: str = ""


@dataclass(frozen=True)
class PostmortemDraft:
    title: str
    markdown: str
    action_count: int
    impact_count: int

