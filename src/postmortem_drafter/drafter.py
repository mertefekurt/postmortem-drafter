from __future__ import annotations

import re
from collections import Counter

from postmortem_drafter.models import Event, PostmortemDraft

ACTION_WORDS = ("fix", "add", "create", "document", "monitor", "alert", "rollback", "review")
ROOT_CAUSE_WORDS = ("because", "root cause", "caused by", "misconfigured", "regression", "expired")


def draft_postmortem(events: list[Event], title: str = "Incident postmortem") -> PostmortemDraft:
    if not events:
        raise ValueError("at least one incident event is required")
    ordered = sorted(events, key=lambda event: event.timestamp)
    impact_lines = _impact_lines(ordered)
    action_items = _action_items(ordered)
    owner_counts = Counter(event.owner for event in ordered if event.owner)
    root_signals = _root_cause_signals(ordered)

    lines = [
        f"# {title}",
        "",
        "## Executive summary",
        "",
        _executive_summary(ordered, impact_lines),
        "",
        "## Impact",
        "",
        *(impact_lines or ["- impact not explicitly recorded"]),
        "",
        "## Timeline",
        "",
        *[
            f"- `{event.timestamp}` **{event.kind}**"
            f"{f' ({event.owner})' if event.owner else ''}: {event.summary}"
            for event in ordered
        ],
        "",
        "## Contributing signals",
        "",
        *(root_signals or ["- no root-cause wording detected in the timeline"]),
        "",
        "## Owners mentioned",
        "",
        *(
            [f"- {owner}: {count} event(s)" for owner, count in sorted(owner_counts.items())]
            if owner_counts
            else ["- no owners recorded"]
        ),
        "",
        "## Follow-up actions",
        "",
        *(action_items or ["- define one concrete follow-up owner and due date"]),
    ]
    return PostmortemDraft(
        title=title,
        markdown="\n".join(lines) + "\n",
        action_count=len(action_items),
        impact_count=len(impact_lines),
    )


def _executive_summary(events: list[Event], impact_lines: list[str]) -> str:
    start = events[0].timestamp
    end = events[-1].timestamp
    impact = " ".join(line.removeprefix("- ") for line in impact_lines[:2])
    impact_text = impact or "Customer impact was not explicitly captured in the source events."
    return f"Incident window `{start}` to `{end}`. {impact_text}"


def _impact_lines(events: list[Event]) -> list[str]:
    seen: set[str] = set()
    lines: list[str] = []
    for event in events:
        if event.impact and event.impact not in seen:
            seen.add(event.impact)
            lines.append(f"- {event.impact}")
    return lines


def _action_items(events: list[Event]) -> list[str]:
    items: list[str] = []
    for event in events:
        summary = event.summary.strip()
        if _looks_actionable(summary):
            owner = event.owner or "unassigned"
            items.append(f"- [ ] {summary} (owner: {owner})")
    return items


def _root_cause_signals(events: list[Event]) -> list[str]:
    signals: list[str] = []
    for event in events:
        lowered = event.summary.casefold()
        if any(word in lowered for word in ROOT_CAUSE_WORDS):
            signals.append(f"- `{event.timestamp}` {event.summary}")
    return signals


def _looks_actionable(text: str) -> bool:
    lowered = text.casefold()
    if lowered.startswith("action:"):
        return True
    return bool(re.match(rf"^({'|'.join(ACTION_WORDS)})\b", lowered))

