import os
from typing import Any, Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover
    OpenAI = None


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str = Field(min_length=1)


class AssistantSettings(BaseModel):
    model: str = "gpt-4.1-mini"
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_output_tokens: int = Field(default=700, ge=64, le=4096)
    system_prompt: str = (
        "You are Nova, a premium AI assistant. Be accurate, concise, and practical."
    )
    api_base_url: str | None = None
    provider: Literal["openai", "custom"] = "openai"
    api_key: str | None = None


class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    settings: AssistantSettings


class ChatResponse(BaseModel):
    content: str
    model: str
    provider: str
    usage: dict[str, Any] = Field(default_factory=dict)
    is_demo: bool = False


app = FastAPI(title="Nova Assistant", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/")
def index() -> FileResponse:
    return FileResponse("app/static/index.html")


def _demo_response(req: ChatRequest) -> ChatResponse:
    user_msg = next((m.content for m in reversed(req.messages) if m.role == "user"), "")
    snippet = user_msg[:240]
    content = (
        "✨ Demo mode is active because no API key is configured.\n\n"
        "Here is a premium-style response template you can customize:\n"
        "1) Goal: clarify the exact outcome in one sentence.\n"
        "2) Strategy: choose the fastest path and list assumptions.\n"
        "3) Action Plan: break into 3-5 concrete steps.\n"
        "4) Quality Check: define how success is measured.\n\n"
        f"Your latest prompt was: \"{snippet}\"\n\n"
        "Set your provider/API key in Settings to enable real AI completions."
    )
    return ChatResponse(
        content=content,
        model=req.settings.model,
        provider=req.settings.provider,
        usage={},
        is_demo=True,
    )


@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    if not req.messages:
        raise HTTPException(status_code=400, detail="messages cannot be empty")

    api_key = req.settings.api_key or os.getenv("OPENAI_API_KEY")
    if OpenAI is None or not api_key:
        return _demo_response(req)

    base_url = req.settings.api_base_url if req.settings.provider == "custom" else None
    client = OpenAI(api_key=api_key, base_url=base_url)

    messages = [{"role": "system", "content": req.settings.system_prompt}]
    messages.extend([m.model_dump() for m in req.messages])

    try:
        completion = client.chat.completions.create(
            model=req.settings.model,
            messages=messages,
            temperature=req.settings.temperature,
            max_tokens=req.settings.max_output_tokens,
        )
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=502, detail=f"Model request failed: {exc}") from exc

    choice = completion.choices[0].message.content if completion.choices else ""
    usage = completion.usage.model_dump() if completion.usage else {}

    return ChatResponse(
        content=choice or "",
        model=req.settings.model,
        provider=req.settings.provider,
        usage=usage,
    )


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
