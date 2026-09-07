# Architecture

ClipVein is a small, readable Python package. One async engine drives
everything; the desktop app and the CLI are just two front-ends that consume
the same stream of events.

```
                         ┌─────────────────────────────┐
                         │          Settings            │  config.py
                         │  (.env → source, floor, keys)│
                         └──────────────┬──────────────┘
                                        │
                                        ▼
   streamer name ────────────►   ┌─────────────┐
                                 │   Engine     │  engine.py
                                 │  .run(name)  │  async generator of Line
                                 └──────┬──────┘
                    ┌──────────────────┼──────────────────┐
                    ▼                  ▼                  ▼
             source=browser      source=grok         source=mock
                    │                  │                  │
                    ▼                  ▼                  ▼
        ┌────────────────┐   ┌──────────────┐   ┌──────────────┐
        │ BrowserSession │   │ grok_find_   │   │ sample_posts │
        │  (CDP attach)  │   │   posts()    │   │  (bundled)   │
        └───────┬────────┘   └──────┬───────┘   └──────┬───────┘
                ▼                    │                  │
        ┌────────────────┐          │                  │
        │  FeedScraper   │          │                  │
        │  .for_you()    │          │                  │
        └───────┬────────┘          │                  │
                └─────────┬─────────┴──────────────────┘
                          ▼
                   ┌─────────────┐
                   │   rank()    │  ranker/score.py
                   └──────┬──────┘
                          ▼
                   ┌─────────────┐
                   │ SearchResult│  models.py  → top 3 links
                   └──────┬──────┘
              ┌───────────┴───────────┐
              ▼                       ▼
      ┌──────────────┐        ┌──────────────┐
      │  ui/ (Qt)    │        │   cli.py     │
      │ 3-column app │        │  terminal    │
      └──────────────┘        └──────────────┘
```

## The pieces

### `config.py` — Settings
Loaded from environment / `.env` with defaults for everything. Designed so
that **browser mode runs with zero configuration**: it attaches to a Chrome
you already have open and reads the feed you already see. `Source` is an enum
(`browser` / `grok` / `mock`).

### `models.py` — the data
Three Pydantic models flow through the whole system:

- **`Post`** — one post pulled from the feed. Carries `views`, `likes`,
  `reposts`, `replies`, `bookmarks`, `has_video`, and computes
  `engagement` and `engagement_rate` (the honest "is this actually good"
  signal — interactions per view).
- **`ScoredPost`** — a `Post` plus a `score` and human-readable `reasons`.
- **`SearchResult`** — everything one search produced; what the UI renders.

### `engine.py` — the conductor
`Engine.run(streamer_name)` is an **async generator** that yields `Line`
objects (`text` + `kind` + optional `result`). It picks the source, drives it,
ranks the output, and emits a live commentary the front-ends animate. Because
both the UI and the CLI consume the same generator, *what you see in the app is
exactly what the terminal prints.*

### `browser/` — attach, don't scrape
- **`session.py`** — `BrowserSession` connects to your Chrome over the
  DevTools Protocol (CDP). Key design choice: **it attaches to a browser you
  already control** instead of launching a headless one. You stay signed in,
  nothing happens behind your back, no API keys, no rate-limit billing. On
  exit it *detaches* rather than closing your browser.
- **`launcher.py`** — `launch_debug_chrome()` finds your Chrome binary and
  starts it with `--remote-debugging-port=9222` and a dedicated profile, so
  the "Connect browser" button works without touching a terminal. Idempotent:
  if a debuggable Chrome already answers, it's reused.

### `scraper/` — walk the feed
- **`feed.py`** — `FeedScraper.for_you()` scrolls the home For You feed,
  extracts every rendered tweet via a single injected JS function
  (`_EXTRACT_JS`), applies the two rules (**streamer in the text** AND
  **views over the floor**), and grabs the canonical link via
  *Share → Copy link*. It yields a `ProgressEvent` per step so the UI can show
  the "flying line of code." After a pass it waits, refreshes, and goes again.
- **`parse.py`** — pure, test-covered helpers: `parse_count("12.3K") → 12300`,
  `parse_status_url(...)`, `canonical_url(...)`.
- **`mock.py`** — realistic bundled sample posts so ClipVein runs with zero
  setup and the ranker behaves the same as it would on live data.

### `ranker/` — decide what's worth clipping
`score.py` blends four transparent signals (reach, engagement quality, video
bonus, freshness) into one number, and attaches the `reasons` that produced
it. A hard **view floor** drops anything below the threshold before it can even
be a candidate. Weights are module-level constants — easy to reason about and
unit-test.

### `integrations/` — the optional `= $` half
- **`grok.py`** — asks Grok (xAI) for the most viral recent posts about a
  streamer, parses its JSON, and normalizes them into `Post` objects so they
  rank identically to browser-found posts.
- **`claude.py`** — hands a `ScoredPost` to Claude, which writes the
  two-line emotional-bait caption. Only imported when a key is present.

### `ui/` — the desktop app
PySide6, three columns: streamer picker · live "how a post is found" console ·
top-3 link cards. The search runs on a background `QThread`
(`ui/worker.py`) that streams engine lines back through Qt signals, so the
window never freezes. A typewriter timer drains queued console lines for the
animated effect.

### `cli.py` — same engine, terminal
`clipvein --streamer "Kai Cenat"` runs the identical engine and prints the
same lines with `rich` colouring, then lists the final links.

## Design principles

1. **Attach, don't scrape.** Use the user's real, logged-in browser. It's more
   honest, more robust, and needs no credentials.
2. **Show your work.** Every step is a visible event; every score carries its
   reasons. No black boxes.
3. **Zero-config default.** It runs on `browser` mode out of the box; keys only
   unlock optional enrichment.
4. **One engine, many faces.** UI and CLI never diverge because they share the
   same async generator.
