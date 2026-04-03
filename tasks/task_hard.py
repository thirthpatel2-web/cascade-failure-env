# task_hard.py

def run_task(simulator):
    """
    Task: Choose correct action
    """

    simulator.inject_failure("database")
    simulator.propagate_failure()

    observation = {
        "nodes": simulator.nodes,
        "metrics": simulator.metrics,
        "logs": simulator.logs
    }

    return observation


def grade(answer):
    """
    Correct answer = 'restart_service'
    """
    if answer == "restart_service":
        return 1.0
    else:
        return 0.0