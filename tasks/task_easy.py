# tasks/task_easy.py
from environment.env import CascadeEnv

def run_task() -> float:
    # seed=None → grader tests with random failure each evaluation
    env = CascadeEnv(task_level="easy", seed=None)
    obs = env.reset()

    for _ in range(15):
        action, target = _choose(obs)
        if action is None:
            break
        obs, _, done, _ = env.step(action, target)
        if done:
            break

    return 1.0 if all(s == "healthy" for s in obs.nodes.values()) else 0.0

def _choose(obs):
    for n, s in obs.nodes.items():
        if s == "failed":   return "restart_service", n
    for n, s in obs.nodes.items():
        if s == "critical": return "scale_up", n
    for n, s in obs.nodes.items():
        if s == "warning":  return "scale_up", n
    return None, None