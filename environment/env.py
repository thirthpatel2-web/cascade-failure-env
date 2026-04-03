# env.py

import random
from typing import Dict, List
from pydantic import BaseModel

from environment.simulator import SystemSimulator


# ✅ OpenEnv Typed Models

class Observation(BaseModel):
    nodes: Dict[str, str]
    metrics: Dict[str, float]
    logs: List[str]


class Action(BaseModel):
    action: str
    target: str


class Reward(BaseModel):
    value: float


class CascadeEnv:
    def __init__(self):
        self.sim = SystemSimulator()
        self.done = False
        self.step_count = 0

    def reset(self):
        self.sim = SystemSimulator()
        self.done = False
        self.step_count = 0

        # 🔥 Random failure injection
        node = random.choice(list(self.sim.nodes.keys()))
        self.sim.inject_failure(node)
        self.sim.propagate_failure()

        return self._get_observation()

    def step(self, action, target="database"):
        """
        action: restart_service / scale_up / do_nothing
        """

        if self.done:
            return self._get_observation(), Reward(value=0.0), True, {}

        # Apply action
        self.sim.apply_action(action, target)

        # Update system
        self.sim.propagate_failure()
        self.sim.reset_metrics_if_healthy()

        # Get observation
        obs = self._get_observation()

        # Compute reward
        reward = self._compute_reward(action)

        # Step tracking
        self.step_count += 1

        # Done conditions
        if all(state == "healthy" for state in self.sim.nodes.values()):
            self.done = True
        elif self.step_count >= 5:
            self.done = True

        return obs, Reward(value=reward), self.done, {}

    def state(self):
        return self._get_observation()

    def _get_observation(self):
        return Observation(
            nodes=self.sim.nodes,
            metrics=self.sim.metrics,
            logs=self.sim.logs
        )

    def _compute_reward(self, action):
        score_map = {
            "healthy": 1.0,
            "warning": 0.6,
            "critical": 0.3,
            "failed": 0.0
        }

        # State score
        state_score = sum(
            score_map[s] for s in self.sim.nodes.values()
        ) / len(self.sim.nodes)

        # Penalty for bad decisions
        penalty = 0
        if action == "do_nothing" and any(
            s in ["critical", "failed"] for s in self.sim.nodes.values()
        ):
            penalty = 0.2

        reward = max(0, state_score - penalty)

        return reward