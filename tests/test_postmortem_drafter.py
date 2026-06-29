from postmortem_drafter.cli import main
from postmortem_drafter.drafter import draft_postmortem
from postmortem_drafter.io import read_events
from postmortem_drafter.models import Event


def test_draft_sorts_timeline_and_extracts_impact() -> None:
    draft = draft_postmortem(
        [
            Event("2026-06-29T10:10:00Z", "mitigation", "Rollback completed", "platform"),
            Event(
                "2026-06-29T10:00:00Z",
                "detect",
                "Checkout errors detected",
                "support",
                "20% of checkouts failed",
            ),
        ],
        "Checkout incident",
    )

    assert draft.markdown.index("10:00") < draft.markdown.index("10:10")
    assert "20% of checkouts failed" in draft.markdown


def test_extracts_action_items() -> None:
    draft = draft_postmortem(
        [Event("t1", "action", "Add alert for payment failures", "sre")],
    )

    assert draft.action_count == 1
    assert "- [ ] Add alert for payment failures (owner: sre)" in draft.markdown


def test_detects_root_cause_signals() -> None:
    draft = draft_postmortem(
        [Event("t1", "analysis", "Root cause was a misconfigured retry policy", "platform")]
    )

    assert "Root cause was a misconfigured retry policy" in draft.markdown


def test_reads_csv_events(tmp_path) -> None:
    path = tmp_path / "timeline.csv"
    path.write_text(
        "timestamp,type,summary,owner,impact\n"
        "t1,detect,Errors detected,support,customers blocked\n",
        encoding="utf-8",
    )

    events = read_events(path)

    assert events == [Event("t1", "detect", "Errors detected", "support", "customers blocked")]


def test_cli_writes_markdown(tmp_path) -> None:
    input_path = tmp_path / "timeline.jsonl"
    out_path = tmp_path / "postmortem.md"
    input_path.write_text(
        '{"timestamp":"t1","kind":"detect","summary":"API errors detected","owner":"sre"}\n',
        encoding="utf-8",
    )

    exit_code = main([str(input_path), "--title", "API incident", "--out", str(out_path)])

    assert exit_code == 0
    assert out_path.read_text(encoding="utf-8").startswith("# API incident")

