# task_easy.py

def run_task(simulator):
    """
    Task: Identify system state
    """

    # Inject failure
    simulator.inject_failure("database")
    simulator.propagate_failure()

    # Observation given to agent
    observation = {
        "nodes": simulator.nodes,
        "metrics": simulator.metrics
    }

    return observation


def grade(answer):
    """
    Correct answer = 'critical'
    """
    if answer == "critical":
        return 1.0
    else:
        return 0.0