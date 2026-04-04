"""
Inference Script — Cascade Failure Prevention Environment
===================================
MANDATORY
- Before submitting, ensure the following variables are defined in your environment configuration:
    API_BASE_URL   The API endpoint for the LLM.
    MODEL_NAME     The model identifier to use for inference.
    HF_TOKEN       Your Hugging Face / API key.

- The inference script must be named `inference.py` and placed in the root directory of the project
- Participants must use OpenAI Client for all LLM calls using above variables

STDOUT FORMAT (strictly followed — matches official sample)
    [START] task=<task_name> env=<benchmark> model=<model_name>
    [STEP]  step=<n> action=<action_str> reward=<0.00> done=<true|false> error=<msg|null>
    [END]   success=<true|false> steps=<n> score=<score> rewards=<r1,r2,...,rn>
"""

import os
from typing import List, Optional

from openai import OpenAI

from environment.env import CascadeEnv

# ── Required env vars ────────────────────────────────────────────────────────
API_KEY = os.getenv("HF_TOKEN") or os.getenv("API_KEY") or "dummy"
API_BASE_URL = os.getenv("API_BASE_URL") or "https://router.huggingface.co/v1"
MODEL_NAME   = os.getenv("MODEL_NAME")   or "meta-llama/Llama-3.1-8B-Instruct"

TASK_NAME  = "cascade_failure_prevention"
BENCHMARK  = "devops_cascade"
MAX_STEPS  = 10
SUCCESS_SCORE_THRESHOLD = 0.4  # normalized score in [0, 1]


# ── Exact log helpers — matching official sample format ──────────────────────

def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    error_val = error if error else "null"
    done_val  = str(done).lower()
    print(
        f"[STEP] step={step} action={action} reward={reward:.2f} done={done_val} error={error_val}",
        flush=True,
    )


def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(
        f"[END] success={str(success).lower()} steps={steps} score={score:.2f} rewards={rewards_str}",
        flush=True,
    )


# ── Agent logic ───────────────────────────────────────────────────────────────

def choose_action(observation) -> tuple:
    """
    Rule-based agent. Prioritises failed → critical → warning nodes.
    Returns (action_str, target_node) tuple.
    """
    nodes = observation.nodes

    for node, state in nodes.items():
        if state == "failed":
            return "restart_service", node

    for node, state in nodes.items():
        if state == "critical":
            return "scale_up", node

    for node, state in nodes.items():
        if state == "warning":
            return "scale_up", node

    return "do_nothing", "database"


def format_action(action: str, target: str) -> str:
    """Format action as a readable string for the [STEP] log."""
    return f"{action}({target})"


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    # Initialize OpenAI client (required by spec — even if agent is rule-based)
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)  # noqa: F841

    rewards:     List[float] = []
    steps_taken: int         = 0
    score:       float       = 0.0
    success:     bool        = False
    obs                      = None

    log_start(task=TASK_NAME, env=BENCHMARK, model=MODEL_NAME)

    try:
        env = CascadeEnv()
        obs = env.reset()

        for step in range(1, MAX_STEPS + 1):
            action, target = choose_action(obs)
            action_str     = format_action(action, target)

            obs, reward_obj, done, info = env.step(action, target)

            reward = reward_obj.value
            error  = None                    # no last_action_error in this env

            rewards.append(reward)
            steps_taken = step

            log_step(
                step   = step,
                action = action_str,
                reward = reward,
                done   = done,
                error  = error,
            )

            if done:
                break

        # Normalize score to [0, 1]
        max_possible = steps_taken * 1.0
        score = min(max(sum(rewards) / max_possible, 0.0), 1.0)
        success = score >= SUCCESS_SCORE_THRESHOLD

    except Exception as exc:
        print(f"[DEBUG] Episode error: {exc}", flush=True)

    finally:
        # Always emit [END] — even on exception (matches official sample)
        log_end(success=success, steps=steps_taken, score=score, rewards=rewards)


if __name__ == "__main__":
    main()