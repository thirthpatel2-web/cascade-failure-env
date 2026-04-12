"""
Hard Task: Full cascade failure requiring multi-step sequential recovery.
Expected score: ~0.4 - 0.7
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from environment.env import CascadeEnv


def _get_reward_float(reward) -> float:
    if isinstance(reward, (float, int)):
        return float(reward)
    for attr in ("score", "value", "reward", "amount"):
        if hasattr(reward, attr):
            return float(getattr(reward, attr))
    return float(reward)


def run_task() -> float:
    env = CascadeEnv(seed=None)
    obs = env.reset()

    # Let cascade spread more for hard difficulty
    for _ in range(6):
        target = list(obs.nodes.keys())[0]
        obs, _, done, _ = env.step("do_nothing", target)
        if done:
            obs = env.reset()

    MAX_STEPS = 20
    total_reward = 0.0
    steps_taken = 0
    restarted = set()

    for _ in range(MAX_STEPS):
        nodes = obs.nodes
        action = "do_nothing"
        target = list(nodes.keys())[0]
        found = False

        for node, status in nodes.items():
            if status == "failed" and node not in restarted:
                action = "restart_service"
                target = node
                restarted.add(node)
                found = True
                break

        if not found:
            for node, status in nodes.items():
                if status == "critical":
                    action = "scale_up"
                    target = node
                    found = True
                    break

        if not found:
            for node, status in nodes.items():
                if status == "warning":
                    action = "scale_up"
                    target = node
                    break

        obs, reward, done, info = env.step(action, target)
        total_reward += _get_reward_float(reward)
        steps_taken += 1

        if done:
            break

    if steps_taken == 0:
        return 0.0
    return round(min(max(total_reward / steps_taken, 0.0), 1.0), 4)


if __name__ == "__main__":
    print(f"Hard task score: {run_task()}")