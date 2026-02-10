"""
FastAPI REST API for the Multi-Agent Customer Service App.
Integrates Google ADK runner with a REST interface.
"""

import os
import uuid
from contextlib import asynccontextmanager

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from agents.orchestrator.agent import root_agent
from database import init_db


# ---------------------------------------------------------------------------
# ADK Runner & Session Service
# ---------------------------------------------------------------------------
APP_NAME = "customer_service"
session_service = InMemorySessionService()
runner = Runner(
    agent=root_agent,
    app_name=APP_NAME,
    session_service=session_service,
)


# ---------------------------------------------------------------------------
# FastAPI lifespan — initialise DB on startup
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Multi-Agent Customer Service API",
    description="REST API backed by Google ADK with 7 specialized agents.",
    version="1.0.0",
    lifespan=lifespan,
)


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------
class UserContext(BaseModel):
    """Optional context passed with requests to populate agent template variables."""
    user_channel: str = ""
    full_name: str = ""
    email: str = ""
    phone: str = ""


class CreateSessionRequest(BaseModel):
    user_id: str = "default_user"
    context: UserContext | None = None


class ChatRequest(BaseModel):
    session_id: str
    message: str
    context: UserContext | None = None


class ChatResponse(BaseModel):
    session_id: str
    response: str
    events: list[dict] | None = None


class SessionResponse(BaseModel):
    session_id: str
    message: str


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}


@app.post("/sessions", response_model=SessionResponse)
async def create_session(request: CreateSessionRequest = None):
    """Create a new conversation session with optional user context."""
    if request is None:
        request = CreateSessionRequest()

    session_id = str(uuid.uuid4())

    # Build initial session state from context
    initial_state = {}
    if request.context:
        initial_state = request.context.model_dump()

    await session_service.create_session(
        app_name=APP_NAME,
        user_id=request.user_id,
        session_id=session_id,
        state=initial_state,
    )
    return SessionResponse(
        session_id=session_id,
        message="Session created successfully.",
    )


@app.get("/sessions/{session_id}")
async def get_session(session_id: str, user_id: str = "default_user"):
    """Get session details and conversation history."""
    session = await session_service.get_session(
        app_name=APP_NAME,
        user_id=user_id,
        session_id=session_id,
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    # Extract conversation history from events
    history = []
    for event in session.events:
        if event.content and event.content.parts:
            text = "".join(
                part.text for part in event.content.parts if hasattr(part, "text") and part.text
            )
            if text:
                history.append({
                    "author": event.author,
                    "text": text,
                })

    return {
        "session_id": session_id,
        "user_id": user_id,
        "history": history,
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Send a message and get the agent's response."""
    # Check session exists
    user_id = "default_user"
    session = await session_service.get_session(
        app_name=APP_NAME,
        user_id=user_id,
        session_id=request.session_id,
    )
    if not session:
        raise HTTPException(
            status_code=404,
            detail="Session not found. Create one first via POST /sessions.",
        )

    # Update session state with any provided context
    if request.context:
        for key, value in request.context.model_dump(exclude_unset=True).items():
            session.state[key] = value

    # Build the user message content
    user_content = types.Content(
        role="user",
        parts=[types.Part.from_text(text=request.message)],
    )

    # Run the agent and collect the response
    final_response_text = ""
    collected_events = []

    async for event in runner.run_async(
        user_id=user_id,
        session_id=request.session_id,
        new_message=user_content,
    ):
        event_data = {
            "author": event.author,
            "is_final": event.is_final_response(),
        }
        if event.content and event.content.parts:
            text = "".join(
                part.text for part in event.content.parts
                if hasattr(part, "text") and part.text
            )
            event_data["text"] = text
            if event.is_final_response() and text:
                final_response_text += text

        collected_events.append(event_data)

    return ChatResponse(
        session_id=request.session_id,
        response=final_response_text or "I'm sorry, I couldn't process that request.",
        events=collected_events,
    )


# ---------------------------------------------------------------------------
# Run with: uvicorn main:app --reload
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
