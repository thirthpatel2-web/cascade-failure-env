# env.py

from environment.simulator import SystemSimulator

class CascadeEnv:
    def __init__(self):
        self.sim = SystemSimulator()
        self.done = False

    def reset(self):
        self.sim = SystemSimulator()
        self.done = False

        return self._get_observation()

    def step(self, action, target="database"):
        """
        action: restart_service / scale_up / do_nothing
        """

        # Apply action
        self.sim.apply_action(action, target)

        # Update system
        self.sim.propagate_failure()
        self.sim.reset_metrics_if_healthy()

        # Get observation
        obs = self._get_observation()

        # Reward logic
        reward = self._compute_reward()

        # Check if done
        if all(state == "healthy" for state in self.sim.nodes.values()):
            self.done = True

        return obs, reward, self.done, {}

    def state(self):
        return self._get_observation()

    def _get_observation(self):
        return {
            "nodes": self.sim.nodes,
            "metrics": self.sim.metrics,
            "logs": self.sim.logs
        }

    def _compute_reward(self):
        # Simple reward logic

        healthy_count = sum(
            1 for s in self.sim.nodes.values() if s == "healthy"
        )

        total = len(self.sim.nodes)

        return healthy_count / total