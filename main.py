"""
Main FastAPI server for DeskMate.
Handles chat requests and demo APIs.
"""

import os
from pathlib import Path

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import logger
from llm import run_agent
from mock_data import USERS

load_dotenv()

app = FastAPI(
    title="DeskMate — AI IT Helpdesk",
    description="AI-powered IT helpdesk assistant demo",
    version="1.0.0",
)

# Serve frontend
app.mount("/static", StaticFiles(directory="static"), name="static")

# stores chat history for each session
_sessions: dict[str, list[dict]] = {}


# Request/response models

class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"
    employee_id: str = "EMP001"


class ChatResponse(BaseModel):
    response: str
    session_id: str
    employee_id: str
    trace: list


# API routes

@app.get("/", include_in_schema=False)
async def serve_ui():
    ui_path = Path("static/index.html")
    if not ui_path.exists():
        raise HTTPException(status_code=404, detail="Frontend not found.")
    return FileResponse(ui_path)


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    logger.log(
        f"[/chat] session={req.session_id} employee={req.employee_id} "
        f"msg={req.message[:80]!r}"
    )

    history = _sessions.setdefault(req.session_id, [])

    try:
        result = run_agent(
            user_message=req.message,
            conversation_history=history,
            employee_id=req.employee_id,
        )
    except RuntimeError as e:
        # Missing API key or similar config error
        logger.log(f"[/chat] Config error: {e}", level="error")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.log(f"[/chat] Unexpected error: {e}", level="error")
        if "429" in str(e) or "rate limit" in str(e).lower():
            raise HTTPException(
                status_code=429,
                detail="DeskMate is busy right now. Please wait 30 seconds and try again.",
            )
        raise HTTPException(
            status_code=500,
            detail="DeskMate encountered an internal error. Please try again.",
        )

    # keep recent messages only in session history to limit memory usage
    history.append({"role": "user", "content": req.message})
    history.append({"role": "assistant", "content": result["response"]})
    if len(history) > 20:
        _sessions[req.session_id] = history[-20:]

    return ChatResponse(
        response=result["response"],
        session_id=req.session_id,
        employee_id=req.employee_id,
        trace=result["trace"],
    )


@app.get("/trace")
async def get_trace():
    """Returns execution logs."""
    return JSONResponse({"logs": logger.get_logs()})


@app.get("/employees")
async def list_employees():
    """Helper endpoint for the demo UI to populate the employee selector."""
    return {
        "employees": [
            {
                "employee_id": uid,
                "name": u["name"],
                "department": u["department"],
                "role": u["role"],
            }
            for uid, u in USERS.items()
        ]
    }


@app.delete("/session/{session_id}")
async def clear_session(session_id: str):
    _sessions.pop(session_id, None)
    logger.log(f"[/session] Cleared session: {session_id}")
    return {"status": "cleared", "session_id": session_id}


@app.get("/health")
async def health():
    return {"status": "ok", "model": "mistral-small-latest"}


# Run server

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
