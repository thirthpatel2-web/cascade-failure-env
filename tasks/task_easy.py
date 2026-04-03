from environment.env import CascadeEnv

def run_task():
    env = CascadeEnv()
    obs = env.reset()

    for _ in range(5):  # allow full recovery
        target = None

        for node, state in obs.nodes.items():
            if state == "failed":
                target = node
                break

        if target is None:
            # if no failed, improve remaining nodes
            for node, state in obs.nodes.items():
                if state in ["critical", "warning"]:
                    obs, reward, done, _ = env.step("scale_up", node)
                    break
            else:
                break
        else:
            obs, reward, done, _ = env.step("restart_service", target)

        if done:
            break

    score = 1.0 if all(s == "healthy" for s in obs.nodes.values()) else 0.0
    return float(score)