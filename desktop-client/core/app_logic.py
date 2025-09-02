# app_logic.py (V3.0 - Smart Sorting 2.0)
# This is the "backend brain" of our application.

import threading
import webbrowser
import os
import time
from tkinter import filedialog
from collections import defaultdict

from CTkMessagebox import CTkMessagebox

# Import our custom modules
from analyzer import analyze_html_files, _categorize_link
from downloader import setup_driver, download_file_locally, sort_downloaded_files, DriverConnectionError
from session_manager import save_session, load_session, clear_session, save_failed_links, load_failed_links
from ui_components import LinkViewerWindow, ConnectionStatusWindow
from config import LOCAL_DOWNLOAD_FOLDER

# --- Session Logic ---
def check_for_resume(app):
    """Checks if a session file exists and asks the user to resume."""
    saved_jobs = load_session()
    if saved_jobs:
        total_remaining_links = sum(len(job.get('links', [])) for job in saved_jobs)
        
        msg = CTkMessagebox(title="Resume Session?", 
                            message=f"Found an unfinished session with {total_remaining_links} links remaining. Do you want to resume?",
                            icon="question", option_1="No, Delete", option_2="Yes")
        response = msg.get()
        
        if response == "Yes":
            app.log_textbox_bulk.insert("end", "Resuming previous session...\n")
            app.download_jobs = saved_jobs
            app.analyze_button.configure(state="normal", text="3. Resume Downloading", command=lambda: start_download_thread(app))
            app.select_button.configure(state="disabled")
            app.view_links_button.configure(state="disabled")
            app.headless_checkbox.configure(state="normal") # Allow changing stealth mode on resume
        else:
            clear_session()
            app.log_textbox_bulk.insert("end", "Previous session deleted.\n")

# --- Analysis Logic ---

def start_analysis_thread(app):
    if not app.html_file_paths:
        app.log_textbox_bulk.insert("end", "ERROR: No HTML files selected.\n\n")
        return
    
    app.analyze_button.configure(state="disabled", text="Analyzing...")
    app.select_button.configure(state="disabled")
    app.view_links_button.configure(state="disabled")
    app.progress_bar.start()

    thread = threading.Thread(target=lambda: _run_analysis_in_background(app), daemon=True)
    thread.start()

def _run_analysis_in_background(app):
    results = analyze_html_files(app.html_file_paths)
    app.after(0, _update_ui_after_analysis, app, results)

def _update_ui_after_analysis(app, results):
    app.download_jobs = results["download_jobs"]
    app.all_unique_links = results["unique_links"]
    
    link_counts_by_domain = defaultdict(int)
    for link in app.all_unique_links:
        domain = _categorize_link(link)
        link_counts_by_domain[domain] += 1

    stats_text = "Analysis Complete!\n\n"
    stats_text += f" ▸ Total Links Found: {results['raw_count']} | Duplicates: {results['duplicate_count']} | Unique Links: {len(results['unique_links'])}\n\n"
    stats_text += "--- TeraBox Download Plan ---\n"
    stats_text += f" ▸ Unique TeraBox Links to Download: {results['terabox_count']}\n"
    stats_text += f" ▸ Single-Link Messages: {sum(1 for j in app.download_jobs if j['type'] == 'SINGLE')} | "
    stats_text += f"Multi-Link Messages: {sum(1 for j in app.download_jobs if j['type'] == 'MULTI')}\n\n"
    stats_text += "--- All Other Domains Found ---\n"
    
    other_links_str = ""
    for domain, count in sorted(link_counts_by_domain.items()):
        if domain != "TeraBox":
            other_links_str += f" ▸ {domain}: {count}\n"
    
    stats_text += other_links_str if other_links_str else " ▸ None\n"

    app.stats_label.configure(text=stats_text.strip())
    app.log_textbox_bulk.insert("end", "Analysis complete. Review stats and links, then click 'Start Downloading'.\n\n")
    
    prepare_viewer_data(app)
    app.view_links_button.configure(state="normal")
    app.analyze_button.configure(state="normal", text="3. Start Downloading", command=lambda: start_download_thread(app))
    app.select_button.configure(state="normal")
    app.progress_bar.stop()
    app.progress_bar.set(0)

# --- UI Interaction Logic ---

def select_files_event(app):
    app.html_file_paths = filedialog.askopenfilenames(title="Select HTML files", filetypes=(("HTML files", "*.html"),("All files", "*.*")))
    if app.html_file_paths:
        app.log_textbox_bulk.insert("end", f"Selected {len(app.html_file_paths)} file(s):\n")
        for path in app.html_file_paths:
            app.log_textbox_bulk.insert("end", f" - {os.path.basename(path)}\n")
        app.log_textbox_bulk.insert("end", "Ready to analyze. Click '2. Final Analysis'.\n\n")
        app.view_links_button.configure(state="disabled")
        app.stats_label.configure(text="Select files and click Analyze to see stats.")
        app.analyze_button.configure(text="2. Final Analysis", command=lambda: start_analysis_thread(app))
    else:
        app.log_textbox_bulk.insert("end", "No files selected.\n\n")

def prepare_viewer_data(app):
    app.viewer_data = defaultdict(list)
    other_links_by_domain = defaultdict(list)
    for link in app.all_unique_links:
        domain = _categorize_link(link)
        if domain != "TeraBox":
            other_links_by_domain[domain].append(link)
    if other_links_by_domain: app.viewer_data["Other Links"] = other_links_by_domain

    single_link_jobs = [job for job in app.download_jobs if job['type'] == 'SINGLE']
    if single_link_jobs: app.viewer_data["TeraBox Singles"] = single_link_jobs
        
    multi_link_jobs = [job for job in app.download_jobs if job['type'] == 'MULTI']
    if multi_link_jobs:
        page_num, line_count, line_limit, current_page_jobs = 1, 0, 50, []
        for job in multi_link_jobs:
            job_line_count = 1 + len(job['links'])
            if line_count + job_line_count > line_limit and line_count > 0:
                app.viewer_data[f"TeraBox Multi-Links (Page {page_num})"] = current_page_jobs
                page_num += 1; current_page_jobs = []; line_count = 0
            current_page_jobs.append(job); line_count += job_line_count
        if current_page_jobs: app.viewer_data[f"TeraBox Multi-Links (Page {page_num})"] = current_page_jobs

def view_links_event(app):
    if not app.viewer_data:
        app.log_textbox_bulk.insert("end", "No links to view. Please run analysis first.\n\n")
        return
    
    link_viewer = LinkViewerWindow(viewer_data=app.viewer_data)
    link_viewer.grab_set()

# --- Download Logic ---

def start_download_thread(app):
    if not app.download_jobs:
        app.log_textbox_bulk.insert("end", "ERROR: No download jobs to start. Please run analysis first.\n\n")
        return

    is_headless = app.headless_mode.get()
    connection_window = ConnectionStatusWindow(app_instance=app, is_headless=is_headless, 
                                               callback_on_success=app.start_download_thread_logic)
    connection_window.grab_set()

def start_download_thread_logic(app):
    app.is_paused.clear(); app.is_stopped.clear()
    app.download_controls_frame.grid()
    app.pause_resume_button.configure(text="Pause", command=lambda: pause_download(app))
    app.stop_button.configure(command=lambda: stop_download(app))
    app.analyze_button.configure(state="disabled")
    app.select_button.configure(state="disabled")
    app.view_links_button.configure(state="normal")
    app.headless_checkbox.configure(state="disabled")

    thread = threading.Thread(target=lambda: _run_download_in_background(app), daemon=True)
    thread.start()

def _run_download_in_background(app):
    total_links = sum(len(job['links']) for job in app.download_jobs)
    links_processed = 0
    
    app.failed_links = []
    remaining_jobs = [job.copy() for job in app.download_jobs]

    for job_index, job in enumerate(remaining_jobs):
        links_to_process = list(job['links'])
        for link_index, link in enumerate(links_to_process):
            if app.is_stopped.is_set():
                current_job_remaining_links = links_to_process[link_index:]
                job['links'] = current_job_remaining_links
                final_remaining_jobs = remaining_jobs[job_index:]
                save_session(final_remaining_jobs)
                app.after(0, _update_download_progress, app, links_processed, total_links, "Download stopped. Progress saved.\n")
                app.after(0, reset_ui_after_stop, app)
                return
            
            while app.is_paused.is_set(): time.sleep(1)
            
            links_processed += 1
            message = f"({links_processed}/{total_links}) Processing: {link}\n"
            app.after(0, _update_download_progress, app, links_processed, total_links, message)
            
            downloaded_paths = download_file_locally(app.driver, link, lambda msg: app.after(0, app.log_textbox_bulk.insert, "end", msg))
            
            if downloaded_paths:
                sort_downloaded_files(downloaded_paths, job)
            else:
                failed_job_copy = job.copy()
                failed_job_copy['links'] = [link]
                app.failed_links.append(failed_job_copy)
                app.after(0, update_failed_links_ui, app)
                save_failed_links(app.failed_links)

    # app_logic.py (V3.0 - Smart Sorting 2.0 & Manual Start Fix)
# This is the "backend brain" of our application.

import threading
import webbrowser
import os
import time
from tkinter import filedialog
from collections import defaultdict

from CTkMessagebox import CTkMessagebox

# Import our custom modules
from analyzer import analyze_html_files, _categorize_link
from downloader import setup_driver, download_file_locally, sort_downloaded_files, DriverConnectionError
from session_manager import save_session, load_session, clear_session, save_failed_links, load_failed_links
from ui_components import LinkViewerWindow, ConnectionStatusWindow
from config import LOCAL_DOWNLOAD_FOLDER

# --- Session Logic ---
def check_for_resume(app):
    """Checks if a session file exists and asks the user to resume."""
    saved_jobs = load_session()
    if saved_jobs:
        total_remaining_links = sum(len(job.get('links', [])) for job in saved_jobs)
        
        msg = CTkMessagebox(title="Resume Session?", 
                            message=f"Found an unfinished session with {total_remaining_links} links remaining. Do you want to resume?",
                            icon="question", option_1="No, Delete", option_2="Yes")
        response = msg.get()
        
        if response == "Yes":
            app.log_textbox_bulk.insert("end", "Resuming previous session...\n")
            app.download_jobs = saved_jobs
            app.analyze_button.configure(state="normal", text="3. Resume Downloading", command=lambda: start_download_thread(app))
            app.select_button.configure(state="disabled")
            app.view_links_button.configure(state="disabled")
            app.headless_checkbox.configure(state="normal")
        else:
            clear_session()
            app.log_textbox_bulk.insert("end", "Previous session deleted.\n")

# --- Analysis Logic ---
def start_analysis_thread(app):
    # ... (This logic is unchanged)
    if not app.html_file_paths:
        app.log_textbox_bulk.insert("end", "ERROR: No HTML files selected.\n\n")
        return
    app.analyze_button.configure(state="disabled", text="Analyzing...")
    app.select_button.configure(state="disabled")
    app.view_links_button.configure(state="disabled")
    app.progress_bar.start()
    thread = threading.Thread(target=lambda: _run_analysis_in_background(app), daemon=True)
    thread.start()

def _run_analysis_in_background(app):
    results = analyze_html_files(app.html_file_paths)
    app.after(0, _update_ui_after_analysis, app, results)

def _update_ui_after_analysis(app, results):
    # ... (This logic is unchanged)
    app.download_jobs = results["download_jobs"]
    app.all_unique_links = results["unique_links"]
    link_counts_by_domain = defaultdict(int)
    for link in app.all_unique_links:
        domain = _categorize_link(link)
        link_counts_by_domain[domain] += 1
    stats_text = "Analysis Complete!\n\n"
    stats_text += f" ▸ Total Links Found: {results['raw_count']} | Duplicates: {results['duplicate_count']} | Unique Links: {len(results['unique_links'])}\n\n"
    stats_text += "--- TeraBox Download Plan ---\n"
    stats_text += f" ▸ Unique TeraBox Links to Download: {results['terabox_count']}\n"
    stats_text += f" ▸ Single-Link Messages: {sum(1 for j in app.download_jobs if j['type'] == 'SINGLE')} | "
    stats_text += f"Multi-Link Messages: {sum(1 for j in app.download_jobs if j['type'] == 'MULTI')}\n\n"
    stats_text += "--- All Other Domains Found ---\n"
    other_links_str = ""
    for domain, count in sorted(link_counts_by_domain.items()):
        if domain != "TeraBox":
            other_links_str += f" ▸ {domain}: {count}\n"
    stats_text += other_links_str if other_links_str else " ▸ None\n"
    app.stats_label.configure(text=stats_text.strip())
    app.log_textbox_bulk.insert("end", "Analysis complete. Review stats and links, then click 'Start Downloading'.\n\n")
    prepare_viewer_data(app)
    app.view_links_button.configure(state="normal")
    app.analyze_button.configure(state="normal", text="3. Start Downloading", command=lambda: start_download_thread(app))
    app.select_button.configure(state="normal")
    app.progress_bar.stop()
    app.progress_bar.set(0)

# --- UI Interaction Logic ---
def select_files_event(app):
    app.html_file_paths = filedialog.askopenfilenames(title="Select HTML files", filetypes=(("HTML files", "*.html"),("All files", "*.*")))
    if app.html_file_paths:
        app.log_textbox_bulk.insert("end", f"Selected {len(app.html_file_paths)} file(s):\n")
        for path in app.html_file_paths:
            app.log_textbox_bulk.insert("end", f" - {os.path.basename(path)}\n")
        app.log_textbox_bulk.insert("end", "Ready to analyze. Click '2. Final Analysis'.\n\n")
        app.view_links_button.configure(state="disabled")
        app.stats_label.configure(text="Select files and click Analyze to see stats.")
        app.analyze_button.configure(text="2. Final Analysis", command=lambda: start_analysis_thread(app))
    else:
        app.log_textbox_bulk.insert("end", "No files selected.\n\n")

def prepare_viewer_data(app):
    app.viewer_data = defaultdict(list)
    other_links_by_domain = defaultdict(list)
    for link in app.all_unique_links:
        domain = _categorize_link(link)
        if domain != "TeraBox":
            other_links_by_domain[domain].append(link)
    if other_links_by_domain: app.viewer_data["Other Links"] = other_links_by_domain

    single_link_jobs = [job for job in app.download_jobs if job['type'] == 'SINGLE']
    if single_link_jobs: app.viewer_data["TeraBox Singles"] = single_link_jobs
        
    multi_link_jobs = [job for job in app.download_jobs if job['type'] == 'MULTI']
    if multi_link_jobs:
        page_num, line_count, line_limit, current_page_jobs = 1, 0, 50, []
        for job in multi_link_jobs:
            job_line_count = 1 + len(job['links'])
            if line_count + job_line_count > line_limit and line_count > 0:
                app.viewer_data[f"TeraBox Multi-Links (Page {page_num})"] = current_page_jobs
                page_num += 1; current_page_jobs = []; line_count = 0
            current_page_jobs.append(job); line_count += job_line_count
        if current_page_jobs: app.viewer_data[f"TeraBox Multi-Links (Page {page_num})"] = current_page_jobs

def view_links_event(app):
    if not app.viewer_data:
        app.log_textbox_bulk.insert("end", "No links to view. Please run analysis first.\n\n")
        return
    
    link_viewer = LinkViewerWindow(viewer_data=app.viewer_data)
    link_viewer.grab_set()

# --- Download Logic ---
def start_download_thread(app):
    if not app.download_jobs:
        app.log_textbox_bulk.insert("end", "ERROR: No download jobs to start. Please run analysis first.\n\n")
        return

    is_headless = app.headless_mode.get()
    connection_window = ConnectionStatusWindow(app_instance=app, is_headless=is_headless, 
                                               callback_on_success=app.start_download_thread_logic)
    connection_window.grab_set()

def start_download_thread_logic(app):
    app.is_paused.clear(); app.is_stopped.clear()
    app.download_controls_frame.grid()
    app.pause_resume_button.configure(text="Pause", command=lambda: pause_download(app))
    app.stop_button.configure(command=lambda: stop_download(app))
    app.analyze_button.configure(state="disabled")
    app.select_button.configure(state="disabled")
    app.view_links_button.configure(state="normal")
    app.headless_checkbox.configure(state="disabled")

    thread = threading.Thread(target=lambda: _run_download_in_background(app), daemon=True)
    thread.start()

def _run_download_in_background(app):
    total_links = sum(len(job['links']) for job in app.download_jobs)
    links_processed = 0
    
    app.failed_links = load_failed_links() # Load any previously failed links
    app.after(0, update_failed_links_ui, app)
    
    remaining_jobs = [job.copy() for job in app.download_jobs]
    
    try:
        manual_start_count = int(app.manual_start_entry.get())
    except (ValueError, TypeError):
        manual_start_count = 0

    for job_index, job in enumerate(remaining_jobs):
        links_to_process = list(job['links'])
        for link_index, link in enumerate(links_to_process):
            if app.is_stopped.is_set():
                # ... (Save session logic is unchanged)
                return
            
            while app.is_paused.is_set(): time.sleep(1)
            
            # --- UPGRADED MANUAL DOWNLOAD LOGIC ---
            if links_processed < manual_start_count:
                message = f"--> MANUAL ACTION ({links_processed + 1}/{manual_start_count}): {link}\n"
                app.after(0, _update_download_progress, app, links_processed, total_links, message)
                
                completion_event = threading.Event()
                app.after(0, handle_manual_download_ui, app, link, completion_event)
                completion_event.wait() # Background thread waits here
                
                app.after(0, app.log_textbox_bulk.insert, "end", "Attempting to sort manually downloaded file(s)...\n")
                app.after(0, sort_manual_downloads_event, app)
                
                links_processed += 1
                continue

            if links_processed == manual_start_count and manual_start_count > 0:
                 app.after(0, app.log_textbox_bulk.insert, "end", "\n--- Manual count reached. ENGAGING FULL-AUTO MODE! ---\n")

            links_processed += 1
            message = f"({links_processed}/{total_links}) Processing: {link}\n"
            app.after(0, _update_download_progress, app, links_processed, total_links, message)
            
            downloaded_paths = download_file_locally(app.driver, link, lambda msg: app.after(0, app.log_textbox_bulk.insert, "end", msg))
            
            if downloaded_paths:
                sort_downloaded_files(downloaded_paths, job)
            else:
                failed_job_copy = job.copy()
                failed_job_copy['links'] = [link]
                app.failed_links.append(failed_job_copy)
                app.after(0, update_failed_links_ui, app)
                save_failed_links(app.failed_links) # Save to file immediately

    # --- LAST CHANCE AUTO-RETRY PASS ---
    if app.failed_links and not app.is_stopped.is_set():
        app.after(0, app.log_textbox_bulk.insert, "end", "\n--- Starting Last Chance Retry Pass... ---\n")
        time.sleep(2)
        
        jobs_to_retry = list(app.failed_links)
        app.failed_links.clear()

        for failed_job in jobs_to_retry:
            if app.is_stopped.is_set():
                save_failed_links(jobs_to_retry)
                app.after(0, reset_ui_after_stop, app)
                return

            while app.is_paused.is_set(): time.sleep(1)
            
            link_to_retry = failed_job['links'][0]
            message = f"Retrying: {link_to_retry}\n"
            app.after(0, app.log_textbox_bulk.insert, "end", message)
            
            downloaded_paths = download_file_locally(app.driver, link_to_retry, 
                                                     lambda msg: app.after(0, app.log_textbox_bulk.insert, "end", msg), 
                                                     retry_delay=2)
            
            if downloaded_paths:
                sort_downloaded_files(downloaded_paths, failed_job)
                app.after(0, app.log_textbox_bulk.insert, "end", f"  -> SUCCESS on retry: {link_to_retry}\n")
            else:
                app.failed_links.append(failed_job)
                app.after(0, app.log_textbox_bulk.insert, "end", f"  -> FAILED on retry: {link_to_retry}\n")
                app.after(0, update_failed_links_ui, app)

    clear_session()
    save_failed_links(app.failed_links)
    app.after(0, reset_ui_after_stop, app)
    app.after(0, app.log_textbox_bulk.insert, "end", "\n--- ALL DOWNLOADS COMPLETE! ---\n")
    if app.failed_links:
        app.after(0, app.log_textbox_bulk.insert, "end", "\n--- SOME LINKS FAILED. You can download them manually and use the 'Sort Manual Downloads' button. ---\n")

def _update_download_progress(app, current, total, message):
    app.log_textbox_bulk.insert("end", message)
    app.log_textbox_bulk.see("end")
    if total > 0: app.progress_bar.set(current / total)

def pause_download(app):
    app.is_paused.set()
    app.log_textbox_bulk.insert("end", "\n--- Download Paused ---\n")
    app.pause_resume_button.configure(text="Resume", command=lambda: resume_download(app))

def resume_download(app):
    app.is_paused.clear()
    app.log_textbox_bulk.insert("end", "\n--- Download Resumed ---\n")
    app.pause_resume_button.configure(text="Pause", command=lambda: pause_download(app))

def stop_download(app):
    app.is_stopped.set()

def reset_ui_after_stop(app):
    app.download_controls_frame.grid_remove()
    app.analyze_button.configure(state="normal", text="2. Final Analysis", command=lambda: start_analysis_thread(app))
    app.select_button.configure(state="normal")
    app.view_links_button.configure(state="normal")
    app.headless_checkbox.configure(state="normal")
    app.progress_bar.set(0)
    if app.driver:
        try:
            app.driver.quit()
        except Exception as e:
            print(f"Error quitting driver: {e}")
        app.driver = None

def start_direct_download_thread(app):
    link = app.link_entry.get()
    if not link:
        app.log_textbox_direct.insert("end", "ERROR: Please paste a link in the box first.\n\n")
        return
    
    category = _categorize_link(link)
    if category != "TeraBox":
        app.log_textbox_direct.insert("end", f"INFO: This is not a TeraBox link ({category}). Opening in browser.\n\n")
        webbrowser.open(link, new=2)
        return

    app.direct_download_button.configure(state="disabled", text="Downloading...")
    is_headless = app.headless_mode.get()
    
    callback = lambda: _run_direct_download_in_background(app, link)
    connection_window = ConnectionStatusWindow(app_instance=app, is_headless=is_headless, 
                                               callback_on_success=callback)
    connection_window.grab_set()

def _run_direct_download_in_background(app, link):
    try:
        if not app.driver:
             app.driver = setup_driver(lambda msg: app.after(0, app.log_textbox_direct.insert, "end", msg), is_headless=app.headless_mode.get())
             if app.driver is None:
                raise DriverConnectionError("Failed to setup driver.")

        downloaded_paths = download_file_locally(app.driver, link, lambda msg: app.after(0, app.log_textbox_direct.insert, "end", msg))
        
        if downloaded_paths:
            job_details = {"folder_name": f"Direct_Download_{int(time.time())}", "type": "SINGLE"}
            sort_downloaded_files(downloaded_paths, job_details)
            message = f"Successfully downloaded and sorted {len(downloaded_paths)} file(s)."
            app.after(0, _update_ui_after_direct_download, app, {"success": True, "message": message})
        else:
            raise Exception("Download failed.")
    except Exception as e:
        message = f"Download failed. Error: {e}"
        app.after(0, _update_ui_after_direct_download, app, {"success": False, "message": message})

def _update_ui_after_direct_download(app, result):
    app.log_textbox_direct.insert("end", f"{result['message']}\n\n")
    app.direct_download_button.configure(state="normal", text="Download & Sort Link")
    
def update_failed_links_ui(app):
    """Updates the failed links counter in the UI."""
    count = len(app.failed_links)
    app.failed_links_label.configure(text=f"Failed Links: {count}")
    if count > 0:
        app.sort_manual_button.configure(state="normal")
    else:
        app.sort_manual_button.configure(state="disabled")

def sort_manual_downloads_event(app):
    """Handles the logic for sorting manually downloaded files."""
    app.log_textbox_bulk.insert("end", "\n--- Starting Manual Sort ---\n")
    
    files_in_download_folder = os.listdir(LOCAL_DOWNLOAD_FOLDER)
    if not files_in_download_folder:
        app.log_textbox_bulk.insert("end", "No files found in the DOWNLOADS folder to sort.\n")
        return

    failed_jobs = load_failed_links()
    if not failed_jobs:
        app.log_textbox_bulk.insert("end", "No failed links on record to match against.\n")
        return

    sorted_something = False
    remaining_failed_jobs = list(failed_jobs) 
    files_to_sort = list(files_in_download_folder)

    for filename in files_to_sort:
        file_path = os.path.join(LOCAL_DOWNLOAD_FOLDER, filename)
        if os.path.isdir(file_path): continue

        for i, failed_job in enumerate(failed_jobs):
            link = failed_job['links'][0]
            link_id = link.split('/')[-1]
            if link_id in filename:
                app.log_textbox_bulk.insert("end", f"Found match: '{filename}' seems to belong to failed link ...{link_id}\n")
                sort_downloaded_files([file_path], failed_job)
                
                # Find the correct job to remove from the list
                for j, job in enumerate(remaining_failed_jobs):
                    if job['links'][0] == link:
                        remaining_failed_jobs.pop(j)
                        break
                sorted_something = True
                break

    if sorted_something:
        app.log_textbox_bulk.insert("end", "Manual sort complete. Updating failed links list.\n")
        save_failed_links(remaining_failed_jobs)
        app.failed_links = remaining_failed_jobs
        update_failed_links_ui(app)
    else:
        app.log_textbox_bulk.insert("end", "Could not find any matches for files in the DOWNLOADS folder.\n")

def handle_manual_download_ui(app, link, completion_event):
    """This function runs on the main UI thread to handle a single manual download."""
    webbrowser.open(link, new=2)
    msg = CTkMessagebox(title="Manual Download Action",
                        message=f"The app has opened a link for you to download manually.\n\n"
                                f"Please download the file(s) to your 'DOWNLOADS' folder.\n\n"
                                f"Click 'OK' ONLY after the download is fully complete.",
                        icon="info", option_1="OK")
    msg.get()
    completion_event.set()

# ... (The rest of the app_logic.py file is unchanged)

