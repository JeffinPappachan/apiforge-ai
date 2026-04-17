# APIForge AI

APIForge AI is a hackathon-ready full-stack developer tool that turns an API documentation URL into:

- Structured API metadata
- A detected authentication strategy
- A ready-to-use Python SDK
- Example usage code

## Stack

- Backend: FastAPI
- Frontend: Streamlit
- LLM: Groq `llama3-8b-8192`
- Scraping: `requests` + `BeautifulSoup`
- Package manager: `uv`

## Project Structure

```text
apiforge-ai/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── scraper.py
│   ├── parser.py
│   ├── llm.py
│   └── generator.py
├── frontend/
│   └── app.py
├── data/
├── .env
├── pyproject.toml
└── README.md
```

## Setup

1. Install dependencies:

```bash
uv add fastapi uvicorn streamlit beautifulsoup4 requests python-dotenv groq
```

2. Add your Groq key in `.env`:

```env
GROQ_API_KEY=your_groq_api_key_here
BACKEND_URL=http://localhost:8000
```

## Run

Backend:

```bash
uv run uvicorn app.main:app --reload
```

Frontend:

```bash
uv run streamlit run frontend/app.py
```

## API Endpoints

### `POST /process`

Input:

```json
{
  "url": "https://docs.example.com/api"
}
```

Output:

```json
{
  "api": {
    "base_url": "https://api.example.com",
    "auth": "Bearer token",
    "endpoints": [
      {
        "path": "/users",
        "method": "GET",
        "description": "List users",
        "params": ["page", "limit"]
      }
    ]
  },
  "summary": "Short API explanation."
}
```

### `POST /generate`

Input:

```json
{
  "base_url": "https://api.example.com",
  "auth": "Bearer token",
  "endpoints": [
    {
      "path": "/users",
      "method": "GET",
      "description": "List users",
      "params": ["page", "limit"]
    }
  ]
}
```

Output:

```json
{
  "sdk_code": "import requests\\n..."
}
```

## Notes

- Scraped content is cached in `data/` by URL hash to avoid reprocessing the same docs page.
- The backend also memoizes processed URLs during runtime for faster repeated requests.
- The Groq extraction prompt is constrained to strict JSON output with no prose.
- The SDK generator creates an `APIClient` class using `requests`, auth helpers, endpoint methods, and example usage.

## Error Handling

The app surfaces clear messages for:

- Invalid or unreachable URLs
- Missing `GROQ_API_KEY`
- No API endpoints found
- Invalid LLM JSON output
- SDK generation failures
