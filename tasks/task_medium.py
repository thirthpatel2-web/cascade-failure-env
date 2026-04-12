"""
Medium Task: Multi-node degraded state recovery.
Expected score: ~0.2 - 0.5
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

    # Let cascade spread a bit for medium difficulty
    for _ in range(3):
        target = list(obs.nodes.keys())[0]
        obs, _, done, _ = env.step("do_nothing", target)
        if done:
            obs = env.reset()

    MAX_STEPS = 15
    total_reward = 0.0
    steps_taken = 0

    for _ in range(MAX_STEPS):
        nodes = obs.nodes
        action = "do_nothing"
        target = list(nodes.keys())[0]

        for node, status in nodes.items():
            if status == "failed":
                action = "restart_service"
                target = node
                break
        else:
            for node, status in nodes.items():
                if status == "critical":
                    action = "scale_up"
                    target = node
                    break
            else:
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
    print(f"Medium task score: {run_task()}")