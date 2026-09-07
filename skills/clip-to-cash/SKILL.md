---
name: clip-to-cash
description: End-to-end workflow that takes a viral streamer post found by ClipVein and turns it into a re-cut, re-captioned clip ready to post and monetize. Use when you have a link (or a ClipVein result) and want the full "found moment → posted clip → paid" loop, including caption generation in the two-line emotional-bait format.
---

# clip-to-cash

Turn a moment ClipVein found into money the legitimate way: a well-cut,
well-captioned repost that earns real, original views and qualifies for
clipping-bounty and affiliate payouts.

This skill assumes ClipVein already handed you the *finding* (the top links).
It covers everything after: verify → cut → caption → post → get paid.

## When to use

- You have a ClipVein result (top 3 links) or any single viral post link.
- You want a repeatable checklist, not a one-off.
- You need the caption written in the high-retention two-line format.

## Inputs you need

- The post link (from ClipVein's browser/grok/mock run).
- The streamer's name + which clipping program you're submitting to (if any).
- Your target platform(s): X, TikTok, YouTube Shorts, Reels.

## The loop

### 1. Verify the moment
Open the link, watch it. Confirm there's a **5–15s self-contained beat** — a
reaction, a line, a fail, a payoff. If you can't state the hook in one sentence,
skip it and take the next ClipVein link. Prefer results whose reasons include
`has video` and `fresh`; a high-engagement-rate sleeper beats a high-view flat
one.

### 2. Cut to the spike
- Trim dead air; land on the hook inside the first second.
- Vertical (9:16) for TikTok/Shorts/Reels; native aspect for X.
- Keep it tight — retention is the whole game.
- Add on-screen text for the hook if the platform is muted-autoplay.

### 3. Caption in the two-line format
Ask Claude (or use `prompts/claude/caption.md`) for the emotional-bait shape:

```
Line 1: narrative teaser, curiosity gap, ends in ONE emoji.
Line 2: gut-punch quote or question on its own line.
No hashtags. No links. Under 200 characters.
```

If the `write-streamer-clip-captions` skill is available, use it — it also
mirrors each caption in Russian and gives bait patterns.

Generate 3 options, pick the one that matches the clip's energy.

### 4. Credit and comply
- Tag/credit the streamer or original where required.
- Read the clipping program's rules **before** posting: min length, required
  tags, allowed platforms, watermark/credit, banned content, no re-uploading
  other clippers' edits. Your edit must be genuinely yours.

### 5. Post at the right time
- Fresh moments: same day.
- Post when *your* audience is online.
- One platform-native upload per platform (don't cross-post the same file if a
  program forbids it).

### 6. Submit and log
- Submit the link to the bounty program if you're in one.
- Log: link, caption used, platform, views at 24h / 72h.
- After ~2 weeks, double down on the winning streamer / caption shape / time.

## Monetization paths (see docs/MONETIZATION.md)

- **Clipping bounties** — pay-per-view / per-approved-clip from the streamer's
  official program.
- **Affiliate / referral** — a cut of sign-ups or sales your clips drive.
- **Creator funds & sponsorship** — once your account has real reach.

## Hard rules (stay eligible and out of trouble)

- No bought views / bots / engagement farms — instant demonetization + bans.
- No stolen edits or captions — gets you kicked from programs, risks strikes.
- No misleading bait — trips "misleading content" rules, tanks retention.
- No pump-and-dump / memecoin funneling — market manipulation in many
  jurisdictions; gets accounts and repos removed. This skill will not help with
  it. The durable money is real attention, cut well.

## Quick reference

```
ClipVein top link
   → verify 5–15s hook
   → cut to the spike (9:16 or native)
   → Claude caption (2-line bait, 1 emoji, no #, no link)
   → credit + program rules
   → post at your audience's peak
   → submit + log 24h/72h views
   → double down on winners
```
