# session_manager.py
# This module handles saving and loading the download session and failed/banned links.

import json
import os
from config import SESSION_FILE

FAILED_LINKS_FILE = "failed_links.json"
BANNED_LINKS_FILE = "banned_links.json"

# --- Session Management ---

def save_session(remaining_jobs, output_folder):
    """Saves the list of remaining download jobs and the output folder to a JSON file."""
    session_data = {
        "remaining_jobs": remaining_jobs,
        "output_folder": output_folder
    }
    try:
        with open(SESSION_FILE, "w", encoding="utf-8") as f:
            json.dump(session_data, f, indent=4)
        print("Session saved successfully.")
    except Exception as e:
        print(f"Error saving session: {e}")

def load_session():
    """Loads session data from a JSON file."""
    if os.path.exists(SESSION_FILE):
        try:
            with open(SESSION_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading session: {e}")
            return None
    return None

def clear_session():
    """Deletes the session file."""
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)
        print("Session file cleared.")

# --- (The rest of the file for failed/banned links is unchanged) ---
def save_failed_links(failed_jobs):
    """Saves the list of failed link jobs to a JSON file."""
    try:
        with open(FAILED_LINKS_FILE, "w", encoding="utf-8") as f:
            json.dump(failed_jobs, f, indent=4)
    except Exception as e:
        print(f"Error saving failed links: {e}")

def load_failed_links():
    """Loads the list of failed link jobs from a JSON file."""
    if os.path.exists(FAILED_LINKS_FILE):
        try:
            with open(FAILED_LINKS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading failed links: {e}")
            return []
    return []

def load_banned_links():
    """Loads the set of permanently banned links from a JSON file."""
    if os.path.exists(BANNED_LINKS_FILE):
        try:
            with open(BANNED_LINKS_FILE, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except Exception as e:
            print(f"Error loading banned links: {e}")
            return set()
    return set()

def save_banned_links(banned_links_set):
    """Saves the set of permanently banned links to a JSON file."""
    try:
        with open(BANNED_LINKS_FILE, "w", encoding="utf-8") as f:
            json.dump(list(banned_links_set), f, indent=4)
    except Exception as e:
        print(f"Error saving banned links: {e}")
