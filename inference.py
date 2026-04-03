# inference.py

import os
from openai import OpenAI
from environment.env import CascadeEnv

# Required environment variables
API_BASE_URL = os.getenv("API_BASE_URL")
MODEL_NAME = os.getenv("MODEL_NAME")
API_KEY = os.getenv("OPENAI_API_KEY")

MAX_STEPS = 5


def choose_action(observation):
    """
    Simple rule-based agent (no LLM dependency needed)
    """

    nodes = observation.nodes  # ✅ FIXED

    # Priority 1: Fix failed
    for node, state in nodes.items():
        if state == "failed":
            return "restart_service", node

    # Priority 2: Handle critical
    for node, state in nodes.items():
        if state == "critical":
            return "scale_up", node

    # Priority 3: Handle warning
    for node, state in nodes.items():
        if state == "warning":
            return "scale_up", node

    return "do_nothing", "database"


def main():
    # Initialize OpenAI client (required by spec)
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)

    env = CascadeEnv()

    rewards = []
    steps_taken = 0

    # 🔥 START LOG
    print(f"[START] task=cascade_failure env=devops model={MODEL_NAME}")

    obs = env.reset()

    for step in range(1, MAX_STEPS + 1):
        action, target = choose_action(obs)

        obs, reward, done, _ = env.step(action, target)

        reward_value = reward.value  # ✅ FIXED

        rewards.append(reward_value)
        steps_taken = step

        # 🔥 STEP LOG
        print(f"[STEP] step={step} action={action}:{target} reward={round(reward_value,3)} done={done}")

        if done:
            break

    # Normalize score (0–1)
    total_reward = sum(rewards)
    max_possible = MAX_STEPS * 1.0
    score = min(max(total_reward / max_possible, 0.0), 1.0)

    # ✅ FIXED SUCCESS LOGIC
    success = all(state == "healthy" for state in obs.nodes.values())

    # 🔥 END LOG
    print(f"[END] success={success} steps={steps_taken} score={round(score,3)} rewards={rewards}")


if __name__ == "__main__":
    main()