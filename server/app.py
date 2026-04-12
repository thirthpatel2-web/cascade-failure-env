# server/app.py
import os
import sys
from typing import Any, Dict, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from environment.env import CascadeEnv

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

_default_env: Optional[CascadeEnv] = None


# ── Required by openenv validate ──────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "healthy", "service": "cascade-failure-env"}


@app.get("/metadata")
def metadata():
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
    return {
        "action": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["restart_service", "scale_up", "do_nothing"]},
                "target": {"type": "string"},
            },
            "required": ["action", "target"],
        },
        "observation": {
            "type": "object",
            "properties": {
                "nodes": {"type": "object"},
                "metrics": {"type": "object"},
                "logs": {"type": "array"},
                "failed_nodes": {"type": "array"},
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
    return {
        "jsonrpc": "2.0",
        "result": {
            "tools": [
                {"name": "restart_service", "description": "Restart a failed service node"},
                {"name": "scale_up", "description": "Scale up a degraded service node"},
                {"name": "do_nothing", "description": "Take no action this step"},
            ]
        },
        "id": None,
    }


# ── Tasks with graders — THIS IS WHAT THE SCALER VALIDATOR CHECKS ─────────────

@app.get("/tasks")
def tasks():
    return {
        "tasks": [
            {
                "id": "easy",
                "difficulty": "easy",
                "max_steps": 15,
                "description": "Single node failure recovery",
                "grader": "deterministic",
                "grader_function": "graders.run_easy",
                "reward_range": [0.0, 1.0],
            },
            {
                "id": "medium",
                "difficulty": "medium",
                "max_steps": 20,
                "description": "Multi-node degraded state recovery",
                "grader": "deterministic",
                "grader_function": "graders.run_medium",
                "reward_range": [0.0, 1.0],
            },
            {
                "id": "hard",
                "difficulty": "hard",
                "max_steps": 25,
                "description": "Full cascade failure recovery",
                "grader": "deterministic",
                "grader_function": "graders.run_hard",
                "reward_range": [0.0, 1.0],
            },
        ]
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


# ── Entry point ───────────────────────────────────────────────────────────────

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