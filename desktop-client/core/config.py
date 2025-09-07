# core/config.py
# This file holds all the global settings and configurations for the application.
# It's the "single source of truth" for paths, domains, and other constants.

import os
from typing import List

# --- 1. DIRECTORY CONFIGURATION ---
# The absolute path to the 'desktop-client' folder. All other paths are built from this.
# os.path.dirname(__file__) gets the directory of the current file (core)
# os.path.dirname(...) of that gets the parent directory (desktop-client)
APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# All paths are now built robustly from APP_DIR to prevent errors.
LOCAL_DOWNLOAD_FOLDER = os.path.join(APP_DIR, "VortexFlow_Downloads") 
SORTED_OUTPUT_FOLDER = os.path.join(APP_DIR, "VortexFlow_Sorted") 

# --- 2. BROWSER CONFIGURATION ---
# IMPORTANT: This path is system-dependent. It will only work if Brave is installed here.
# In a future version, we could make this configurable in the UI's settings panel.
BRAVE_BROWSER_PATH = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"

# --- 3. LINK DETECTION CONFIGURATION ---
# The comprehensive list of all TeraBox domains to be detected by the analyzer.
TERABOX_DOMAINS: List[str] = [
    "terabox.com", "terabox.app", "teraboxlink.com", "freeterabox.com",
    "1024terabox.com", "terafileshare.com", "terasharelink.com",
    "teraboxshare.com", "4funbox.co", "mirrobox.com"
]

# --- 4. SESSION & DATA FILE CONFIGURATION ---
# Defines the names for the files that store session data, failed links, and banned links.
# These will be created in the APP_DIR.
SESSION_FILE = os.path.join(APP_DIR, "session.json")
FAILED_LINKS_FILE = os.path.join(APP_DIR, "failed_links.json")
BANNED_LINKS_FILE = os.path.join(APP_DIR, "banned_links.json")