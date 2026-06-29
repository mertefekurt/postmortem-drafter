from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from postmortem_drafter.models import Event


def read_events(path: Path, input_format: str = "auto") -> list[Event]:
    resolved = _resolve_format(path, input_format)
    if resolved == "csv":
        return _read_csv(path)
    if resolved == "jsonl":
        return _read_jsonl(path)
    raise ValueError(f"unsupported input format: {resolved}")


def _resolve_format(path: Path, requested: str) -> str:
    if requested != "auto":
        return requested
    if path.suffix.lower() == ".csv":
        return "csv"
    if path.suffix.lower() in {".jsonl", ".ndjson"}:
        return "jsonl"
    raise ValueError("could not infer input format; pass --format csv or --format jsonl")


def _read_csv(path: Path) -> list[Event]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError("CSV input requires a header row")
        return [_event_from_mapping(row) for row in reader]


def _read_jsonl(path: Path) -> list[Event]:
    events: list[Event] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            raw = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid JSON on line {line_number}: {exc.msg}") from exc
        if not isinstance(raw, dict):
            raise ValueError(f"line {line_number} must contain a JSON object")
        events.append(_event_from_mapping(raw))
    return events


def _event_from_mapping(raw: dict[str, Any]) -> Event:
    lowered = {str(key).lower(): value for key, value in raw.items()}
    timestamp = _first(lowered, "timestamp", "time", "occurred_at")
    summary = _first(lowered, "summary", "message", "description", "event")
    if not timestamp or not summary:
        raise ValueError("each event requires timestamp and summary fields")
    return Event(
        timestamp=timestamp,
        kind=_first(lowered, "kind", "type", "event_type") or "note",
        summary=summary,
        owner=_first(lowered, "owner", "team"),
        impact=_first(lowered, "impact", "customer_impact"),
    )


def _first(raw: dict[str, Any], *keys: str) -> str:
    for key in keys:
        value = raw.get(key)
        if value is not None and str(value).strip():
            return str(value).strip()
    return ""

