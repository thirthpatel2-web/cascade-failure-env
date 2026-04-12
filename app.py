from fastapi import FastAPI
from fastapi.responses import JSONResponse
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from environment.env import CascadeEnv

app = FastAPI()
env = CascadeEnv()

@app.get("/")
def root():
    return {"status": "running", "environment": "cascade_failure_prevention"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/reset")
def reset():
    obs = env.reset()
    return obs.model_dump() if hasattr(obs, "model_dump") else obs

@app.post("/step")
def step(action: str = "do_nothing", target: str = "api_gateway"):
    obs, reward, done, info = env.step(action, target)
    r = reward if isinstance(reward, float) else float(getattr(reward, "score", getattr(reward, "value", 0.0)))
    return {
        "observation": obs.model_dump() if hasattr(obs, "model_dump") else obs,
        "reward": r,
        "done": done,
        "info": info
    }

@app.get("/state")
def state():
    s = env.state()
    return s.model_dump() if hasattr(s, "model_dump") else s

@app.get("/tasks")
def tasks():
    return {
        "tasks": [
            {"id": "easy",   "description": "Single node failure recovery", "difficulty": "easy"},
            {"id": "medium", "description": "Multi-node degraded state recovery", "difficulty": "medium"},
            {"id": "hard",   "description": "Full cascade failure recovery", "difficulty": "hard"},
        ]
    }

def _get_float(reward):
    if isinstance(reward, (float, int)):
        return float(reward)
    for attr in ("score", "value", "reward", "amount"):
        if hasattr(reward, attr):
            return float(getattr(reward, attr))
    return float(reward)

def _best_action(nodes):
    for node, status in nodes.items():
        if status == "failed":
            return "restart_service", node
    for node, status in nodes.items():
        if status == "critical":
            return "scale_up", node
    for node, status in nodes.items():
        if status == "warning":
            return "scale_up", node
    return "do_nothing", list(nodes.keys())[0]

def _run_episode(max_steps, spread_steps=0):
    e = CascadeEnv(seed=None)
    obs = e.reset()
    for _ in range(spread_steps):
        target = list(obs.nodes.keys())[0]
        obs, _, done, _ = e.step("do_nothing", target)
        if done:
            obs = e.reset()
    total, steps = 0.0, 0
    for _ in range(max_steps):
        action, target = _best_action(obs.nodes)
        obs, reward, done, _ = e.step(action, target)
        total += _get_float(reward)
        steps += 1
        if done:
            break
    return round(min(max(total / max(steps, 1), 0.0), 1.0), 4)

@app.get("/grader")
def grader(task_id: str = "easy"):
    if task_id == "easy":
        score = _run_episode(max_steps=10, spread_steps=0)
    elif task_id == "medium":
        score = _run_episode(max_steps=15, spread_steps=3)
    else:
        score = _run_episode(max_steps=20, spread_steps=6)
    return {"task_id": task_id, "score": score}

@app.get("/baseline")
def baseline():
    easy   = _run_episode(max_steps=10, spread_steps=0)
    medium = _run_episode(max_steps=15, spread_steps=3)
    hard   = _run_episode(max_steps=20, spread_steps=6)
    return {
        "easy":   easy,
        "medium": medium,
        "hard":   hard,
        "average": round((easy + medium + hard) / 3, 4)
    }