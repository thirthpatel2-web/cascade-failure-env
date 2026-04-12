# server/app.py  — required entrypoint for OpenEnv validator
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import os
import sys

# Ensure root is on path so environment/ and tasks/ can be imported
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from environment.env import CascadeEnv

app = FastAPI(
    title="Cascade Failure Prevention Environment",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_env: Optional[CascadeEnv] = None


@app.get("/")
def root():
    return {"status": "running", "env_id": "cascade-failure-env", "version": "1.0.0"}


@app.get("/reset")
@app.post("/reset")
def reset():
    global _env
    _env = CascadeEnv(task_level="easy", seed=None)
    obs = _env.reset()
    return JSONResponse(obs.model_dump())


@app.post("/step")
def step(action: str, target: str = "api_gateway"):
    if _env is None:
        return JSONResponse({"error": "Call /reset first"}, status_code=400)
    obs, reward, done, info = _env.step(action, target)
    return JSONResponse({
        "observation": obs.model_dump(),
        "reward": reward.model_dump(),
        "done": done,
        "info": info,
    })


@app.get("/state")
def state():
    if _env is None:
        return JSONResponse({"error": "Call /reset first"}, status_code=400)
    return JSONResponse(_env.state())


@app.get("/tasks")
def tasks():
    return {
        "tasks": [
            {"id": "easy",   "difficulty": "easy",   "max_steps": 15},
            {"id": "medium", "difficulty": "medium",  "max_steps": 20},
            {"id": "hard",   "difficulty": "hard",    "max_steps": 25},
        ]
    }


def main():
    import uvicorn
    uvicorn.run("server.app:app", host="0.0.0.0", port=7860)


if __name__ == "__main__":
    main()