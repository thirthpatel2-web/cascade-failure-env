"""
Inference Script — Cascade Failure Prevention (12-node)
Uses LLM via provided API_BASE_URL and API_KEY to choose actions.
"""

import os
import json
from typing import List, Optional

from openai import OpenAI
from environment.env import CascadeEnv

# ── MUST use injected env vars exactly as specified ───────────────────────────
API_KEY      = os.environ.get("API_KEY") or os.environ.get("HF_TOKEN") or "dummy"
API_BASE_URL = os.environ.get("API_BASE_URL") or "https://router.huggingface.co/v1"
MODEL_NAME   = os.environ.get("MODEL_NAME") or "meta-llama/Llama-3.1-8B-Instruct"

TASK_NAME  = "cascade_failure_prevention"
BENCHMARK  = "devops_cascade"
MAX_STEPS  = 20
SUCCESS_SCORE_THRESHOLD = 0.4

VALID_ACTIONS = ["restart_service", "scale_up", "do_nothing"]
NODE_PRIORITY = [
    "api_gateway", "db_primary", "payment_svc", "auth_service",
    "cache_layer", "user_service", "order_service", "db_replica",
    "search_svc", "inventory_svc", "message_queue", "notification",
]

SYSTEM_PROMPT = """You are an AI SRE agent managing a 12-node microservice system.

Nodes: api_gateway, auth_service, user_service, order_service, payment_svc,
inventory_svc, notification, search_svc, cache_layer, db_primary, db_replica, message_queue

Node states: healthy, warning, critical, failed
Dependencies: api_gateway → auth_service, user_service, order_service, search_svc
              order_service → payment_svc, inventory_svc, message_queue
              payment_svc → db_primary
              user_service → cache_layer, db_primary
              cache_layer → db_primary
              db_primary → db_replica
              message_queue → notification

Actions:
- restart_service(node): Gradually recovers a failed node (failed→critical→warning→healthy over steps)
- scale_up(node): Improves a node one severity level
- do_nothing: No action (penalized if failures active)

Strategy: Fix failed nodes first, then critical, then warning. Target highest-criticality nodes.

You must respond with ONLY a valid JSON object like:
{"action": "restart_service", "target": "db_primary"}

No explanation. No markdown. Just the JSON."""


def log_start(task, env, model):
    print(f"[START] task={task} env={env} model={model}", flush=True)

def log_step(step, action, reward, done, error):
    print(f"[STEP] step={step} action={action} reward={reward:.2f} done={str(done).lower()} error={error or 'null'}", flush=True)

def log_end(success, steps, score, rewards):
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.2f} rewards={','.join(f'{r:.2f}' for r in rewards)}", flush=True)


def fallback_action(obs):
    """Rule-based fallback if LLM call fails."""
    for node in NODE_PRIORITY:
        if obs.nodes.get(node) == "failed":
            return "restart_service", node
    for node in NODE_PRIORITY:
        if obs.nodes.get(node) == "critical":
            return "scale_up", node
    for node in NODE_PRIORITY:
        if obs.nodes.get(node) == "warning":
            return "scale_up", node
    return "do_nothing", "api_gateway"


def get_llm_action(client: OpenAI, obs, step: int):
    """Ask LLM to choose next action based on system state."""
    user_prompt = f"""Step {step} — Current system state:

Nodes: {json.dumps(obs.nodes, indent=2)}
Metrics: cpu={obs.metrics.get('cpu', 0):.1f}% memory={obs.metrics.get('memory', 0):.1f}% error_rate={obs.metrics.get('error_rate', 0):.2f}
Failed nodes: {obs.failed_nodes}
Steps remaining: {obs.time_remaining}

Choose the best action to recover the system. Respond with JSON only:
{{"action": "restart_service", "target": "node_name"}}"""

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": user_prompt},
            ],
            max_tokens=50,
            temperature=0.0,
        )
        text = response.choices[0].message.content.strip()

        # Strip markdown code fences if present
        text = text.replace("```json", "").replace("```", "").strip()

        parsed = json.loads(text)
        action = parsed.get("action", "do_nothing")
        target = parsed.get("target", "api_gateway")

        # Validate action
        if action not in VALID_ACTIONS:
            action = "do_nothing"
        if target not in NODE_PRIORITY:
            target = "api_gateway"

        return action, target, None

    except Exception as e:
        # Fallback to rule-based if LLM fails
        action, target = fallback_action(obs)
        return action, target, str(e)


def main():
    # Initialize OpenAI client with injected credentials
    client = OpenAI(
        base_url=API_BASE_URL,
        api_key=API_KEY,
    )

    rewards, steps_taken, score, success = [], 0, 0.0, False
    obs = None

    log_start(task=TASK_NAME, env=BENCHMARK, model=MODEL_NAME)

    try:
        env = CascadeEnv(task_level="hard", seed=None)
        obs = env.reset()

        for step in range(1, MAX_STEPS + 1):
            action, target, error = get_llm_action(client, obs, step)

            obs, reward_obj, done, info = env.step(action, target)

            reward = reward_obj.value
            rewards.append(reward)
            steps_taken = step

            log_step(
                step=step,
                action=f"{action}({target})",
                reward=reward,
                done=done,
                error=error,
            )

            if done:
                break

        steps_taken = max(steps_taken, 1)
        score       = min(max(sum(rewards) / steps_taken, 0.0), 1.0)
        success     = score >= SUCCESS_SCORE_THRESHOLD

    except Exception as exc:
        print(f"[DEBUG] Episode error: {exc}", flush=True)

    finally:
        log_end(success=success, steps=steps_taken, score=score, rewards=rewards)


if __name__ == "__main__":
    main()