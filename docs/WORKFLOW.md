# The clipper workflow

This is the loop ClipVein is built around — from a moment on stream to real,
original views on your own account. The tool automates step 2 (the slow part).
The rest is craft.

```
 1. pick your lane   →  2. FIND with ClipVein  →  3. verify the moment
        ↓                                                  ↓
 6. track & double   ←  5. post at the right time  ←  4. re-cut + re-caption
```

## 1. Pick a lane

Consistency beats spray-and-pray. Pick a streamer (or a tight cluster) and own
that audience. The default roster in `clipvein/streamers.py` is a starting
point — add whoever you're clipping:

```python
Streamer(
    name="Your Streamer",
    handles=("theirhandle",),
    aliases=("nickname", "common clip phrase"),
    accent="#c5f82a",
)
```

Aliases matter: they're the extra words ClipVein looks for in a post's text, so
add the nicknames people actually type.

## 2. Find (ClipVein does this)

```bash
python -m clipvein            # Connect browser → pick streamer → Find clips ▸
```

or headless:

```bash
python -m clipvein.cli --streamer "Kai Cenat" --min-views 200000
```

You get the top 3 links, each with a score and its reasons. **Read the
reasons**, not just the rank:

- **High views + low engagement rate** → big reach but the moment didn't
  *land*. Fine for a quick repost, weak for a narrative clip.
- **Lower views + high engagement rate + fresh** → this is the sleeper. It's
  landing hard and still early. Often the best clip to move on *fast*.
- **`has video`** → clippable as-is. No video means you'd be quoting/screen-
  recording, which is slower.

## 3. Verify the moment

Open the link. Watch it. Ask: *is there a 5–15s beat that stands on its own?*
The best clips are a single spike — a reaction, a line, a fail, a payoff — not a
whole segment. If you can't summarise the hook in one sentence, keep scrolling.

## 4. Re-cut and re-caption

- **Cut to the spike.** Trim dead air before and after. Land on the hook within
  the first second.
- **Vertical (9:16) if you repost to TikTok/Reels/Shorts, native for X.**
  ClipVein finds the moment on X; reposting elsewhere is your own step.
- **Caption is the bait.** This is where Claude comes in — the two-line
  emotional-bait format (teaser line ending in one emoji, then a gut-punch
  quote/question). See [`prompts/claude/`](../prompts/claude/) and the
  `write-streamer-clip-captions` skill.
- **Credit the source.** Tag the streamer / original where appropriate. It's
  good manners, it's often required, and it helps the algorithm connect your
  clip to the moment.

## 5. Post at the right time

A hot moment has a window. Fresh clips (the `fresh` reason in ClipVein) are
worth moving on the same day. Evergreen funny moments can be queued. Post when
*your* audience is awake, not when the streamer was live.

## 6. Track and double down

Keep a simple log: link, caption used, views after 24h / 72h. Patterns show up
fast — which streamer, which caption shape, which time. Feed the winners back
into your lane choice. (A built-in tracker is on the roadmap.)

---

## A realistic run

```bash
$ python -m clipvein.cli --streamer "N3on" --source mock

# target: N3on  (@N3onwastaken)
source = mock
running on bundled sample data
scan @N3onwastaken  views=540,000  vid=True
scan @N3onwastaken  views=1,200,000  vid=True
scan @N3onwastaken  views=95,000  vid=False
...
rank(24 posts, min_views=100,000)
[1] https://x.com/N3onwastaken/status/...  (score 16.9)
[2] https://x.com/N3onwastaken/status/...  (score 15.7)
[3] https://x.com/N3onwastaken/status/...  (score 14.2)
done — 3 link(s) ready

1. https://x.com/N3onwastaken/status/...
2. https://x.com/N3onwastaken/status/...
3. https://x.com/N3onwastaken/status/...
```

Swap `--source mock` for the browser flow and those become live links from your
own feed.

---

## Honest boundaries

ClipVein is a *discovery* tool. It doesn't:

- buy views, likes, or followers;
- run bot/engagement farms;
- auto-post on your behalf without you seeing it;
- bypass any platform's login or paywall.

The views you earn are real people watching a real clip you re-cut well. That's
the whole point — [MONETIZATION.md](MONETIZATION.md) covers how those views turn
into money the legitimate way.
