# WebScout AI

**WebScout AI** is a FastAPI service built for **AZINHACK '26**. It turns a URL and a plain-English goal into a structured scout report by sending a live TinyFish web agent to the page.

You do not write CSS selectors, Playwright scripts, or scraping rules. You describe what to collect. TinyFish opens a remote browser, navigates the site, and returns the result.

---

## The problem

Hackathon and research workflows still spend too much time on brittle scrapers:

- Product pages, news sites, and dashboards load content after JavaScript.
- Layouts change and selectors break.
- Login walls, cookie banners, and geo-restricted pages stall one-off scripts.

WebScout AI is a thin API around TinyFish so a teammate (or another agent) can scout a live site with one POST request.

---

## Features

- **Goal-driven scouting** — send any public URL plus a natural-language goal (`Extract the top 5 headlines as JSON`).
- **Live browser agent** — TinyFish handles clicks, waits, dynamic DOM, and extraction. No local Chrome required.
- **FastAPI surface** — `GET /` for health, `POST /api/scout` for runs, interactive docs at `/docs`.
- **Env-based secrets** — the TinyFish key is loaded from `.env` via `python-dotenv`; it is never hardcoded in source.
- **Honest run status** — the scout endpoint returns TinyFish `status`, `run_id`, `result`, `error`, and `num_of_steps` so you can tell infrastructure success from a failed goal.

---

## TinyFish integration

WebScout AI uses the official **TinyFish Python SDK** (`tinyfish` on PyPI).

| Piece | How WebScout uses it |
| --- | --- |
| Auth | `TINYFISH_API_KEY` in `.env` → `load_dotenv()` → `AsyncTinyFish(api_key=...)` |
| Client | `AsyncTinyFish` (async FastAPI; same API as sync `TinyFish`) |
| Core call | `await client.agent.run(url=..., goal=...)` |
| Result | `AgentRunResponse`: `status`, `run_id`, `result`, `error`, `num_of_steps` |

Equivalent to the SDK quickstart:

```python
from tinyfish import TinyFish

client = TinyFish()  # or TinyFish(api_key=os.getenv("TINYFISH_API_KEY"))
response = client.agent.run(
    goal="What is the current Bitcoin price?",
    url="https://www.coinbase.com/price/bitcoin",
)
print(response.result)
```

On FastAPI we `await` the same method on `AsyncTinyFish`.

### Why TinyFish (not a local scraper)

TinyFish is the web layer for agents: **Search** and **Fetch** for reading pages, and **Agent** when the task needs a real browser (click, type, wait, extract). WebScout's scout path is Agent-first because judges and users will ask for interactive pages, not static HTML dumps.

- Agent runs: **$0.016 / step** (`num_of_steps` is returned on each scout).
- Search / Fetch: free at standard rate limits (useful if you extend the API later).
- API keys: [agent.tinyfish.ai/api-keys](https://agent.tinyfish.ai/api-keys) (`sk-tinyfish-...`).
- Docs: [pypi.org/project/tinyfish](https://pypi.org/project/tinyfish/), [docs.tinyfish.ai](https://docs.tinyfish.ai).

Write **specific goals**. TinyFish reports that precise goals complete much faster and return far less noise than vague ones. Always include what to extract, the output shape, and what **not** to do (for example: do not add to cart, do not submit forms).

---

## Project layout

```
azinhack-project/
├── .env                 # TINYFISH_API_KEY
├── requirements.txt     # fastapi, uvicorn, tinyfish, python-dotenv
├── main.py              # FastAPI app
└── README.md
```

---

## Setup

### 1. Prerequisites

- Python **3.11+** (TinyFish SDK requirement)
- A TinyFish API key from [agent.tinyfish.ai/api-keys](https://agent.tinyfish.ai/api-keys)

### 2. Clone / open the project

```bash
cd azinhack-project
```

### 3. Create a virtual environment

**Windows (PowerShell)**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure the API key

Edit `.env`:

```
TINYFISH_API_KEY=sk-tinyfish-your_key_here
```

Replace the placeholder with your real key. Do not commit a live key.

### 6. Run the server

```bash
uvicorn main:app --reload
```

The API listens on `http://127.0.0.1:8000`. Open `http://127.0.0.1:8000/docs` for Swagger UI.

---

## API

### `GET /`

Returns service metadata and available routes.

```bash
curl http://127.0.0.1:8000/
```

### `POST /api/scout`

Runs a TinyFish agent against a URL with your goal.

**Body**

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `url` | string (HTTP URL) | yes | Page the agent should open |
| `goal` | string | yes | What the agent should do on that page |

**Example**

```bash
curl -X POST http://127.0.0.1:8000/api/scout \
  -H "Content-Type: application/json" \
  -d "{
    \"url\": \"https://news.ycombinator.com\",
    \"goal\": \"Extract the top 5 headlines. Return JSON: [{\\\"title\\\": str, \\\"points\\\": int}]. Do not click links.\"
  }"
```

**Success shape**

```json
{
  "status": "COMPLETED",
  "run_id": "run_...",
  "result": { },
  "error": null,
  "num_of_steps": 4
}
```

**Notes**

- `COMPLETED` means the TinyFish run finished. Always inspect `result` — a completed run can still describe a goal failure (blocked page, missing data).
- Missing or invalid keys return `401`. Rate limits return `429`. Other SDK failures return `502`.

---

## Demo script for judges

1. Start `uvicorn main:app --reload`.
2. Hit `GET /` and show the service is live.
3. Open `/docs`, try `POST /api/scout` with a public news or product URL and a tight JSON goal.
4. Point out `run_id` and `num_of_steps` as proof of a real TinyFish agent run, not a mock.

---

## Built for AZINHACK '26

WebScout AI is a focused hackathon build: one clear product (scout the live web by goal), one serious integration (TinyFish Agent SDK), and a setup path a judge can run in minutes.

---

## License

Hackathon prototype — use and extend for AZINHACK '26.
