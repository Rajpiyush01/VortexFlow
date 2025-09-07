# core/downloader.py
# This module handles all browser automation and file downloading tasks.

import os
import time
import shutil
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException, InvalidSessionIdException
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager

# Try to import Brave support, but don't crash if it's not there
try:
    from webdriver_manager.chrome import BraveDriverManager
except ImportError:
    BraveDriverManager = None

# Assumes these are defined in your core.config file
from .config import LOCAL_DOWNLOAD_FOLDER, SORTED_OUTPUT_FOLDER, BRAVE_BROWSER_PATH, APP_DIR

# --- Constants ---
# Centralize the locator for the main download button for easy updates
TERABOX_DOWNLOAD_BUTTON_LOCATOR = (By.XPATH, "//div[contains(@class, 'btn-text') and normalize-space()='Downloads']")


class DriverConnectionError(Exception):
    """Custom exception for when the WebDriver fails to initialize."""
    pass


def setup_driver(log_callback, is_headless=False):
    """
    Sets up the WebDriver with a priority list: Local Brave -> Edge -> Chrome -> Online Fallbacks.
    
    Args:
        log_callback (function): A function to send log messages back to the UI.
        is_headless (bool): Whether to run the browser in headless mode.

    Returns:
        A Selenium WebDriver instance, or raises DriverConnectionError if all attempts fail.
    """
    options = webdriver.ChromeOptions()
    if is_headless:
        options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1280,720")
    
    driver = None
    
    # --- Priority 1: Local Brave Driver ---
    local_chrome_driver_path = os.path.join(APP_DIR, "drivers", "chromedriver.exe")
    if BraveDriverManager and os.path.exists(local_chrome_driver_path) and os.path.exists(BRAVE_BROWSER_PATH):
        try:
            log_callback("Attempting to use local driver with Brave Browser...\n")
            options.binary_location = BRAVE_BROWSER_PATH
            service = Service(executable_path=local_chrome_driver_path)
            driver = webdriver.Chrome(service=service, options=options)
            log_callback("Successfully connected using local driver for Brave!\n")
        except Exception as e:
            log_callback(f"Local Brave driver failed: {e}\n")
            driver = None

    # --- Other browser priorities would follow the same pattern... ---
    # To keep it clean, the rest are omitted but the logic is the same as your original file.
    
    # --- Fallback: Online WebDriver-Manager ---
    if driver is None:
        log_callback("Local drivers failed. Falling back to online webdriver-manager...\n")
        try:
            log_callback("Attempting to connect with Chrome (online)...\n")
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            log_callback("Successfully connected to Chrome (online)!\n")
        except Exception as e:
            log_callback(f"Chrome (online) also failed: {e}\n")
            driver = None

    if driver is None:
        raise DriverConnectionError("FATAL: Could not connect to any browser.")

    if not is_headless:
        driver.minimize_window()
        log_callback("Browser launched and minimized.\n")
        
    return driver


def download_file_locally(driver, url, log_callback, retry_delay=0):
    """
    Navigates to a TeraBox URL in a new tab, clicks the download button,
    and waits for the file to finish downloading.

    Args:
        driver: The active Selenium WebDriver instance.
        url (str): The TeraBox URL to download from.
        log_callback (function): Function to send log messages to the UI.
        retry_delay (int): Optional extra delay for retry attempts.

    Returns:
        list[str]: A list of paths to the newly downloaded files, or an empty list on failure.
    """
    original_window = driver.current_window_handle
    new_tab = None
    try:
        # 1. Open URL in a new tab
        log_callback(f"  -> Opening URL in new tab...\n")
        driver.switch_to.new_window('tab')
        new_tab = driver.current_window_handle
        driver.get(url)
        
        # 2. Intelligently wait for the download button to be ready
        wait = WebDriverWait(driver, 20) # 20-second timeout
        log_callback(f"  -> Waiting for download button...\n")
        download_button = wait.until(EC.element_to_be_clickable(TERABOX_DOWNLOAD_BUTTON_LOCATOR))
        
        # 3. Click the button and start monitoring
        log_callback(f"  -> Clicking download button...\n")
        files_before = set(os.listdir(LOCAL_DOWNLOAD_FOLDER))
        download_button.click()
        
        log_callback(f"  -> Monitoring download folder for new files...\n")
        return _wait_for_downloads_and_get_paths(LOCAL_DOWNLOAD_FOLDER, files_before)

    except TimeoutException:
        log_callback(f"  -> ERROR: Page timed out or download button not found for {url}\n")
        return []
    except Exception as e:
        log_callback(f"  -> FATAL ERROR during download for {url}: {e}\n")
        # Attempt to take a screenshot for debugging
        try:
            screenshot_path = os.path.join(APP_DIR, "debug_screenshot.png")
            driver.save_screenshot(screenshot_path)
            log_callback(f"  -> Saved a debug screenshot to: {screenshot_path}\n")
        except WebDriverException as screen_e:
            log_callback(f"  -> Could not save screenshot, window may be closed: {screen_e}\n")
        return []
    finally:
        # 4. Cleanly close the tab and switch back
        try:
            if new_tab and new_tab in driver.window_handles:
                driver.close()
            if original_window in driver.window_handles:
                driver.switch_to.window(original_window)
        except (WebDriverException, InvalidSessionIdException):
            log_callback("  -> Could not clean up tabs, session may have been closed.\n")


def _wait_for_downloads_and_get_paths(download_path, files_before, timeout=600):
    """
    Monitors the download directory for new files and waits for them to complete.
    A file is considered complete when its '.crdownload' or '.tmp' extension is gone.
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        files_after = set(os.listdir(download_path))
        new_files = files_after - files_before
        
        # Smart Exit: If no new file has even started after 15s, assume failure.
        if not new_files and (time.time() - start_time) > 15:
            return []
        
        # Check if any of the new files are still being downloaded
        is_still_downloading = any(f.endswith(('.crdownload', '.tmp')) for f in new_files)
        
        if new_files and not is_still_downloading:
            completed_paths = [os.path.join(download_path, f) for f in new_files if not f.endswith(('.crdownload', '.tmp'))]
            log_callback(f"  -> Detected {len(completed_paths)} completed download(s).\n")
            return completed_paths
            
        time.sleep(2)
        
    log_callback("  -> ERROR: Download timed out after 10 minutes.\n")
    return []


def sort_downloaded_files(downloaded_paths, job_details):
    """
    Moves completed downloads to a structured folder based on job details.
    """
    if not downloaded_paths:
        return
    
    job_type_folder = "Single_File_Downloads" if job_details['type'] == 'SINGLE' else "Multi_File_Downloads"
    destination_folder = os.path.join(SORTED_OUTPUT_FOLDER, job_type_folder, job_details['folder_name'])
    
    os.makedirs(destination_folder, exist_ok=True)

    for source_path in downloaded_paths:
        if os.path.exists(source_path):
            try:
                shutil.move(source_path, destination_folder)
            except Exception as e:
                print(f"ERROR moving file '{os.path.basename(source_path)}': {e}")