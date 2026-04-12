"""
All three task graders in one root-level file.
The validator can import these directly without any package structure.
"""

import sys
import os

# Ensure the project root is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def _get_float(reward):
    """Safely extract float from either a float or a Pydantic Reward object."""
    if isinstance(reward, (float, int)):
        return float(reward)
    for attr in ("score", "value", "reward", "amount"):
        if hasattr(reward, attr):
            return float(getattr(reward, attr))
    try:
        return float(reward)
    except Exception:
        return 0.0


def _best_action(nodes):
    """Pick the best action/target given current node states."""
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


def run_easy() -> float:
    """Easy task: recover a single random failed node within 10 steps."""
    from environment.env import CascadeEnv
    env = CascadeEnv(seed=None)
    obs = env.reset()
    total, steps = 0.0, 0
    for _ in range(10):
        action, target = _best_action(obs.nodes)
        obs, reward, done, _ = env.step(action, target)
        total += _get_float(reward)
        steps += 1
        if done:
            break
    return round(min(max(total / max(steps, 1), 0.0), 1.0), 4)


def run_medium() -> float:
    """Medium task: handle multi-node degraded state."""
    from environment.env import CascadeEnv
    env = CascadeEnv(seed=None)
    obs = env.reset()
    # Let cascade spread slightly
    for _ in range(3):
        target = list(obs.nodes.keys())[0]
        obs, _, done, _ = env.step("do_nothing", target)
        if done:
            obs = env.reset()
    total, steps = 0.0, 0
    for _ in range(15):
        action, target = _best_action(obs.nodes)
        obs, reward, done, _ = env.step(action, target)
        total += _get_float(reward)
        steps += 1
        if done:
            break
    return round(min(max(total / max(steps, 1), 0.0), 1.0), 4)


def run_hard() -> float:
    """Hard task: full cascade recovery with limited steps."""
    from environment.env import CascadeEnv
    env = CascadeEnv(seed=None)
    obs = env.reset()
    # Let cascade spread more
    for _ in range(6):
        target = list(obs.nodes.keys())[0]
        obs, _, done, _ = env.step("do_nothing", target)
        if done:
            obs = env.reset()
    total, steps = 0.0, 0
    restarted = set()
    for _ in range(20):
        nodes = obs.nodes
        action, target = "do_nothing", list(nodes.keys())[0]
        found = False
        for node, status in nodes.items():
            if status == "failed" and node not in restarted:
                action, target = "restart_service", node
                restarted.add(node)
                found = True
                break
        if not found:
            action, target = _best_action(nodes)
        obs, reward, done, _ = env.step(action, target)
        total += _get_float(reward)
        steps += 1
        if done:
            break
    return round(min(max(total / max(steps, 1), 0.0), 1.0), 4)


# Aliases so the yaml can point to either name style
run_task = run_easy  # default alias


if __name__ == "__main__":
    print(f"Easy:   {run_easy()}")
    print(f"Medium: {run_medium()}")
    print(f"Hard:   {run_hard()}")