from fastapi import FastAPI
from environment.env import CascadeEnv

app = FastAPI()


@app.get("/")
def root():
    return {"status": "running"}


@app.get("/reset")
@app.post("/reset")
def reset():
    env = CascadeEnv()
    return env.reset()


def main():
    return app