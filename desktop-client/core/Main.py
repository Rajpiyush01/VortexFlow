# backend-server/main.py
# This is the central "Brain" of VortexFlow, powered by FastAPI.

from fastapi import FastAPI
from typing import Dict

# Creates our actual web application instance. This 'app' is our entire backend.
app = FastAPI(title="VortexFlow Backend")

@app.get("/")
def read_root() -> Dict[str, str]:
    """
    Root endpoint for the backend. Just confirms the server is alive.
    """
    return {"message": "VortexFlow Backend is alive and awaiting commands!"}

@app.get("/ping")
def ping_pong() -> Dict[str, str]:
    """
    A simple endpoint that our desktop client can "ping" to verify a connection.
    """
    return {"response": "pong"}

# In a real application, you would add more endpoints here, for example:
# @app.post("/users/login")
# def login_user():
#     # Logic for handling Google Sign-In from Firebase
#     return {"status": "success"}

if __name__ == "__main__":
    import uvicorn
    # This block allows you to run the server directly with `python main.py` for easy debugging.
    # Uvicorn is the high-performance server that runs your FastAPI application.
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)