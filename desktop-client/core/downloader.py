# downloader.py
# This module handles all Selenium browser automation and file operations.

import os
import time
import shutil
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from config import LOCAL_DOWNLOAD_FOLDER, SORTED_OUTPUT_FOLDER, BRAVE_BROWSER_PATH

class DriverConnectionError(Exception):
    pass

def setup_driver(log_callback, is_headless=False):
    """Sets up and connects to the Selenium WebDriver."""
    try:
        options = webdriver.ChromeOptions()
        options.binary_location = BRAVE_BROWSER_PATH
        prefs = {"download.default_directory": LOCAL_DOWNLOAD_FOLDER}
        options.add_experimental_option("prefs", prefs)
        
        if is_headless:
            options.add_argument("--headless")
            options.add_argument("--window-size=1920,1080")
            log_callback("Connecting to browser in Stealth Mode...\n")
        else:
            options.add_experimental_option("debuggerAddress", "localhost:9222")
            log_callback("Connecting to manually opened browser...\n")

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        if not is_headless:
            log_callback("Successfully connected to the browser!\n")
        return driver
    except Exception as e:
        error_message = f"Could not connect to browser. Details: {e}"
        raise DriverConnectionError(error_message)

def download_file_locally(driver, url, log_callback, retry_delay=0):
    """Navigates to a URL, clicks download, and waits for the file."""
    original_window = driver.current_window_handle
    new_tab = None
    try:
        driver.switch_to.new_window('tab')
        new_tab = driver.current_window_handle
        driver.get(url)
        wait = WebDriverWait(driver, 20)
        # Add the extra delay for retries
        time.sleep(3 + retry_delay)

        download_button_locator = (By.XPATH, "//div[@class='btn-text' and normalize-space()='Downloads']")
        download_button = wait.until(EC.element_to_be_clickable(download_button_locator))
        
        files_before = set(os.listdir(LOCAL_DOWNLOAD_FOLDER))
        download_button.click()
        
        return _wait_for_downloads_and_get_paths(LOCAL_DOWNLOAD_FOLDER, files_before)

    except Exception as e:
        log_callback(f"  -> ERROR during download for {url}: {e}\n")
        return []
    finally:
        if new_tab and new_tab in driver.window_handles:
            driver.close()
        driver.switch_to.window(original_window)

def _wait_for_downloads_and_get_paths(download_path, files_before, timeout=600):
    """Waits for .crdownload files to disappear and returns a list of new file paths."""
    time.sleep(5)
    seconds = 0
    while seconds < timeout:
        still_downloading = False
        files_after = set(os.listdir(download_path))
        new_files = files_after - files_before
        
        if not new_files and seconds > 15: break
        
        for file_name in new_files:
            if file_name.endswith(('.crdownload', '.tmp')):
                still_downloading = True; break
        
        if not still_downloading and new_files:
            return [os.path.join(download_path, f) for f in new_files]
        time.sleep(2); seconds += 2
    return []

def sort_downloaded_files(downloaded_paths, job_details):
    """Sorts downloaded files into the correct final directory structure."""
    if not downloaded_paths: return
    
    # This logic now correctly checks the original job type
    if job_details['type'] == 'SINGLE':
        destination_folder = os.path.join(SORTED_OUTPUT_FOLDER, "Single_File_Downloads", job_details['folder_name'])
    else: # This means it was a 'MULTI' link job
        destination_folder = os.path.join(SORTED_OUTPUT_FOLDER, "Multi_File_Downloads", job_details['folder_name'])
    
    os.makedirs(destination_folder, exist_ok=True)

    for source_path in downloaded_paths:
        if os.path.exists(source_path):
            try:
                shutil.move(source_path, destination_folder)
            except Exception as e:
                print(f"ERROR moving file: {e}")
