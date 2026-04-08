import random

NODES = {
    "api_gateway":     {"name": "API Gateway",        "criticality": 1.0},
    "auth_service":    {"name": "Auth Service",        "criticality": 0.9},
    "user_service":    {"name": "User Service",        "criticality": 0.8},
    "order_service":   {"name": "Order Service",       "criticality": 0.8},
    "payment_svc":     {"name": "Payment Service",     "criticality": 0.95},
    "inventory_svc":   {"name": "Inventory Service",   "criticality": 0.7},
    "notification":    {"name": "Notification Svc",    "criticality": 0.5},
    "search_svc":      {"name": "Search Service",      "criticality": 0.6},
    "cache_layer":     {"name": "Cache Layer",         "criticality": 0.85},
    "db_primary":      {"name": "DB Primary",          "criticality": 1.0},
    "db_replica":      {"name": "DB Replica",          "criticality": 0.7},
    "message_queue":   {"name": "Message Queue",       "criticality": 0.75},
}

EDGES = [
    ("api_gateway",   "auth_service"),
    ("api_gateway",   "user_service"),
    ("api_gateway",   "order_service"),
    ("api_gateway",   "search_svc"),
    ("auth_service",  "user_service"),
    ("order_service", "payment_svc"),
    ("order_service", "inventory_svc"),
    ("order_service", "message_queue"),
    ("payment_svc",   "db_primary"),
    ("user_service",  "cache_layer"),
    ("user_service",  "db_primary"),
    ("search_svc",    "cache_layer"),
    ("cache_layer",   "db_primary"),
    ("db_primary",    "db_replica"),
    ("message_queue", "notification"),
    ("inventory_svc", "db_replica"),
]


class SystemSimulator:
    def __init__(self, seed: int = None):
        self._seed = seed
        self._rng = random.Random(seed)
        self.nodes = {}
        self.metrics = {}
        self.logs = []
        self._downstream = {}
        self._build_graph()

    def _build_graph(self):
        self._downstream = {n: [] for n in NODES}
        for src, tgt in EDGES:
            self._downstream[src].append(tgt)

    def reset(self):
        self._rng = random.Random(self._seed)
        self.nodes   = {n: "healthy" for n in NODES}
        self.metrics = {"cpu": 20.0, "memory": 30.0, "error_rate": 0.01}
        self.logs    = []

    def inject_failure(self, node_id: str, severity: str = "failed"):
        self.nodes[node_id] = severity
        self.metrics["cpu"]        = 90.0
        self.metrics["memory"]     = 95.0
        self.metrics["error_rate"] = 0.5
        self.logs.append(f"[ERROR] {node_id} has {severity}")

    def propagate(self):
        for _ in range(20):
            changed = False
            for src, targets in self._downstream.items():
                for tgt in targets:
                    src_s = self.nodes[src]
                    tgt_s = self.nodes[tgt]
                    if src_s == "failed" and tgt_s not in ("failed", "critical"):
                        self.nodes[tgt] = "critical"
                        changed = True
                    elif src_s == "critical" and tgt_s == "healthy":
                        self.nodes[tgt] = "warning"
                        changed = True
            if not changed:
                break

    def apply_action(self, action: str, target: str):
        if target not in self.nodes:
            self.logs.append(f"[WARN] Unknown target: {target}")
            return
        if action == "restart_service":
            cur = self.nodes[target]
            if cur == "failed":
                self.nodes[target] = "critical"
            elif cur == "critical":
                self.nodes[target] = "warning"
            elif cur == "warning":
                self.nodes[target] = "healthy"
            self.logs.append(f"[INFO] restart_service applied to {target} → {self.nodes[target]}")
        elif action == "scale_up":
            cur = self.nodes[target]
            if cur == "critical":
                self.nodes[target] = "warning"
            elif cur == "warning":
                self.nodes[target] = "healthy"
            self.logs.append(f"[INFO] scale_up applied to {target} → {self.nodes[target]}")
        elif action == "isolate":
            self.nodes[target] = "healthy"
            self.logs.append(f"[INFO] isolate applied to {target}")
        elif action == "do_nothing":
            self.logs.append("[INFO] do_nothing — no action taken")

    def reset_metrics_if_healthy(self):
        if all(s == "healthy" for s in self.nodes.values()):
            self.metrics = {"cpu": 20.0, "memory": 30.0, "error_rate": 0.01}

    def system_health(self) -> float:
        score_map = {"healthy": 1.0, "warning": 0.6, "critical": 0.3, "failed": 0.0}
        total_weight = sum(NODES[n]["criticality"] for n in NODES)
        weighted_sum = sum(
            score_map.get(self.nodes[n], 0.0) * NODES[n]["criticality"]
            for n in NODES
        )
        return weighted_sum / total_weight if total_weight > 0 else 0.0

    def get_failed_nodes(self):
        return [n for n, s in self.nodes.items() if s == "failed"]

    def get_critical_nodes(self):
        return [n for n, s in self.nodes.items() if s == "critical"]

    def get_degraded_nodes(self):
        return [n for n, s in self.nodes.items() if s in ("critical", "warning")]