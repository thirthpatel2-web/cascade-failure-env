# tasks/task_medium.py
from environment.env import CascadeEnv

PRIORITY = ["api_gateway","db_primary","payment_svc","auth_service",
            "cache_layer","user_service","order_service","db_replica",
            "search_svc","inventory_svc","message_queue","notification"]

def run_task() -> float:
    env = CascadeEnv(task_level="medium", seed=None)
    obs = env.reset()
    total, steps = 0.0, 0

    for _ in range(20):
        action, target = _choose(obs)
        if action is None: break
        obs, r, done, _ = env.step(action, target)
        total += r.value; steps += 1
        if done: break

    return float(round(min(max(total / max(steps, 1), 0.0), 1.0), 4))

def _choose(obs):
    for n in PRIORITY:
        if obs.nodes.get(n) == "failed":   return "restart_service", n
    for n in PRIORITY:
        if obs.nodes.get(n) == "critical": return "scale_up", n
    for n in PRIORITY:
        if obs.nodes.get(n) == "warning":  return "scale_up", n
    return None, None