---
title: Cascade Failure Env
---
# 🚨 DevOps Cascade Failure AI Environment

## 🧠 Overview

This project is a **real-world AI evaluation environment** that simulates cascading failures in distributed systems (frontend → API → database).

An AI agent must:

* Detect system degradation
* Diagnose root cause
* Take corrective action to prevent full system failure

---

## ⚡ Problem

Modern systems (e.g., Instagram, WhatsApp) fail due to **cascade failures**:

> A small failure in one service spreads across dependencies → causing system-wide outages.

This environment models that exact scenario.

---

## 🎯 Objective

Evaluate how well an AI agent can:

* Identify system health
* Understand failure propagation
* Select optimal recovery actions

---

## 🏗️ System Architecture

```
Frontend → API → Database
```

Each node can be:

* 🟢 Healthy
* 🟡 Warning
* 🔴 Critical
* ❌ Failed

Failures propagate across dependencies.

---

## 🧪 Tasks

### 🟢 Easy Task

* Identify system severity from metrics

### 🟡 Medium Task

* Diagnose root cause using logs

### 🔴 Hard Task

* Choose correct recovery action

---

## ⚙️ Actions

The agent can:

* `restart_service`
* `scale_up`
* `do_nothing`

---

## 🧮 Reward Function

```
reward = healthy_nodes / total_nodes
```

* Full recovery → 1.0
* Partial recovery → 0.x

---

## 🔁 Environment API

```python
env.reset()
env.step(action)
env.state()
```

---

## 📊 Example Output

```json
{
  "nodes": {
    "frontend": "warning",
    "api": "critical",
    "database": "failed"
  },
  "metrics": {
    "cpu": 90,
    "memory": 95,
    "error_rate": 0.5
  }
}
```

---

## 📊 Visualization

The system includes a simple visual interface showing real-time service states:

* 🟢 Healthy
* 🟡 Warning
* 🔴 Critical
* ⚫ Failed

This helps visualize how failures propagate across services.

---

## 🚀 Why This Matters

* Real-world DevOps scenario
* Used daily by companies like Meta
* Simulates real incident response workflows
* No standard benchmark exists for cascade failure AI agents

---

## 🏆 Highlights

* Deterministic grading system
* Multi-step reasoning tasks
* Realistic system simulation
* Fully deployable environment

---

## ⚡ Run Locally

```bash
python inference.py
```

---

## 🌍 Deployment

Deployed on Hugging Face Spaces using Docker.

---

## 👨‍💻 Author

Built for AI Hackathon — Cascade Failure Simulation Environment