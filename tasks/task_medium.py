# tasks/task_medium.py
"""
Medium task: Handle two simultaneous failures.
Grader: returns float in [0.0, 1.0]
Score = average reward over episode steps
"""
from environment.env import CascadeEnv

PRIORITY = [
    "api_gateway", "db_primary", "payment_svc", "auth_service",
    "cache_layer", "user_service", "order_service", "db_replica",
    "search_svc", "inventory_svc", "message_queue", "notification",
]


def run_task() -> float:
    env = CascadeEnv(task_level="medium", seed=None)
    obs = env.reset()

    total_reward = 0.0
    steps = 0

    for _ in range(20):
        action, target = _choose_action(obs)
        if action is None:
            break
        obs, reward, done, _ = env.step(action, target)
        total_reward += reward.value
        steps += 1
        if done:
            break

    steps = max(steps, 1)
    score = min(max(total_reward / steps, 0.0), 1.0)
    return float(round(score, 4))


def _choose_action(obs):
    for node in PRIORITY:
        if obs.nodes.get(node) == "failed":
            return "restart_service", node
    for node in PRIORITY:
        if obs.nodes.get(node) == "critical":
            return "scale_up", node
    for node in PRIORITY:
        if obs.nodes.get(node) == "warning":
            return "scale_up", node
    return None, None