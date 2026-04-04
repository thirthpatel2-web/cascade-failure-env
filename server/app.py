from fastapi import FastAPI
from environment.env import CascadeEnv

app = FastAPI()


# ROOT ENDPOINT (MANDATORY)
@app.get("/")
def root():
    return {"status": "running"}


# RESET ENDPOINT (SUPPORT BOTH GET + POST)
@app.get("/reset")
@app.post("/reset")
def reset():
    env = CascadeEnv()
    obs = env.reset()
    return obs