# app.py

from fastapi import FastAPI
from environment.env import CascadeEnv

app = FastAPI()


# ROOT ENDPOINT (MANDATORY)
@app.get("/")
def root():
    return {"status": "running"}


# RESET ENDPOINT (VERY IMPORTANT)
@app.get("/reset")
def reset():
    env = CascadeEnv()
    obs = env.reset()
    return obs.dict()