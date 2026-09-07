# ClipVein — как запустить

Софт написан на **Python + PySide6**. Работает на Windows/macOS/Linux.
Ничего платного не нужно: он подключается к твоему же Chrome и читает ленту,
как это делаю я, когда ты даёшь мне доступ к браузеру.

---

## 1. Установка (один раз)

Нужен Python 3.10+. В папке проекта:

```bash
pip install -r requirements.txt
playwright install chromium
```

> `playwright install chromium` нужен только как запасной браузерный движок.
> В обычном режиме ClipVein цепляется к твоему настоящему Chrome — см. ниже.

---

## 2. Быстрый старт — демо-режим (без браузера)

Чтобы сразу увидеть, как всё работает, на примерных данных:

```bash
# десктоп-приложение
CLIPVEIN_SOURCE=mock python -m clipvein          # macOS/Linux
set CLIPVEIN_SOURCE=mock && python -m clipvein   # Windows (cmd)

# или в терминале, без окна:
python -m clipvein.cli --streamer "Kai Cenat" --source mock
```

Откроется окно: слева выбери стримера → кнопка **Find clips ▸** → по центру
побежит консоль «как ищется пост» → справа появятся 3 ссылки.

---

## 3. Боевой режим — чтение живой ленты через твой Chrome

ClipVein подключается к Chrome по протоколу отладки (CDP) — так он использует
**твою** авторизацию в X и ничего не логинит сам.

**Вариант А (через кнопку в приложении):**
1. Запусти приложение: `python -m clipvein`
2. Нажми **Connect browser** — ClipVein сам откроет отдельный Chrome с
   включённой отладкой.
3. В этом окне Chrome войди в свой X (один раз — профиль сохранится).
4. Выбери стримера → **Find clips ▸**.

**Вариант Б (запустить Chrome вручную):**

Windows:
```cmd
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="%TEMP%\clipvein-chrome" https://x.com/home
```
macOS:
```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 --user-data-dir=/tmp/clipvein-chrome https://x.com/home
```
Затем запусти приложение — оно подцепится к этому Chrome автоматически.

---

## 4. Как это работает (коротко)

```
выбор стримера  →  ClipVein открывает вкладку For You (рекомендации)  →  листает ленту
   →  вытаскивает посты и их метрики (просмотры/лайки/репосты/видео)
   →  ранкер считает score  →  справа 3 лучших ссылки
```

Скоринг честный и прозрачный: reach (log просмотров) + качество
(engagement rate) + бонус за видео (клипабельно) + свежесть. У каждой ссылки
видно, *почему* она попала в топ.

---

## 5. Опционально: Grok и Claude

- **Grok (xAI)** — вместо ручного листания можно попросить Grok найти
  залетевшие посты. Вставь `XAI_API_KEY` в `.env`, поставь `CLIPVEIN_SOURCE=grok`.
- **Claude (Anthropic)** — по найденному посту пишет готовый caption в
  вирусном формате. Вставь `ANTHROPIC_API_KEY` в `.env`.

Скопируй `.env.example` в `.env` и заполни, что нужно. Без ключей всё
работает в режиме `browser`/`mock`.

---

## 6. Настройки (.env)

| Переменная | Что делает | По умолчанию |
|---|---|---|
| `CLIPVEIN_SOURCE` | `browser` / `grok` / `mock` | `browser` |
| `CHROME_CDP_URL` | адрес отладки Chrome | `http://127.0.0.1:9222` |
| `CLIPVEIN_MIN_VIEWS` | порог просмотров | `50000` |
| `CLIPVEIN_TOP_N` | сколько ссылок показывать | `3` |
| `XAI_API_KEY` | ключ Grok (опц.) | — |
| `ANTHROPIC_API_KEY` | ключ Claude (опц.) | — |

---

## 7. Собрать в .exe (Windows, опционально)

```bash
pip install pyinstaller
pyinstaller --noconfirm --windowed --name ClipVein --collect-all PySide6 -m clipvein
```
Готовый `ClipVein.exe` появится в `dist/ClipVein/`.
