# backend-server/main.py
# This is the central "Brain" of VortexFlow, powered by FastAPI.

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict

# --- 1. CREATE THE APP INSTANCE ---
app = FastAPI(
    title="VortexFlow Backend",
    description="The central API server that manages users, subscriptions, and other business logic.",
    version="1.0.0"
)

# --- 2. CONFIGURE CORS MIDDLEWARE (CRITICAL FOR CONNECTING TO THE DESKTOP APP) ---
# This allows our desktop app (running on a different 'origin') to make requests to this server.
origins = [
    "*"  # For development, we allow all origins. For production, you would restrict this.
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 3. DEFINE API ENDPOINTS ---

@app.get("/")
def read_root() -> Dict[str, str]:
    """
    Root endpoint for the backend. Just confirms the server is alive.
    You can visit this in your browser at http://127.0.0.1:8000
    """
    return {"message": "VortexFlow Backend is alive and awaiting commands!"}


@app.get("/ping")
def ping_pong() -> Dict[str, str]:
    """
    A simple endpoint that our desktop client can "ping" to verify a connection.
    This is the function our desktop app will test on startup.
    """
    return {"response": "pong"}


# --- 4. PLACEHOLDER FOR FUTURE FEATURES (FROM OUR BLUEPRINT) ---

# @app.post("/auth/google")
# def handle_google_login(token: str):
#     """
#     This is where you would handle the user's Google Sign-In token
#     sent from the desktop client, verify it with Firebase, and
#     create or update the user in your database.
#     """
#     # Firebase admin logic would go here
#     return {"status": "success", "user_id": "some_user_id"}


# --- 5. STANDARD RUN BLOCK FOR EASY DEVELOPMENT ---
if __name__ == "__main__":
    # This block allows you to run the server directly with `python main.py`.
    # Uvicorn is the high-performance server that runs your FastAPI application.
    # reload=True automatically restarts the server when you save changes.
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)