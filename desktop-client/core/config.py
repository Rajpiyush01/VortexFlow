# config.py
# This file holds all the global settings and configurations for the application.

import os

# --- FOLDER PATHS ---
# Make sure these folders exist in the same directory as the main.py file
LOCAL_DOWNLOAD_FOLDER = os.path.abspath("DOWNLOADS") 
SORTED_OUTPUT_FOLDER = os.path.abspath("Tera_Downloads_Sorted") 

# --- BROWSER CONFIG ---
# IMPORTANT: Double-check this path is correct for your system
BRAVE_BROWSER_PATH = r"C:\Users\lenovo\AppData\Local\BraveSoftware\Brave-Browser\Application\brave.exe" 

# --- LINK DETECTION ---
# The comprehensive list of all TeraBox domains to be detected
TERABOX_DOMAINS = [
    "terabox.com", "terabox.app", "teraboxlink.com", "freeterabox.com",
    "1024terabox.com", "terafileshare.com", "terasharelink.com",
    "teraboxshare.com", "4funbox.co", "mirrobox.com"
]

# --- SESSION CONFIG ---
SESSION_FILE = "session.json"