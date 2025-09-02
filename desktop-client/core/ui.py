# ui.py
# This module contains the main App class and all the CustomTkinter UI code.

import customtkinter
from PIL import Image
import os
import threading 

# Import our custom modules
from theme import Theme
from ui_components import LinkViewerWindow
# Import all the functions that control the app's behavior
import app_logic

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # --- CONFIGURE THE MAIN WINDOW ---
        self.title("TeraPipeline v3.0")
        self.geometry("800x750")

        # --- APP STATE VARIABLES ---
        self.html_file_paths = []
        self.download_jobs = []
        self.all_unique_links = []
        self.viewer_data = {}
        self.driver = None 
        self.is_paused = threading.Event()
        self.is_stopped = threading.Event()
        self.failed_links = []
        self.headless_mode = customtkinter.BooleanVar(value=False)

        # --- CONFIGURE THE GRID LAYOUT ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- LOAD ICONS ---
        icon_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "icons")
        self.select_icon = customtkinter.CTkImage(Image.open(os.path.join(icon_path, "folder.png")), size=(20, 20))
        self.analyze_icon = customtkinter.CTkImage(Image.open(os.path.join(icon_path, "analyze.png")), size=(20, 20))
        self.download_icon = customtkinter.CTkImage(Image.open(os.path.join(icon_path, "download.png")), size=(20, 20))
        self.view_icon = customtkinter.CTkImage(Image.open(os.path.join(icon_path, "link.png")), size=(20, 20))
        
        # --- CREATE THE TAB VIEW ---
        self.tab_view = customtkinter.CTkTabview(self, fg_color=Theme.LIGHT_GRAY, border_color=Theme.BORDER,
                                                 segmented_button_selected_color=Theme.GREEN,
                                                 segmented_button_selected_hover_color=Theme.GREEN_HOVER,
                                                 segmented_button_unselected_color=Theme.LIGHT_GRAY)
        self.tab_view.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        self.tab_view.add("Bulk Processor")
        self.tab_view.add("Direct Download")

        # --- SETUP UI FOR EACH TAB ---
        self.setup_bulk_processor_tab()
        self.setup_direct_download_tab()

        # --- Check for a saved session on startup ---
        self.after(100, lambda: app_logic.check_for_resume(self))

    def setup_bulk_processor_tab(self):
        bulk_tab = self.tab_view.tab("Bulk Processor")
        bulk_tab.grid_columnconfigure(0, weight=1)
        bulk_tab.grid_rowconfigure(4, weight=1) 

        controls_frame = customtkinter.CTkFrame(bulk_tab, fg_color="transparent")
        controls_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        controls_frame.grid_columnconfigure((0, 1), weight=1)

        self.select_button = customtkinter.CTkButton(controls_frame, text="1. Select HTML Files", image=self.select_icon, 
                                                     command=lambda: app_logic.select_files_event(self), **Theme.BUTTON_STYLE)
        self.select_button.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        self.analyze_button = customtkinter.CTkButton(controls_frame, text="2. Final Analysis", image=self.analyze_icon, 
                                                       command=lambda: app_logic.start_analysis_thread(self), **Theme.BUTTON_STYLE)
        self.analyze_button.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        settings_frame = customtkinter.CTkFrame(bulk_tab, fg_color="transparent")
        settings_frame.grid(row=1, column=0, padx=10, pady=0, sticky="ew")
        
        # UPGRADED: Renamed for clarity
        self.headless_checkbox = customtkinter.CTkCheckBox(settings_frame, text="Minimize Browser on Start (Focus Mode)",
                                                           variable=self.headless_mode, onvalue=True, offvalue=False)
        self.headless_checkbox.pack(side="left", padx=10, pady=5)

        self.manual_start_label = customtkinter.CTkLabel(settings_frame, text="Manual Downloads at Start:")
        self.manual_start_label.pack(side="left", padx=(20, 5), pady=5)
        self.manual_start_entry = customtkinter.CTkEntry(settings_frame, width=40)
        self.manual_start_entry.insert(0, "1")
        self.manual_start_entry.pack(side="left", pady=5)

        stats_frame = customtkinter.CTkFrame(bulk_tab, **Theme.STATS_FRAME_STYLE)
        stats_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        stats_frame.grid_columnconfigure(0, weight=1)

        self.stats_label = customtkinter.CTkLabel(stats_frame, text="Select files and click Analyze to see stats.", font=Theme.BODY_FONT, justify="left")
        self.stats_label.grid(row=0, column=0, padx=20, pady=10, sticky="w")
        
        self.view_links_button = customtkinter.CTkButton(stats_frame, text="View Links", image=self.view_icon, 
                                                         command=lambda: app_logic.view_links_event(self), state="disabled")
        self.view_links_button.grid(row=0, column=1, padx=20, pady=10, sticky="e")
        
        failed_links_frame = customtkinter.CTkFrame(bulk_tab, fg_color=Theme.DARK_GRAY, border_color=Theme.BORDER, border_width=1)
        failed_links_frame.grid(row=3, column=0, padx=10, pady=5, sticky="ew")
        failed_links_frame.grid_columnconfigure(1, weight=1)

        self.failed_links_label = customtkinter.CTkLabel(failed_links_frame, text="Failed Links: 0", font=Theme.BODY_FONT)
        self.failed_links_label.grid(row=0, column=0, padx=20, pady=10)
        
        self.sort_manual_button = customtkinter.CTkButton(failed_links_frame, text="Sort Manual Downloads", 
                                                          command=lambda: app_logic.sort_manual_downloads_event(self), state="disabled")
        self.sort_manual_button.grid(row=0, column=2, padx=20, pady=10)
        
        log_frame = customtkinter.CTkFrame(bulk_tab, fg_color="transparent")
        log_frame.grid(row=4, column=0, padx=10, pady=10, sticky="nsew")
        log_frame.grid_columnconfigure(0, weight=1)
        log_frame.grid_rowconfigure(0, weight=1)

        self.log_textbox_bulk = customtkinter.CTkTextbox(log_frame, **Theme.TEXTBOX_STYLE)
        self.log_textbox_bulk.grid(row=0, column=0, pady=(10,5), sticky="nsew")
        self.log_textbox_bulk.insert("0.0", "Welcome to TeraPipeline v3.0!\n\n")

        self.progress_bar = customtkinter.CTkProgressBar(log_frame, progress_color=Theme.GREEN)
        self.progress_bar.grid(row=1, column=0, pady=(5,10), sticky="ew")
        self.progress_bar.set(0)
        
        self.download_controls_frame = customtkinter.CTkFrame(controls_frame, fg_color="transparent")
        self.download_controls_frame.grid(row=1, column=0, columnspan=2, pady=5)
        self.download_controls_frame.grid_columnconfigure((0,1), weight=1)

        self.pause_resume_button = customtkinter.CTkButton(self.download_controls_frame, text="Pause")
        self.pause_resume_button.grid(row=0, column=0, padx=5, sticky="ew")
        
        self.stop_button = customtkinter.CTkButton(self.download_controls_frame, text="Stop", fg_color=Theme.RED, hover_color=Theme.RED_HOVER)
        self.stop_button.grid(row=0, column=1, padx=5, sticky="ew")

        self.download_controls_frame.grid_remove()

    def setup_direct_download_tab(self):
        direct_tab = self.tab_view.tab("Direct Download")
        direct_tab.grid_columnconfigure(0, weight=1)
        direct_tab.grid_rowconfigure(1, weight=1)
        
        direct_frame = customtkinter.CTkFrame(direct_tab, fg_color="transparent")
        direct_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        direct_frame.grid_columnconfigure(0, weight=1)
        
        self.label_direct = customtkinter.CTkLabel(direct_frame, text="Single Link Downloader", font=Theme.TITLE_FONT)
        self.label_direct.grid(row=0, column=0, padx=20, pady=10)
        
        self.link_entry = customtkinter.CTkEntry(direct_frame, placeholder_text="https://teraboxlink.com/s/...")
        self.link_entry.grid(row=1, column=0, padx=20, pady=5, sticky="ew")

        self.direct_download_button = customtkinter.CTkButton(direct_frame, text="Download & Sort Link", image=self.download_icon, 
                                                              command=lambda: app_logic.start_direct_download_thread(self), **Theme.BUTTON_STYLE)
        self.direct_download_button.grid(row=2, column=0, padx=20, pady=20)
        
        self.log_textbox_direct = customtkinter.CTkTextbox(direct_tab, **Theme.TEXTBOX_STYLE)
        self.log_textbox_direct.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.log_textbox_direct.insert("0.0", "Log messages for direct downloads will appear here...\n")

    def start_download_thread_logic(self):
        """This is called by the ConnectionStatusWindow AFTER a successful connection."""
        app_logic.start_download_thread_logic(self)
