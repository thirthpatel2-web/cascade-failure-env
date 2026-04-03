# simulator.py

class SystemSimulator:
    def __init__(self):
        self.nodes = {
            "frontend": "healthy",
            "api": "healthy",
            "database": "healthy"
        }

        self.dependencies = {
            "frontend": ["api"],
            "api": ["database"],
            "database": []
        }

        # Metrics
        self.metrics = {
            "cpu": 20,
            "memory": 30,
            "error_rate": 0.01
        }

        # Logs
        self.logs = []

    def inject_failure(self, node):
        print(f"\n[!] Injecting failure in {node}")
        self.nodes[node] = "failed"

        # Update metrics
        self.metrics["cpu"] = 90
        self.metrics["memory"] = 95
        self.metrics["error_rate"] = 0.5

        # Add log
        self.logs.append(f"[ERROR] {node} has failed")

    def propagate_failure(self):
        changed = True

        while changed:
            changed = False

            for node, deps in self.dependencies.items():
                for dep in deps:

                    # FAILURE PROPAGATION
                    if self.nodes[dep] == "failed":
                        if self.nodes[node] not in ["failed", "critical"]:
                            self.nodes[node] = "critical"
                            changed = True

                    elif self.nodes[dep] == "critical":
                        if self.nodes[node] == "healthy":
                            self.nodes[node] = "warning"
                            changed = True

                    # RECOVERY PROPAGATION
                    elif self.nodes[dep] == "healthy":
                        if self.nodes[node] == "critical":
                            self.nodes[node] = "warning"
                            changed = True
                        elif self.nodes[node] == "warning":
                            self.nodes[node] = "healthy"
                            changed = True

    def apply_action(self, action, target):
        print(f"\n[⚡ Action] {action} on {target}")

        # 🔥 GRADUAL RECOVERY (KEY UPGRADE)
        if action == "restart_service":
            if self.nodes[target] == "failed":
                self.nodes[target] = "critical"
            elif self.nodes[target] == "critical":
                self.nodes[target] = "warning"
            elif self.nodes[target] == "warning":
                self.nodes[target] = "healthy"

            self.logs.append(f"[INFO] Restart step applied to {target}")

        elif action == "scale_up":
            if self.nodes[target] == "critical":
                self.nodes[target] = "warning"
            elif self.nodes[target] == "warning":
                self.nodes[target] = "healthy"

            self.logs.append(f"[INFO] Scaled {target}")

        elif action == "do_nothing":
            self.logs.append("[INFO] No action taken")

    def reset_metrics_if_healthy(self):
        if all(state == "healthy" for state in self.nodes.values()):
            self.metrics["cpu"] = 20
            self.metrics["memory"] = 30
            self.metrics["error_rate"] = 0.01

    def show_state(self):
        print("\nCurrent System State:")
        for node, state in self.nodes.items():
            print(f"{node}: {state}")

        print("\nMetrics:")
        for k, v in self.metrics.items():
            print(f"{k}: {v}")

        print("\nRecent Logs:")
        for log in self.logs[-5:]:
            print(log)


# =========================
# TEST RUN
# =========================
if __name__ == "__main__":
    sim = SystemSimulator()

    sim.show_state()

    sim.inject_failure("database")
    sim.propagate_failure()
    sim.show_state()

    # Apply multiple steps to recover
    sim.apply_action("restart_service", "database")
    sim.propagate_failure()

    sim.apply_action("restart_service", "database")
    sim.propagate_failure()

    sim.apply_action("restart_service", "database")
    sim.propagate_failure()

    sim.reset_metrics_if_healthy()
    sim.show_state()