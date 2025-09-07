# core/session_manager.py
# This module handles saving and loading the download session and failed/banned links.

import json
import os
import logging
from typing import Any

# --- Setup a basic logger ---
# In a larger app, this would be configured in your main.py
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- All file paths should be managed in the config file for professional code ---
# We assume these are defined in your core.config
from .config import SESSION_FILE, FAILED_LINKS_FILE, BANNED_LINKS_FILE


# --- Session Management ---

def save_session(remaining_jobs: list[dict], output_folder: str) -> None:
    """
    Saves the list of remaining download jobs and the output folder to a JSON file.

    Args:
        remaining_jobs (list[dict]): A list of download job dictionaries that are yet to be processed.
        output_folder (str): The path to the root output folder for this session.
    """
    session_data = {
        "remaining_jobs": remaining_jobs,
        "output_folder": output_folder
    }
    try:
        with open(SESSION_FILE, "w", encoding="utf-8") as f:
            json.dump(session_data, f, indent=4)
        logging.info("Session saved successfully.")
    except Exception as e:
        logging.error(f"Error saving session: {e}")

def load_session() -> dict[str, Any] | None:
    """
    Loads session data from the session JSON file if it exists.

    Returns:
        dict | None: The loaded session data as a dictionary, or None if the file doesn't exist or an error occurs.
    """
    if os.path.exists(SESSION_FILE):
        try:
            with open(SESSION_FILE, "r", encoding="utf-8") as f:
                logging.info("Previous session found. Loading...")
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logging.error(f"Error loading session file: {e}")
            return None
    return None

def clear_session() -> None:
    """Deletes the session file if it exists."""
    if os.path.exists(SESSION_FILE):
        try:
            os.remove(SESSION_FILE)
            logging.info("Session file cleared successfully.")
        except OSError as e:
            logging.error(f"Error clearing session file: {e}")


# --- Failed & Banned Link Management ---

def save_failed_links(failed_jobs: list[dict]) -> None:
    """
    Saves the list of failed link jobs to a JSON file.

    Args:
        failed_jobs (list[dict]): A list of job dictionaries that failed to download.
    """
    try:
        with open(FAILED_LINKS_FILE, "w", encoding="utf-8") as f:
            json.dump(failed_jobs, f, indent=4)
    except IOError as e:
        logging.error(f"Error saving failed links: {e}")

def load_failed_links() -> list[dict]:
    """
    Loads the list of failed link jobs from a JSON file.

    Returns:
        list[dict]: A list of failed jobs, or an empty list if none are found or an error occurs.
    """
    if os.path.exists(FAILED_LINKS_FILE):
        try:
            with open(FAILED_LINKS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logging.error(f"Error loading failed links: {e}")
            return []
    return []

def save_banned_links(banned_links_set: set[str]) -> None:
    """
    Saves the set of permanently banned links to a JSON file.

    Args:
        banned_links_set (set[str]): A set of URL strings to ban.
    """
    try:
        with open(BANNED_LINKS_FILE, "w", encoding="utf-8") as f:
            json.dump(list(banned_links_set), f, indent=4)
    except IOError as e:
        logging.error(f"Error saving banned links: {e}")

def load_banned_links() -> set[str]:
    """
    Loads the set of permanently banned links from a JSON file.

    Returns:
        set[str]: A set of banned links, or an empty set if none are found or an error occurs.
    """
    if os.path.exists(BANNED_LINKS_FILE):
        try:
            with open(BANNED_LINKS_FILE, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except (json.JSONDecodeError, IOError) as e:
            logging.error(f"Error loading banned links: {e}")
            return set()
    return set()