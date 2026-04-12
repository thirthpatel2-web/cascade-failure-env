# server/app.py — Full OpenEnv-compliant server
import os
import sys
import uuid
from typing import Any, Dict, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from environment.env import CascadeEnv

# ── FastAPI app ───────────────────────────────────────────────────────────────

app = FastAPI(
    title="Cascade Failure Prevention Environment",
    description="OpenEnv environment for DevOps cascade failure prevention",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Session store: episode_id → CascadeEnv instance
_sessions: Dict[str, CascadeEnv] = {}
_default_env: Optional[CascadeEnv] = None


# ── OpenEnv required endpoints ────────────────────────────────────────────────

@app.get("/health")
def health():
    """Required by openenv validate."""
    return {"status": "healthy", "service": "cascade-failure-env"}


@app.get("/metadata")
def metadata():
    """Required by openenv validate — must return name and description."""
    return {
        "name": "cascade-failure-env",
        "description": (
            "A real-world DevOps environment where an AI agent monitors 12 "
            "interconnected microservices and must prevent cascade failures."
        ),
        "version": "1.0.0",
        "tasks": ["easy", "medium", "hard"],
    }


@app.get("/schema")
def schema():
    """Required by openenv validate — must return action, observation, state schemas."""
    return {
        "action": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["restart_service", "scale_up", "do_nothing"],
                    "description": "Action to take on the target node",
                },
                "target": {
                    "type": "string",
                    "description": "Node to act on",
                },
            },
            "required": ["action", "target"],
        },
        "observation": {
            "type": "object",
            "properties": {
                "nodes": {"type": "object", "description": "Node health states"},
                "metrics": {"type": "object", "description": "System metrics"},
                "logs": {"type": "array", "description": "Recent log entries"},
                "failed_nodes": {"type": "array", "description": "Currently failed nodes"},
                "step": {"type": "integer"},
                "time_remaining": {"type": "integer"},
            },
        },
        "state": {
            "type": "object",
            "properties": {
                "task_level": {"type": "string"},
                "step": {"type": "integer"},
                "done": {"type": "boolean"},
                "system_health": {"type": "number"},
                "nodes": {"type": "object"},
            },
        },
    }


@app.post("/mcp")
def mcp(body: dict = None):
    """Required by openenv validate — JSON-RPC 2.0 endpoint."""
    return {
        "jsonrpc": "2.0",
        "result": {
            "tools": [
                {
                    "name": "restart_service",
                    "description": "Restart a failed service node",
                    "inputSchema": {
                        "type": "object",
                        "properties": {"target": {"type": "string"}},
                        "required": ["target"],
                    },
                },
                {
                    "name": "scale_up",
                    "description": "Scale up a degraded service node",
                    "inputSchema": {
                        "type": "object",
                        "properties": {"target": {"type": "string"}},
                        "required": ["target"],
                    },
                },
                {
                    "name": "do_nothing",
                    "description": "Take no action this step",
                    "inputSchema": {"type": "object", "properties": {}},
                },
            ]
        },
        "id": None,
    }


# ── Standard OpenEnv endpoints ────────────────────────────────────────────────

@app.get("/")
def root():
    return {"status": "running", "env": "cascade-failure-env", "version": "1.0.0"}


@app.get("/reset")
@app.post("/reset")
def reset(task_level: str = "easy"):
    global _default_env
    _default_env = CascadeEnv(task_level=task_level, seed=None)
    obs = _default_env.reset()
    return JSONResponse(obs.model_dump())


@app.post("/step")
def step(action: str = "do_nothing", target: str = "api_gateway"):
    global _default_env
    if _default_env is None:
        _default_env = CascadeEnv(task_level="easy", seed=None)
        _default_env.reset()
    obs, reward, done, info = _default_env.step(action, target)
    return JSONResponse({
        "observation": obs.model_dump(),
        "reward": reward.model_dump(),
        "done": done,
        "info": info,
    })


@app.get("/state")
def state():
    global _default_env
    if _default_env is None:
        return JSONResponse({"error": "Call /reset first"}, status_code=400)
    return JSONResponse(_default_env.state())


@app.get("/tasks")
def tasks():
    return {
        "tasks": [
            {"id": "easy",   "difficulty": "easy",   "max_steps": 15, "description": "Single node failure recovery"},
            {"id": "medium", "difficulty": "medium",  "max_steps": 20, "description": "Multi-node degraded state recovery"},
            {"id": "hard",   "difficulty": "hard",    "max_steps": 25, "description": "Full cascade failure recovery"},
        ]
    }


# ── Entry point (required by pyproject.toml [project.scripts] server=server.app:main) ──

def main():
    import uvicorn
    uvicorn.run(
        "server.app:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 7860)),
        reload=False,
    )


if __name__ == "__main__":
    main()