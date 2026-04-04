---

title: Cascade Failure Env
emoji: 🚨
colorFrom: red
colorTo: yellow
sdk: docker
app_file: app.py
pinned: false
tags:

* openenv

---

# 🚨 DevOps Cascade Failure Prevention Environment

> A real-world OpenEnv benchmark for evaluating AI agents on **incident response in distributed systems** — simulating cascading failures across microservices.

---

## 🧠 Overview

Modern production systems fail due to **cascade effects**: one service slows down, overloads dependencies, and triggers system-wide outages.

Companies like Meta, Google, and AWS lose **millions per minute** during such failures.

This environment simulates that exact scenario.

👉 An AI agent must:

* Monitor system state
* Detect failure propagation
* Take corrective actions (restart / scale / wait)
* Stabilize the system within limited steps

---

## ⚙️ Environment Description

We model a **3-node microservice dependency chain**:

```
Frontend → API → Database
```

Each node transitions through:

| State       | Meaning            |
| ----------- | ------------------ |
| 🟢 healthy  | Normal operation   |
| 🟡 warning  | Degraded           |
| 🔴 critical | Severe degradation |
| ❌ failed    | Fully down         |

---

### 🔁 Failure Propagation

* Database failure → API becomes critical → Frontend becomes warning
* Recovery propagates back upstream gradually

👉 This creates a **realistic cascading failure system**

---

## 📦 Observation Space

```python
class Observation(BaseModel):
    nodes:   Dict[str, str]
    metrics: Dict[str, float]
    logs:    List[str]
```

### Example:

```json
{
  "nodes": {"frontend": "warning", "api": "critical", "database": "failed"},
  "metrics": {"cpu": 90.0, "memory": 95.0, "error_rate": 0.5},
  "logs": ["[ERROR] database failed", "[WARN] api latency spike"]
}
```

---

## 🎮 Action Space

```python
class Action(BaseModel):
    action: str
    target: str
```

| Action          | Effect                                                   |
| --------------- | -------------------------------------------------------- |
| restart_service | Gradual recovery (failed → critical → warning → healthy) |
| scale_up        | Improves state by one level                              |
| do_nothing      | No action (penalized if system unstable)                 |

---

## 🎯 Reward Function

```python
score_map = {
    "healthy": 1.0,
    "warning": 0.6,
    "critical": 0.3,
    "failed": 0.0
}

reward = average(node_scores) - penalty
```

### Key Properties:

* ✅ Dense (step-wise signal, not binary)
* ✅ Encourages gradual recovery
* ❌ Penalizes bad decisions (`do_nothing`)

---

## 🧪 Tasks

### 🟢 Easy — Single Failure Recovery

* Recover system from one failed node
* Strategy: restart → scale remaining
* **Expected score: 1.0**

---

### 🟡 Medium — Partial Degradation

* Mixed states across system
* Requires prioritization
* **Expected score: 0.2 – 0.5**

---

### 🔴 Hard — Full Cascade Recovery

* Multi-step failure propagation
* Requires sequential reasoning
* **Expected score: 0.4 – 0.7**

---

## 📊 Baseline Performance

| Task   | Score   | Behavior                 |
| ------ | ------- | ------------------------ |
| Easy   | 1.0     | Full recovery            |
| Medium | 0.2–0.5 | Partial recovery         |
| Hard   | 0.4–0.7 | Multi-step stabilization |

---

## 🧾 Sample Output

```
[START] task=cascade_failure env=devops model=gpt-4o-mini
[STEP] step=1 action=restart_service:database reward=0.40 done=false
[STEP] step=2 action=scale_up:api reward=0.50 done=false
[STEP] step=3 action=scale_up:database reward=0.60 done=false
[STEP] step=4 action=scale_up:frontend reward=0.73 done=false
[STEP] step=5 action=scale_up:api reward=0.87 done=true
[END] success=true steps=5 score=0.62 rewards=[0.4,0.5,0.6,0.73,0.87]
```

---

## 🔌 Environment API

```python
from environment.env import CascadeEnv

env = CascadeEnv()

obs = env.reset()
obs, reward, done, _ = env.step("restart_service", "database")
state = env.state()
```

---

## 🛠️ Setup & Usage

### Requirements

* Python 3.10+

---

### Clone Repo

```bash
git clone https://github.com/thirthpatel2-web/cascade-failure-env
cd cascade-failure-env
```

---

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

### Set Environment Variables

#### Windows (PowerShell)

```powershell
$env:API_BASE_URL="https://api.openai.com/v1"
$env:MODEL_NAME="gpt-4o-mini"
$env:OPENAI_API_KEY="your_key_here"
$env:HF_TOKEN="dummy"
```

#### Mac/Linux

```bash
export API_BASE_URL="https://api.openai.com/v1"
export MODEL_NAME="gpt-4o-mini"
export OPENAI_API_KEY="your_key_here"
export HF_TOKEN="dummy"
```

---

### ▶️ Run Baseline

```bash
python inference.py
```

---

### 🧪 Run Tasks

```bash
python -c "from tasks.task_easy import run_task; print(run_task())"
python -c "from tasks.task_medium import run_task; print(run_task())"
python -c "from tasks.task_hard import run_task; print(run_task())"
```

---

### 🌐 Run API

```bash
uvicorn app:app --host 0.0.0.0 --port 7860
```

---

### 🐳 Docker

```bash
docker build -t cascade-failure-env .
docker run -p 7860:7860 cascade-failure-env
```

---

## 🚀 Deployment

Hosted on Hugging Face Spaces:

* `/` → `{"status": "running"}`
* `/reset` → returns system observation

---

## 📂 Project Structure

```
cascade-failure-env/
├── environment/
│   ├── env.py
│   └── simulator.py
├── tasks/
│   ├── task_easy.py
│   ├── task_medium.py
│   └── task_hard.py
├── inference.py
├── app.py
├── openenv.yaml
├── Dockerfile
└── README.md
```

---

## 💡 Why This Matters

There is currently **no standard OpenEnv benchmark** for DevOps incident response.

This environment:

* Simulates **real production failures**
* Enables **agent evaluation in infrastructure domains**
* Bridges **AI research with real-world systems**

👉 Direct applications:

* Autonomous incident response agents
* Reliability engineering automation
* AI-based system monitoring

---

## 🏁 Final Statement

> This project introduces a realistic benchmark for **AI-driven system recovery**, modeling how failures propagate and how intelligent agents can intervene to prevent large-scale outages.

---
