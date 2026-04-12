# tasks/task_easy.py
"""
Easy task: Recover system from a single random node failure.
Grader: returns float in [0.0, 1.0]
Score 1.0 = full recovery, 0.0 = failed
"""
from environment.env import CascadeEnv


def run_task() -> float:
    env = CascadeEnv(task_level="easy", seed=None)
    obs = env.reset()

    for _ in range(15):
        action, target = _choose_action(obs)
        if action is None:
            break
        obs, _, done, _ = env.step(action, target)
        if done:
            break

    score = 1.0 if all(s == "healthy" for s in obs.nodes.values()) else 0.0
    return float(score)


def _choose_action(obs):
    for node, state in obs.nodes.items():
        if state == "failed":
            return "restart_service", node
    for node, state in obs.nodes.items():
        if state == "critical":
            return "scale_up", node
    for node, state in obs.nodes.items():
        if state == "warning":
            return "scale_up", node
    return None, None