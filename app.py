from fastapi import FastAPI
from environment.env import CascadeEnv

app = FastAPI()

@app.get("/")
def run_env():
    env = CascadeEnv()
    obs = env.reset()

    obs, reward, done, _ = env.step("restart_service")

    return {
        "observation": obs,
        "reward": reward,
        "done": done
    }