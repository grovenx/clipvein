# FAQ & troubleshooting

## General

**Is this a bot that posts for me?**
No. ClipVein is a *discovery* tool. It finds and ranks clips worth reposting;
you do the cutting, captioning and posting. Nothing is posted on your behalf.

**Does it need my X password / an API key?**
No password, ever. In the default `browser` mode it attaches to a Chrome you're
already signed into — it uses your session, it never sees your credentials.
Grok and Claude keys are optional and only unlock the enrichment steps.

**Is scraping my own feed allowed?**
ClipVein reads the feed *you* are already looking at, in *your* browser, at
human speed. That's very different from automated mass-scraping through an API.
Still — platform terms change, so use it responsibly: read your feed, don't
hammer it, and respect any program rules you've signed up to. You are
responsible for how you use it.

**Which platforms?**
X (Twitter) only. ClipVein reads the X For You feed — that's the
source it's built for. Where you *repost* the clip you cut (X, and vertical
platforms like TikTok/Reels/Shorts) is up to you; ClipVein just finds the
source moment on X.

---

## Setup

**`playwright` / browser errors on first run.**
```bash
pip install -r requirements.txt
playwright install chromium
```
The Chromium download is only a fallback engine. In normal use ClipVein
attaches to *your* Chrome (see below).

**"Could not attach to Chrome at http://127.0.0.1:9222".**
A debuggable Chrome isn't running yet. Either click **Connect browser** in the
app, or start one yourself:

```cmd
:: Windows
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="%TEMP%\clipvein-chrome" https://x.com/home
```
```bash
# macOS
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 --user-data-dir=/tmp/clipvein-chrome https://x.com/home
```
Then run the app — it auto-detects the debug port.

**"not signed into X in that Chrome".**
The `--user-data-dir` gives you a fresh, separate Chrome profile. Sign into X
once in that window; the profile is remembered for next time.

**Nothing shows up / no tweets rendered.**
Make sure the For You feed actually has posts about your streamer. Lower
`CLIPVEIN_MIN_VIEWS`, or switch `--source mock` to confirm the pipeline works,
then go back to `browser`.

---

## Results & tuning

**The top link has huge views but feels weak.**
Read the reasons. High views + low engagement rate = big reach, but the moment
didn't land. A lower-view post with high engagement and `fresh` is often the
better clip. Adjust what you value by editing the weights in
`clipvein/ranker/score.py`.

**How do I change what counts as "enough" views?**
`CLIPVEIN_MIN_VIEWS` in `.env`, or `--min-views` on the CLI. Below this floor a
post can't be a candidate at all.

**My streamer isn't in the list.**
Add them to `ROSTER` in `clipvein/streamers.py`. Include their handle(s) and any
nicknames/phrases people type — those aliases are matched against post text.

**Can I get more than 3 links?**
`CLIPVEIN_TOP_N` (the app shows the top 3 as cards; the CLI prints them all).

---

## Grok & Claude

**Do I need them?**
No. `browser` and `mock` work with zero keys. Grok scouts the firehose so you
don't have to scroll; Claude writes the caption. Both are conveniences.

**Grok returned junk / an error.**
ClipVein falls back to mock and tells you. Check `XAI_API_KEY`, and see the
prompt in `prompts/grok/` — you can tune what you ask it for.

**Where are the exact prompts?**
`prompts/grok/` and `prompts/claude/`. They're plain files so you can read, fork
and improve them.

---

## Money

**How do I actually earn?**
See [MONETIZATION.md](MONETIZATION.md). Short version: join streamers' official
clipping bounty programs (pay-per-view), and/or run affiliate links — get paid
for real views you create.

**Is the memecoin thing a real strategy?**
No — driving an audience into a token to skim fees is market manipulation in
many places and gets accounts and repos removed. ClipVein is built for the
durable version: find good moments fast, cut them well, get paid for genuine
attention.
