# Contributing to ClipVein

Thanks for wanting to make ClipVein better. It's a small, readable codebase on
purpose — contributions that keep it that way are the most welcome.

## Setup

```bash
git clone https://github.com/grovenx/clipvein.git
cd clipvein
pip install -e ".[dev]"
playwright install chromium
```

## Run the tests

```bash
pytest
```

The pure-logic parts (parsing, ranking) are unit-tested and don't need a
browser. Please keep them green and add tests for new logic.

## Style

- `ruff` for lint/format (`ruff check .` / `ruff format .`).
- Type hints on public functions.
- Keep modules small and single-purpose — match the existing layout.

## Good first contributions

- New streamers in `clipvein/streamers.py` (with real handles + aliases).
- Ranker tuning experiments (with a test that shows the effect).
- New data sources behind the `Source` enum (ClipVein reads the X feed today).
- Prompt improvements in `prompts/` (keep the code + prompt files in sync).
- Docs and examples.

## What won't be merged

- Anything that buys/fakes engagement, runs bots, or auto-posts silently.
- Anything built to funnel an audience into a token/pump scheme.
- Scrapers that mass-hit endpoints instead of reading the user's own feed.

ClipVein is a discovery tool for real, honest clipping. PRs that keep it that
way are the ones that ship.

## Opening a PR

1. Branch from `main`.
2. Keep the change focused; one idea per PR.
3. `pytest` green, `ruff` clean.
4. Describe *what* and *why* in the PR body.
