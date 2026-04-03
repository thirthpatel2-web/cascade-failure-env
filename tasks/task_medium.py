from environment.env import CascadeEnv

def run_task():
    env = CascadeEnv()
    obs = env.reset()

    total = 0.0

    for _ in range(5):
        action, target = None, None

        for node, state in obs.nodes.items():
            if state == "failed":
                action, target = "restart_service", node
                break

        if action is None:
            for node, state in obs.nodes.items():
                if state == "critical":
                    action, target = "scale_up", node
                    break

        if action is None:
            action, target = "do_nothing", "database"

        obs, reward, done, _ = env.step(action, target)
        total += reward.value

        if done:
            break

    score = total / 5.0
    return float(min(max(score, 0.0), 1.0))