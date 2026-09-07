# Prompt library

Every prompt ClipVein sends to a model lives here as a plain file, so you can
read exactly what's being asked, fork it, and tune it. Nothing is hidden in the
code.

```
prompts/
├── grok/     # Grok (xAI) as a "scout" — find viral posts to clip
└── claude/   # Claude (Anthropic) as a "writer" — caption the clip
```

- **Grok = discovery.** It sits on the live X firehose, so it's good at
  *finding* what's already popping off. → [grok/](grok/)
- **Claude = packaging.** It writes the high-retention caption that makes your
  repost land. → [claude/](claude/)

Both are **optional**. ClipVein works fully in `browser` and `mock` mode with no
keys. These prompts only matter if you set `CLIPVEIN_SOURCE=grok` or add an
`ANTHROPIC_API_KEY`.

The versions shipped in the Python code are in
[`clipvein/integrations/grok.py`](../clipvein/integrations/grok.py) and
[`clipvein/integrations/claude.py`](../clipvein/integrations/claude.py). The
files here are the readable, forkable source of truth — keep them in sync when
you tune.
