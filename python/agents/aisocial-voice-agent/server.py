# Copyright 2025 AISocialGrowth
#
# AISocial Voice Agent - FastAPI HTTP Server
# Exposes the ADK agent via REST API endpoints.
# Any frontend, telephony gateway, or voice layer can use this API.

import os
import uuid
from typing import Any, Optional

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from aisocial_voice_agent.agent import root_agent
from aisocial_voice_agent.config import list_available_configs, load_bot_config
from aisocial_voice_agent.tools import get_leads

load_dotenv()

# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------
app = FastAPI(
    title="AISocial Voice Agent API",
    description="REST API for the AISocial config-driven voice/chat agent.",
    version="0.1.0",
)

# ---------------------------------------------------------------------------
# ADK session service and runner
# ---------------------------------------------------------------------------
session_service = InMemorySessionService()
runner = Runner(
    agent=root_agent,
    app_name="aisocial_voice_agent",
    session_service=session_service,
)

# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------


class SessionRequest(BaseModel):
    bot_id: Optional[str] = "default"
    metadata: Optional[dict[str, Any]] = None


class SessionResponse(BaseModel):
    session_id: str
    bot_id: str
    message: str


class ChatRequest(BaseModel):
    session_id: str
    user_id: Optional[str] = "user"
    message: str


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    events: list[dict[str, Any]] = []


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@app.get("/")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "AISocial Voice Agent API",
        "version": "0.1.0",
    }


@app.get("/configs")
async def get_configs():
    """List all available bot configurations."""
    configs = list_available_configs()
    return {"configs": configs, "count": len(configs)}


@app.get("/configs/{bot_id}")
async def get_config(bot_id: str):
    """Get a specific bot configuration."""
    try:
        config = load_bot_config(bot_id)
        return config
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/session", response_model=SessionResponse)
async def create_session(req: SessionRequest):
    """Create a new conversation session."""
    session_id = str(uuid.uuid4())
    user_id = "user"

    session = await session_service.create_session(
        app_name="aisocial_voice_agent",
        user_id=user_id,
        session_id=session_id,
    )

    return SessionResponse(
        session_id=session.id,
        bot_id=req.bot_id or "default",
        message="Session created. Send messages to /chat.",
    )


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """Send a message and get a response from the agent."""
    content = types.Content(
        role="user",
        parts=[types.Part.from_text(text=req.message)],
    )

    events = []
    final_reply = ""

    async for event in runner.run_async(
        user_id=req.user_id or "user",
        session_id=req.session_id,
        new_message=content,
    ):
        if event.is_final_response():
            for part in event.content.parts:
                if part.text:
                    final_reply += part.text
        events.append(
            {
                "author": event.author,
                "is_final": event.is_final_response(),
            }
        )

    return ChatResponse(
        session_id=req.session_id,
        reply=final_reply,
        events=events,
    )


@app.get("/leads")
async def list_leads():
    """Retrieve all saved leads."""
    return get_leads()


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    host = os.getenv("SERVER_HOST", "0.0.0.0")
    port = int(os.getenv("SERVER_PORT", "8000"))
    uvicorn.run(app, host=host, port=port)
