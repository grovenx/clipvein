# ClipVein — how to run

ClipVein is written in **Python + PySide6**. It runs on Windows / macOS / Linux.
Nothing paid is required: it connects to your own Chrome and reads the feed you
already see.

---

## 1. Install (once)

You need Python 3.10+. In the project folder:

```bash
pip install -r requirements.txt
playwright install chromium
```

> `playwright install chromium` is only needed as a fallback browser engine.
> In normal use ClipVein attaches to your real Chrome — see below.

---

## 2. Quick start — demo mode (no browser)

To see how everything works right away, on sample data:

```bash
# desktop app
CLIPVEIN_SOURCE=mock python -m clipvein          # macOS/Linux
set CLIPVEIN_SOURCE=mock && python -m clipvein   # Windows (cmd)

# or in the terminal, no window:
python -m clipvein.cli --streamer "Kai Cenat" --source mock
```

A window opens: pick a streamer on the left → **Find clips ▸** button → in the
middle the console shows *how a post is found* → the right column fills with
3 links.

---

## 3. Live mode — read the real feed through your Chrome

ClipVein connects to Chrome over the DevTools Protocol (CDP), so it uses **your**
own X session and never logs in itself.

**Option A (via the button in the app):**
1. Launch the app: `python -m clipvein`
2. Click **Connect browser** — ClipVein opens a separate Chrome with debugging
   enabled.
3. In that Chrome window, sign into your X (once — the profile is remembered).
4. Pick a streamer → **Find clips ▸**.

**Option B (start Chrome manually):**

Windows:
```cmd
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="%TEMP%\clipvein-chrome" https://x.com/home
```
macOS:
```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 --user-data-dir=/tmp/clipvein-chrome https://x.com/home
```
Then launch the app — it attaches to that Chrome automatically.

---

## 4. How it works (short)

```
pick streamer  →  ClipVein opens the For You tab (recommendations)  →  scrolls the feed
   →  pulls posts and their metrics (views/likes/reposts/video)
   →  the ranker computes a score  →  the best 3 links on the right
```

The scoring is honest and transparent: reach (log of views) + quality
(engagement rate) + a video bonus (clippable) + freshness. Each link shows
*why* it made the top.

---

## 5. Optional: Grok and Claude

- **Grok (xAI)** — instead of scrolling by hand, you can ask Grok to find the
  posts that are popping off. Put `XAI_API_KEY` in `.env`, set
  `CLIPVEIN_SOURCE=grok`.
- **Claude (Anthropic)** — for a found post, it writes a ready caption in the
  viral format. Put `ANTHROPIC_API_KEY` in `.env`.

Copy `.env.example` to `.env` and fill in what you need. With no keys,
everything works in `browser`/`mock` mode.

---

## 6. Settings (.env)

| Variable | What it does | Default |
|---|---|---|
| `CLIPVEIN_SOURCE` | `browser` / `grok` / `mock` | `browser` |
| `CHROME_CDP_URL` | Chrome debug endpoint | `http://127.0.0.1:9222` |
| `CLIPVEIN_MIN_VIEWS` | view floor | `50000` |
| `CLIPVEIN_TOP_N` | how many links to show | `3` |
| `XAI_API_KEY` | Grok key (optional) | — |
| `ANTHROPIC_API_KEY` | Claude key (optional) | — |

---

## 7. Build a .exe (Windows, optional)

```bash
pip install pyinstaller
pyinstaller --noconfirm --windowed --name ClipVein --collect-all PySide6 -m clipvein
```
The finished `ClipVein.exe` appears in `dist/ClipVein/`.
