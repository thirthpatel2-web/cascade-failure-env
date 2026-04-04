from environment.env import CascadeEnv


def run_task() -> float:
    env = CascadeEnv()
    obs = env.reset()

    for _ in range(10):
        action, target = None, None

        # Priority 1: restart any failed node
        for node, state in obs.nodes.items():
            if state == "failed":
                action, target = "restart_service", node
                break

        # Priority 2: scale any critical node
        if action is None:
            for node, state in obs.nodes.items():
                if state == "critical":
                    action, target = "scale_up", node
                    break

        # Priority 3: scale any warning node
        if action is None:
            for node, state in obs.nodes.items():
                if state == "warning":
                    action, target = "scale_up", node
                    break

        # All healthy — stop early
        if action is None:
            break

        obs, reward, done, _ = env.step(action, target)

        if done:
            break

    # Deterministic binary grader
    score = 1.0 if all(s == "healthy" for s in obs.nodes.values()) else 0.0
    return float(score)