from __future__ import annotations

import json
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from nexus_core.config import settings
from nexus_core.core.orchestrator import NexusOrchestrator
from nexus_core.event_bus import bus
from nexus_core.memory.store import memory_store
from nexus_core.telemetry import get_system_status
from nexus_core.tools.registry import registry


class ChatRequest(BaseModel):
    message: str


class ToolRequest(BaseModel):
    tool: str
    payload: dict[str, Any] = {}
    approval: bool = False


app = FastAPI(title="NEXUS")
app.mount("/static", StaticFiles(directory="nexus/frontend"), name="static")

orchestrator = NexusOrchestrator(provider_name=settings.ai_provider, model=settings.ai_model)


@app.get("/")
async def index() -> HTMLResponse:
    from pathlib import Path
    html = (Path(__file__).parent / "frontend" / "index.html").read_text(encoding="utf-8")
    return HTMLResponse(content=html)


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/system/status")
async def system_status() -> dict[str, Any]:
    status = get_system_status()
    return {"online": True, "name": "NEXUS", "telemetry": status}


@app.get("/api/tasks")
async def list_tasks() -> dict[str, Any]:
    return {"tasks": [{"id": "task-1", "title": "System boot", "status": "COMPLETED"}]}


@app.post("/api/chat")
async def chat(request: ChatRequest) -> dict[str, Any]:
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")
    result = orchestrator.handle_user_input(request.message)
    return result


@app.post("/api/tools/execute")
async def execute_tool(request: ToolRequest) -> dict[str, Any]:
    result = registry.execute(request.tool, request.payload, approval=request.approval)
    return {"success": result.success, "tool": result.tool, "data": result.data, "error": result.error}


@app.get("/api/memory")
async def list_memory() -> dict[str, Any]:
    return {"items": [item.__dict__ for item in memory_store.list_memories()]}


@app.post("/api/memory")
async def create_memory(payload: dict[str, Any]) -> dict[str, Any]:
    category = payload.get("category", "general")
    content = payload.get("content", "")
    item = memory_store.store_memory(category=category, content=content, metadata=payload.get("metadata", {}))
    return {"stored": True, "item": item.__dict__}


@app.get("/api/events")
async def event_stream():
    def generate():
        yield "event: connected\ndata: {\"status\":\"online\"}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


@app.get("/api/projects")
async def projects() -> dict[str, Any]:
    return {
        "projects": [
            {"name": "Math Master", "path": "./projects/math-master", "status": "active"},
            {"name": "Glow Nuture", "path": "./projects/glow-nuture", "status": "research"},
            {"name": "NEXUS", "path": ".", "status": "active"},
        ]
    }
