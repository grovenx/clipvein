# Grok scout prompt

**Role:** find the streamer clips that are already going viral, so ClipVein can
rank them.
**Where it runs:** `clipvein/integrations/grok.py`, when `CLIPVEIN_SOURCE=grok`.
**Why Grok:** it has native access to the live X feed, which makes it a natural
scout — instead of scrolling yourself, you ask Grok what's popping off.

---

## System prompt (shipped)

```
You are a scout for a clip-hunting tool. Given a streamer, return the most
viral recent X posts/clips about or from them. Respond ONLY with a JSON array;
each item: {"url": str, "handle": str, "views": int, "text": str,
"has_video": bool}. No prose.
```

## User prompt (shipped, templated)

```
Streamer: {name} (handles: {handles}).
Return up to {limit} of the most viral recent posts/clips. JSON only.
```

ClipVein then parses the JSON, normalizes each item into a `Post`, and runs it
through the same ranker as browser-found posts. Grok rarely returns full
engagement metrics, so the code estimates them conservatively from views.

---

## Why it's shaped this way

- **JSON-only, no prose** — the output is parsed by code, so any prose breaks
  it. The system prompt hammers this; the parser also strips markdown fences and
  digs a `[...]` array out of messy replies as a fallback.
- **"about or from them"** — you want both the streamer's own posts *and*
  clip-account reposts of their moments; both are clippable.
- **"recent"** — hot windows are short. Old virals are already saturated.
- **Low temperature (0.2)** — you want recall of real posts, not creativity.

---

## Tuning ideas

Fork the system/user prompt to bias the scout:

- **Only video:** add `Only include posts that contain video.`
- **Minimum reach:** add `Only include posts with more than 200k views.`
- **Freshness:** add `Only posts from the last 48 hours.`
- **Niche:** add `Prefer funny/reaction moments over announcements.`
- **More candidates:** raise `limit` (the user prompt's `{limit}`).

Keep the JSON schema line intact — the parser depends on those exact keys
(`url`, `handle`, `views`, `text`, `has_video`).

---

## Copy-paste version (use Grok directly, no code)

If you just want to ask Grok by hand in the X app or console:

```
You are a scout for a clip-hunting tool. Find the most viral recent X
posts/clips about or from the streamer <STREAMER NAME> (handle @<HANDLE>).

Return up to 12 items as a JSON array only — no prose. Each item:
{"url": "<link to the post>", "handle": "<author handle>",
 "views": <integer>, "text": "<post text>", "has_video": <true|false>}

Rules: real posts only, prefer video, prefer the last 72 hours, sort by views
descending.
```

Then paste the links into ClipVein (or just start cutting the top ones).
