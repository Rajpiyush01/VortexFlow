# ui_components.py
# This module contains reusable, complex UI components for our app.

import customtkinter
from collections import defaultdict
import threading

# Import our custom modules
from theme import Theme
from downloader import setup_driver, DriverConnectionError

class LinkViewerWindow(customtkinter.CTkToplevel):
    """
    A professional, high-performance pop-up window for viewing categorized links.
    It features a navigation pane on the left and a content viewer on the right.
    """
    def __init__(self, viewer_data, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.viewer_data = viewer_data
        self.title("TeraPipeline - Link Viewer")
        self.geometry("1000x700")

        # --- CONFIGURE GRID LAYOUT ---
        self.grid_columnconfigure(1, weight=1) 
        self.grid_rowconfigure(0, weight=1)

        # --- LEFT NAVIGATION PANE ---
        nav_frame = customtkinter.CTkScrollableFrame(self, label_text="Categories", label_font=Theme.TITLE_FONT, width=250)
        nav_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # --- RIGHT CONTENT PANE ---
        self.content_textbox = customtkinter.CTkTextbox(self, wrap="word", font=Theme.REPORT_FONT)
        self.content_textbox.grid(row=0, column=1, padx=(0, 10), pady=10, sticky="nsew")
        
        # --- POPULATE NAVIGATION BUTTONS ---
        for category_name in self.viewer_data.keys():
            button = customtkinter.CTkButton(nav_frame, text=category_name,
                                             command=lambda name=category_name: self.display_links_for_category(name),
                                             **Theme.BUTTON_STYLE)
            button.pack(fill="x", padx=5, pady=5)

        if self.viewer_data:
            first_category = list(self.viewer_data.keys())[0]
            self.display_links_for_category(first_category)

    def display_links_for_category(self, category_name):
        """Updates the content textbox with the links for the selected category."""
        self.content_textbox.configure(state="normal")
        self.content_textbox.delete("0.0", "end")
        
        report = f"--- Displaying: {category_name} ---\n\n"
        content = self.viewer_data[category_name]

        if category_name == "Other Links":
            for domain, links in sorted(content.items()):
                report += f"--- {domain} ({len(links)} links) ---\n"
                report += "\n".join(links) + "\n\n"
        elif category_name == "TeraBox Singles":
            for job in content:
                report += f"{job['links'][0]}\n"
        elif "TeraBox Multi-Links" in category_name:
            for job in content:
                report += f"--- Job from {job['source_file']} ---\n"
                report += "\n".join(job['links']) + "\n\n"

        self.content_textbox.insert("0.0", report.strip())
        self.content_textbox.configure(state="disabled")

class ConnectionStatusWindow(customtkinter.CTkToplevel):
    """
    A pop-up that handles the browser connection process in a background thread,
    providing live feedback to the user without freezing the main app.
    """
    def __init__(self, app_instance, is_headless=False, callback_on_success=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.app = app_instance
        self.is_headless = is_headless
        self.callback_on_success = callback_on_success

        self.title("Connecting...")
        self.geometry("450x250")
        self.grab_set()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.status_label = customtkinter.CTkLabel(self, text="Attempting to connect to browser...", font=Theme.TITLE_FONT)
        self.status_label.pack(pady=20)

        self.progress_bar = customtkinter.CTkProgressBar(self, mode="indeterminate")
        self.progress_bar.pack(pady=10, padx=20, fill="x")
        self.progress_bar.start()

        self.details_textbox = customtkinter.CTkTextbox(self, wrap="word", height=100)
        self.details_textbox.pack(pady=10, padx=20, fill="x")
        self.details_textbox.insert("0.0", "Please wait...")
        self.details_textbox.configure(state="disabled")
        
        self.connection_thread = threading.Thread(target=self._connect_to_driver_thread, daemon=True)
        self.connection_thread.start()

    def _connect_to_driver_thread(self):
        """Runs in the background to avoid freezing the UI."""
        try:
            driver = setup_driver(lambda msg: self.after(0, self.update_log, msg), is_headless=self.is_headless)
            self.after(0, self.on_connection_success, driver)
        except DriverConnectionError as e:
            self.after(0, self.on_connection_failure, str(e))

    def update_log(self, message):
        """Safely updates the textbox from the background thread."""
        self.details_textbox.configure(state="normal")
        self.details_textbox.insert("end", message)
        self.details_textbox.configure(state="disabled")

    def on_connection_success(self, driver):
        """Called on the main thread when connection is successful."""
        self.progress_bar.stop()
        self.status_label.configure(text="Connection Successful!", text_color=Theme.GREEN)
        self.app.driver = driver
        
        self.after(1500, self.start_main_task)

    def start_main_task(self):
        self.destroy()
        if self.callback_on_success:
            self.callback_on_success()

    def on_connection_failure(self, error_message):
        """Called on the main thread when connection fails."""
        self.progress_bar.stop()
        self.status_label.configure(text="Connection Failed!", text_color=Theme.RED)
        
        tips = ("Please ensure you have followed these steps:\n\n"
                "1. Close ALL other Brave browser windows.\n"
                "2. Open a Command Prompt (CMD).\n"
                "3. Paste and run the command:\n"
                "   start \"\" \"C:\\...\\brave.exe\" --remote-debugging-port=9222\n"
                "(Ensure the path in config.py is correct)\n"
                "4. In the new Brave window, log in to TeraBox.\n"
                "5. Close this window and try again.")
        
        self.details_textbox.configure(state="normal")
        self.details_textbox.delete("0.0", "end")
        self.details_textbox.insert("0.0", tips)
        self.details_textbox.configure(state="disabled")
        
        self.app.reset_ui_after_stop()
