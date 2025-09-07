# core/app_logic.py
import eel
import os
import tkinter as tk
from tkinter import filedialog
import threading
import time

from .analyzer import analyze_html_file
from .downloader import setup_driver, download_file_locally

# --- 1. Functions Exposed to the JavaScript UI ---

@eel.expose
def select_files():
    """Opens a native file dialog to select one or more files."""
    # ... (code is complete and correct from previous version)
    root = tk.Tk(); root.withdraw(); root.attributes('-topmost', True)
    file_paths = filedialog.askopenfilenames(title="Select your links file(s)")
    return list(file_paths) if file_paths else []

@eel.expose
def start_analysis(file_paths):
    """Starts the link analysis process in a background thread."""
    threading.Thread(target=_run_analysis_in_background, args=(file_paths,)).start()

@eel.expose
def start_downloading(download_jobs):
    """Starts the main download process in a background thread."""
    threading.Thread(target=_run_download_in_background, args=(download_jobs,)).start()

# --- 2. Internal Logic (The "Engine Room") ---

def _run_analysis_in_background(file_paths):
    """The actual analysis logic that runs in the background."""
    results = analyze_html_file(file_paths)
    eel.receive_analysis_results(results)

def _run_download_in_background(download_jobs):
    """The actual download logic that runs in a separate thread."""
    succeeded_count = 0
    failed_count = 0
    all_links_to_download = [link for job in download_jobs for link in job.get('links', [])]
    total_links = len(all_links_to_download)
    
    eel.update_log("Initializing browser driver...")
    driver = None
    try:
        driver = setup_driver(lambda msg: eel.update_log(msg), is_headless=False)
        for i, link in enumerate(all_links_to_download):
            eel.update_log(f"--> Starting download for link {i+1}/{total_links}...")
            downloaded_paths = download_file_locally(driver, link, lambda msg: eel.update_log(msg))
            
            if downloaded_paths:
                succeeded_count += 1
                eel.update_log(f"  -> SUCCESS!\n")
            else:
                failed_count += 1
                eel.update_log(f"  -> FAILED.\n")

            eel.update_stats(succeeded_count, failed_count)
            eel.update_progress(((i + 1) / total_links) * 100)
            
        eel.update_log("\n--- ALL DOWNLOADS COMPLETE! ---")
    except Exception as e:
        eel.update_log(f"FATAL ERROR: {e}\n")
    finally:
        if driver:
            eel.update_log("Closing browser driver...")
            driver.quit()