# Nova AI Assistant (Gemini-style)

A premium-feeling, fully working, and highly customizable AI assistant web app.

## Features

- Chat interface with polished UI (dark/light themes)
- Custom system prompt/persona
- Model selection
- Temperature + max token controls
- OpenAI provider support
- Custom OpenAI-compatible endpoint support (base URL)
- Local browser settings persistence
- Demo mode fallback when no API key is provided

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Open: <http://localhost:8000>

## Configuration

You can set API key either:

1. In the app Settings panel (saved in your browser localStorage), or
2. As environment variable:

```bash
export OPENAI_API_KEY="your_key"
```

## Tech

- FastAPI backend
- Vanilla HTML/CSS/JS frontend
- OpenAI Python SDK

## Notes

- If no API key is configured, the app runs in **demo mode** and still responds with a useful structured template.
- The app accepts OpenAI-compatible providers when `Provider` is `Custom` and a base URL is set.
