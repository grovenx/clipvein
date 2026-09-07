# Claude caption prompt

**Role:** turn a found post into a ready-to-post, high-retention caption.
**Where it runs:** `clipvein/integrations/claude.py`, when `ANTHROPIC_API_KEY`
is set.
**The format:** two-line emotional-bait — the shape that performs on streamer
clip accounts (Clavicular / Kick-Twitch style).

---

## Prompt (shipped, templated)

```
You write viral captions for streamer clip accounts on X.

Format (exactly):
Line 1: a narrative teaser that creates a curiosity gap, ending in ONE emoji.
Line 2: a gut-punch quote or question on its own line.

Keep it English. No hashtags. No links. Under 200 characters total.

The clip:
- streamer/context: {ctx}
- original post text: {text}
- it already has {views} views

Write 3 caption options, numbered.
```

Claude returns three numbered options; you pick the one that fits the clip.

---

## Anatomy of the format

```
Line 1  →  the TEASER. Sets a scene, promises a payoff, withholds it.
           Ends in exactly ONE emoji (the emoji is punctuation, not decoration).
Line 2  →  the HOOK. A short quote from the clip, or a question that only the
           clip answers. This is the line that makes the thumb stop.
```

**Why it works:** line 1 opens a curiosity gap, line 2 makes not-watching feel
like missing something. No hashtags or links because they leak attention out of
the post before the video earns the click.

---

## Good vs bad (illustrative)

**Good**
```
he did NOT think the mic was still on 😳
"say that again to my face"
```
Teaser sets a situation, one emoji, then a quote that demands the video.

**Bad**
```
Check out this insane clip of the streamer!! 🔥🔥🔥 #clip #viral #fyp link in bio
```
No curiosity gap, emoji spam, hashtags and a link that bleed attention.

---

## Tuning ideas

Fork the prompt to match your lane:

- **Tone:** `Make it deadpan.` / `Make it hype.` / `Make it ominous.`
- **Localise:** `Write the captions in <language>.` (the shipped prompt is
  English by default).
- **Length:** tighten to `Under 120 characters total.` for punchier posts.
- **Options:** ask for `5 caption options` to A/B more.
- **Repost target:** if you repost to a vertical platform (TikTok/Shorts) add
  `Assume a vertical video with on-screen text; keep it readable at a glance.`

---

## The full craft skill

For the complete captioning method — bait patterns, retention rules, and a
Russian mirror of every caption — see the **`write-streamer-clip-captions`**
skill and the end-to-end **[`clip-to-cash`](../../skills/clip-to-cash/)** skill.

---

## Copy-paste version (use Claude directly, no code)

```
You write viral captions for streamer clip accounts on X.

Format (exactly):
Line 1: a narrative teaser that creates a curiosity gap, ending in ONE emoji.
Line 2: a gut-punch quote or question on its own line.

English. No hashtags. No links. Under 200 characters total.

The clip: <describe the moment in one line, e.g. "N3on realises he's been
muted the whole stream">. It already has <N> views.

Give me 3 numbered caption options.
```
