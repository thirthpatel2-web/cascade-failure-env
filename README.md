---
title: Cascade Failure Env
emoji: 🚀
colorFrom: blue
colorTo: green
sdk: docker
app_file: app.py
pinned: false
---

# 🚨 DevOps Cascade Failure AI Environment

> 🚨 A benchmark environment for evaluating AI agents on real-world incident response in distributed systems with cascading failures.

## 🧠 Overview

This project simulates real-world cascading failures in distributed systems (e.g., frontend → API → database).

It is designed as a benchmark environment where AI agents must detect failures, diagnose root causes, and take corrective actions to recover the system efficiently.

## 🚀 Why This Matters

Modern production systems often fail due to cascade effects:

A small issue in one service spreads across dependencies and leads to system-wide outages.

This environment models that exact behavior and enables evaluation of AI agents in production-like scenarios.

## 🎯 Benchmark Objective

Evaluate how well an AI agent can:

* Understand system health
* Interpret logs and metrics
* Handle cascading failures
* Make sequential recovery decisions

## 🏗️ System Architecture

Frontend → API → Database

Each node can be:

* 🟢 Healthy
* 🟡 Warning
* 🔴 Critical
* ❌ Failed

Failures propagate through dependencies.

## 🔥 Key Features

* Multi-step cascade failure simulation
* Dependency-aware failure propagation
* Gradual recovery dynamics (non-instant repair)
* Structured observation space (nodes, metrics, logs)
* Deterministic and interpretable reward function
* Supports evaluation of decision-making agents

## ⚠️ Why This Problem is Hard

* Failures propagate across dependencies
* Partial observability using logs and metrics
* Multiple valid actions with different outcomes
* Requires multi-step planning, not single-step fixes

## ⚙️ Actions

The agent can perform:

* restart_service
* scale_up
* do_nothing

## 🧮 Reward Function

Reward reflects system health quality:

* Healthy → highest score
* Warning / Critical → partial score
* Failed → lowest score
* Poor decisions are penalized

This encourages gradual recovery and intelligent action selection.

## 🔁 Environment API

env.reset()
env.step(action)
env.state()

## 📊 Sample Output

--- Step 1 ---
Action: restart_service on database
Reward: 0.4

--- Step 2 ---
Action: scale_up on api
Reward: 0.5

--- Step 3 ---
Action: scale_up on database
Reward: 0.6

--- Step 4 ---
Action: scale_up on frontend
Reward: 0.73

--- Step 5 ---
Action: scale_up on api
Reward: 0.86

Final:
Total Reward: 3.1
Normalized Score: 0.62

## 📊 Baseline Performance

A simple rule-based agent achieves:

* Easy Task → 1.0
* Medium Task → ~0.8
* Hard Task → ~0.6

## ⚡ Run Locally

python inference.py

## 🌍 Deployment

Deployed on Hugging Face Spaces using Docker.

## 🧠 Insight

This environment models incident response as a sequential decision-making problem, bridging reinforcement learning with real-world DevOps systems.

## 👨‍💻 Author

Built for AI Hackathon — Cascade Failure Simulation Environment
