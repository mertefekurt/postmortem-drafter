# Postmortem Drafter

Draft incident postmortems from timeline CSV or JSONL exports. In practice it is a narrow guardrail for incident response, ownership, release risk, and follow-up notes: one command, a concrete report, and very little ceremony.

## A quick look

![Postmortem Drafter cover](assets/readme-cover.svg)

## Start here

```bash
git clone https://github.com/mertefekurt/postmortem-drafter.git
cd postmortem-drafter
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

Run:

```bash
postmortem-drafter examples/timeline.csv
```

## Files with the most context

```text
.github/        CI workflow
examples/       sample inputs
src/            package source
tests/          test coverage
.gitignore      project file
pyproject.toml  package metadata
```
