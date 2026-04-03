# inference.py

from environment.env import CascadeEnv


def simple_agent(observation):
    """
    Basic rule-based agent
    """

    nodes = observation["nodes"]

    # If any node failed → restart database
    if "failed" in nodes.values():
        return "restart_service"

    return "do_nothing"


def run():
    env = CascadeEnv()

    obs = env.reset()

    total_reward = 0

    for step in range(5):
        action = simple_agent(obs)

        obs, reward, done, _ = env.step(action)

        total_reward += reward

        if done:
            break

    print("\nFinal Reward:", total_reward)


if __name__ == "__main__":
    run()