# desktop-client/main.py
# The main entry point for the VortexFlow Desktop Client.

import eel
import os
import tkinter as tk
from tkinter import filedialog
import requests
from typing import Dict

# Import from our new, organized core modules
# from core.app_logic import expose_all_functions # In the future, you can uncomment this
from core.utils import get_screen_center_position
from core.config import LOCAL_DOWNLOAD_FOLDER, SORTED_OUTPUT_FOLDER

def test_backend_connection() -> bool:
    """Pings the FastAPI backend server to check if it's running."""
    try:
        response = requests.get("http://127.0.0.1:8000/ping", timeout=3)
        return response.status_code == 200 and response.json().get("response") == "pong"
    except requests.exceptions.ConnectionError:
        return False

# This tells Eel where to find the UI files
eel.init('web')

# This is the main execution block
if __name__ == '__main__':
    # --- 1. Application Startup Logic ---
    print("--- VortexFlow Initializing ---")
    
    os.makedirs(LOCAL_DOWNLOAD_FOLDER, exist_ok=True)
    os.makedirs(SORTED_OUTPUT_FOLDER, exist_ok=True)
    print(f"Required folders are ready.")

    # --- TEST THE BACKEND CONNECTION ON STARTUP ---
    print("--- Attempting to establish first contact with backend... ---")
    if test_backend_connection():
        print("Backend connection successful!")
    else:
        print("Backend connection FAILED. The app may not function correctly.")
    print("----------------------------------------------------------")

    # --- 2. Start the Eel Application ---
    print("Starting VortexFlow UI...")
    
    window_size = (1200, 800)
    window_position = get_screen_center_position(window_size)

    eel.start(
        'index.html',
        size=window_size,
        position=window_position,
        port=0  # <-- THIS IS THE FIX! Use any available port.
    )

    print("--- VortexFlow has been closed. ---")