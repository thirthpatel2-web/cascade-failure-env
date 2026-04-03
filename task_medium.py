# task_medium.py

def run_task(simulator):
    """
    Task: Identify root cause
    """

    simulator.inject_failure("database")
    simulator.propagate_failure()

    observation = {
        "logs": simulator.logs,
        "metrics": simulator.metrics
    }

    return observation


def grade(answer):
    """
    Correct answer = 'database'
    """
    if answer == "database":
        return 1.0
    else:
        return 0.0