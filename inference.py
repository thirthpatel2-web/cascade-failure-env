import os
import sys

API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "meta-llama/Llama-3.1-8B-Instruct")
HF_TOKEN = os.getenv("HF_TOKEN", "dummy")

MAX_STEPS = 10
SUCCESS_SCORE_THRESHOLD = 0.4

def log_start(task, env, model):
    print(f"[START] task={task} env={env} model={model}", flush=True)

def log_step(step, action, reward, done, error=None):
    error_str = error if error else "null"
    print(f"[STEP] step={step} action={action} reward={reward:.2f} done={str(done).lower()} error={error_str}", flush=True)

def log_end(success, steps, score, rewards):
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.2f} rewards={rewards_str}", flush=True)

def main():
    from environment.env import CascadeEnv

    log_start("cascade_failure_prevention", "devops_cascade", MODEL_NAME)

    env = CascadeEnv()
    obs = env.reset()

    rewards = []
    done = False
    step = 0

    # Find the first failed/critical node
    def pick_action(obs):
        for node, status in obs.nodes.items():
            if status == "failed":
                return "restart_service", node
        for node, status in obs.nodes.items():
            if status == "critical":
                return "scale_up", node
        for node, status in obs.nodes.items():
            if status == "warning":
                return "scale_up", node
        return "do_nothing", list(obs.nodes.keys())[0]

    while not done and step < MAX_STEPS:
        step += 1
        action_type, target = pick_action(obs)
        action_str = f"{action_type}({target})"

        try:
           obs, reward_obj, done, info = env.step(action_type, target)
           reward = reward_obj.value
        except Exception as e:
            log_step(step, action_str, 0.0, True, str(e))
            log_end(False, step, 0.0, rewards)
            return

        rewards.append(reward)
        log_step(step, action_str, reward, done)

    steps_taken = max(step, 1)
    score = min(max(sum(rewards) / steps_taken, 0.0), 1.0)
    success = score >= SUCCESS_SCORE_THRESHOLD

    log_end(success, step, score, rewards)

if __name__ == "__main__":
    main()