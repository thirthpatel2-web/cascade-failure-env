# app.py — root level, used by Dockerfile CMD
# Imports and re-exports everything from server/app.py so both entry points work
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Re-use the same app defined in server/app.py
from server.app import app  # noqa: F401 — exported for uvicorn

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "server.app:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 7860)),
    )