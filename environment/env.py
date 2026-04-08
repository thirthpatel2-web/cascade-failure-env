# environment/env.py

import random
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel

from environment.simulator import SystemSimulator, NODES


# ── OpenEnv typed models ──────────────────────────────────────────────────────

class Observation(BaseModel):
    nodes:          Dict[str, str]
    metrics:        Dict[str, float]
    logs:           List[str]
    failed_nodes:   List[str]
    step:           int
    time_remaining: int


class Action(BaseModel):
    action: str
    target: str


class Reward(BaseModel):
    value:       float
    explanation: str


# ── Task difficulty configs ───────────────────────────────────────────────────

ALL_NODES = list(NODES.keys())

TASK_CONFIGS = {
    "easy": {
        "description": "Single node failure — simple recovery",
        "num_failures": 1,
        "max_steps": 15,
    },
    "medium": {
        "description": "Two simultaneous failures — requires prioritisation",
        "num_failures": 2,
        "max_steps": 20,
    },
    "hard": {
        "description": "Three failures including critical nodes — full cascade",
        "num_failures": 3,
        "max_steps": 25,
    },
}


class CascadeEnv:
    """
    OpenEnv-compliant Cascade Failure Prevention Environment.
    12-node microservice graph with realistic dependency propagation.
    Seed=None means random failure each episode (intended behaviour).
    """

    def __init__(self, task_level: str = "easy", seed: Optional[int] = None):
        assert task_level in TASK_CONFIGS, f"task_level must be one of {list(TASK_CONFIGS)}"
        self.task_level  = task_level
        self.config      = TASK_CONFIGS[task_level]
        self._seed       = seed   # None = random each reset
        self.sim         = SystemSimulator()
        self._step_count = 0
        self._done       = False

    # ── OpenEnv API ───────────────────────────────────────────────────────────

    def reset(self) -> Observation:
        # Use random seed each episode so failure node changes every run
        episode_seed = self._seed if self._seed is not None else random.randint(0, 999999)
        self.sim = SystemSimulator(seed=episode_seed)
        self.sim.reset()
        self._step_count = 0
        self._done       = False

        # Pick failure nodes randomly based on seed
        rng = random.Random(episode_seed)
        num = self.config["num_failures"]
        failure_nodes = rng.sample(ALL_NODES, k=num)

        for node_id in failure_nodes:
            self.sim.inject_failure(node_id, severity="failed")

        self.sim.propagate()
        return self._build_obs()

    def step(self, action: str, target: str = "api_gateway") -> Tuple[Observation, Reward, bool, Dict]:
        if self._done:
            return self._build_obs(), Reward(value=0.0, explanation="episode ended"), True, {}

        self.sim.apply_action(action, target)
        self.sim.propagate()
        self.sim.reset_metrics_if_healthy()

        self._step_count += 1

        reward  = self._compute_reward(action)
        obs     = self._build_obs()

        all_healthy = all(s == "healthy" for s in self.sim.nodes.values())
        time_up     = self._step_count >= self.config["max_steps"]
        self._done  = all_healthy or time_up

        info = {
            "system_health": self.sim.system_health(),
            "failed_nodes":  self.sim.get_failed_nodes(),
            "step":          self._step_count,
            "success":       all_healthy,
        }
        return obs, reward, self._done, info

    def state(self) -> Dict[str, Any]:
        return {
            "task_level":    self.task_level,
            "step":          self._step_count,
            "done":          self._done,
            "system_health": self.sim.system_health(),
            "nodes":         dict(self.sim.nodes),
            "metrics":       dict(self.sim.metrics),
            "failed_nodes":  self.sim.get_failed_nodes(),
            "config":        self.config,
        }

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _build_obs(self) -> Observation:
        return Observation(
            nodes          = dict(self.sim.nodes),
            metrics        = dict(self.sim.metrics),
            logs           = list(self.sim.logs[-10:]),
            failed_nodes   = self.sim.get_failed_nodes(),
            step           = self._step_count,
            time_remaining = self.config["max_steps"] - self._step_count,
        )

    def _compute_reward(self, action: str) -> Reward:
        score_map = {"healthy": 1.0, "warning": 0.6, "critical": 0.3, "failed": 0.0}

        total_w     = sum(NODES[n]["criticality"] for n in NODES)
        state_score = sum(
            score_map.get(self.sim.nodes[n], 0.0) * NODES[n]["criticality"]
            for n in NODES
        ) / total_w

        penalty = 0.0
        if action == "do_nothing" and len(self.sim.get_degraded_nodes()) > 0:
            penalty = 0.15

        reward = max(0.0, min(1.0, state_score - penalty))
        explanation = (
            f"health={state_score:.3f} penalty={penalty:.2f} "
            f"failed={len(self.sim.get_failed_nodes())} "
            f"degraded={len(self.sim.get_degraded_nodes())}"
        )
        return Reward(value=round(reward, 4), explanation=explanation)