---
title: Cascade Failure Env
emoji: 🚨
colorFrom: red
colorTo: yellow
sdk: docker
app_file: app.py
pinned: false
tags:
  - openenv
---

# 🚨 DevOps Cascade Failure Prevention Environment

> A real-world OpenEnv benchmark where AI agents act as on-call engineers to detect, diagnose, and recover cascading failures in distributed systems.

---

## 🧠 Overview

Modern distributed systems (like Meta, Google, etc.) often fail due to **cascade failures** — where one failing service overloads others, causing system-wide outages.

This environment simulates that exact scenario.

An AI agent must:

* Monitor system state
* Interpret logs and metrics
* Take corrective actions
* Prevent full system collapse

---

## 🎯 Objective

Evaluate how well an AI agent can:

* Detect failures early
* Understand cascading dependencies
* Take sequential recovery actions
* Restore system stability efficiently

---

## 🏗️ System Architecture

This environment simulates a **12-node microservice system**:

Example services:

* api_gateway
* auth_service
* user_service
* payment_service
* cache_layer
* db_primary
* db_replica
* worker_service
* notification_service
* analytics_service
* frontend
* monitoring

Each service depends on others → failures propagate across the system.

---

## 🔥 Failure States

Each node can be:

| State       | Meaning          |
| ----------- | ---------------- |
| 🟢 healthy  | Normal operation |
| 🟡 warning  | Degrading        |
| 🔴 critical | Severe issue     |
| ❌ failed    | Down             |

Failures propagate through dependencies. Recovery also propagates gradually.

---

## 📥 Observation Space

```python
class Observation(BaseModel):
    nodes: Dict[str, str]
    metrics: Dict[str, float]
    logs: List[str]
```

### Example:

```json
{
  "nodes": {
    "api_gateway": "critical",
    "auth_service": "failed"
  },
  "metrics": {
    "cpu": 92.5,
    "memory": 88.0,
    "error_rate": 0.45
  },
  "logs": [
    "[ERROR] auth_service failed",
    "[WARN] api_gateway latency spike"
  ]
}
```

---

## ⚙️ Action Space

```python
class Action(BaseModel):
    action: str
    target: str
```

| Action          | Description              |
| --------------- | ------------------------ |
| restart_service | Gradual recovery of node |
| scale_up        | Improves node health     |
| do_nothing      | No action (penalized)    |

---

## 🧮 Reward Function

```python
score_map = {
    "healthy": 1.0,
    "warning": 0.6,
    "critical": 0.3,
    "failed": 0.0
}
```

Reward:

* Based on average system health
* Dense (every step gives signal)
* Penalizes bad actions

Range: **0.0 → 1.0**

---

## 🧪 Tasks

### 🟢 Easy

* Single node failure
* Agent recovers system

Expected Score: **~1.0**

---

### 🟡 Medium

* Multiple degraded nodes
* Requires prioritization

Expected Score: **~0.3 – 0.6**

---

### 🔴 Hard

* Full cascade failure
* Multi-step planning required

Expected Score: **~0.5 – 0.8**

---

## 🤖 Baseline Agent

Rule-based agent:

* Fix failed nodes first
* Then critical → warning

---

## 📊 Sample Output

```
[START] task=cascade_failure_prevention env=devops_cascade model=meta-llama/...
[STEP] step=1 action=restart_service(api_gateway) reward=0.35 done=false error=null
[STEP] step=2 action=scale_up(auth_service) reward=0.50 done=false error=null
[STEP] step=3 action=scale_up(cache_layer) reward=0.65 done=false error=null
[STEP] step=4 action=scale_up(frontend) reward=0.80 done=true error=null
[END] success=true steps=4 score=0.65 rewards=0.35,0.50,0.65,0.80
```

---

## 🔁 Environment API

```python
env = CascadeEnv()

obs = env.reset()
obs, reward, done, info = env.step("restart_service", "api_gateway")
state = env.state()
```

---

## ⚙️ Setup

```bash
git clone https://github.com/thirthpatel2-web/cascade-failure-env
cd cascade-failure-env
pip install -r requirements.txt
```

---

## 🔑 Environment Variables

```bash
export API_BASE_URL="https://router.huggingface.co/v1"
export MODEL_NAME="meta-llama/Llama-3.1-8B-Instruct"
export HF_TOKEN="your_token_here"
```

---

## ▶️ Run

```bash
python inference.py
```

---

## 🌐 API Endpoints

| Endpoint | Description       |
| -------- | ----------------- |
| `/`      | Health check      |
| `/reset` | Reset environment |

---

## 🐳 Docker

```bash
docker build -t cascade-env .
docker run -p 7860:7860 cascade-env
```

---

## 📂 Project Structure

```
cascade-failure-env/
├── environment/
│   ├── env.py
│   └── simulator.py
├──server/
|   └── env.py
├── tasks/
│   ├── task_easy.py
│   ├── task_medium.py
│   └── task_hard.py
├── app.py
├── inference.py
├── openenv.yaml
├── pyproject.toml
├── uv.lock
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## 🚀 Why This Project

* Real-world DevOps problem
* Used in production systems
* Strong AI benchmark
* Unique OpenEnv environment

---

## 🏁 Final Status

✅ OpenEnv compliant
✅ Deterministic graders
✅ HF Space deployable
✅ Docker working
✅ Inference reproducible
✅ Validator-ready

---

## 👨‍💻 Author

Built for Meta x HuggingFace OpenEnv Hackathon
DevOps Cascade Failure Simulation
