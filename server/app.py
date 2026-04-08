import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from environment.env import CascadeEnv
from environment.simulator import NODES

app = FastAPI(
    title="Cascade Failure Prevention Environment",
    description="OpenEnv-compliant 12-node microservice cascade failure simulation",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_env: Optional[CascadeEnv] = None


class StepRequest(BaseModel):
    action: str
    target: str = "api_gateway"


@app.get("/")
def root():
    return {"status": "running", "nodes": len(NODES), "version": "2.0.0"}


@app.post("/reset")
def reset_post():
    global _env
    _env = CascadeEnv(task_level="easy", seed=None)
    obs = _env.reset()
    return JSONResponse(obs.model_dump())


@app.get("/reset")
def reset_get():
    global _env
    _env = CascadeEnv(task_level="easy", seed=None)
    obs = _env.reset()
    return JSONResponse(obs.model_dump())


@app.post("/step")
def step(req: StepRequest):
    if _env is None:
        return JSONResponse({"error": "Call /reset first"}, status_code=400)
    obs, reward, done, info = _env.step(req.action, req.target)
    return JSONResponse({
        "observation": obs.model_dump(),
        "reward":      reward.model_dump(),
        "done":        done,
        "info":        info,
    })


@app.get("/state")
def state():
    if _env is None:
        return JSONResponse({"error": "Call /reset first"}, status_code=400)
    return JSONResponse(_env.state())


@app.get("/health")
def health():
    return {"status": "ok", "nodes": list(NODES.keys())}


def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)


if __name__ == "__main__":
    main()