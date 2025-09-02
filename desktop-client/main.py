# main.py
# This is the main entry point for the TeraPipeline application.

import os
import customtkinter

# Import the main App class from our UI module
from ui import App
# Import folder configurations
from config import LOCAL_DOWNLOAD_FOLDER, SORTED_OUTPUT_FOLDER

if __name__ == "__main__":
    # Create necessary folders on startup if they don't exist
    os.makedirs(LOCAL_DOWNLOAD_FOLDER, exist_ok=True)
    os.makedirs(SORTED_OUTPUT_FOLDER, exist_ok=True)
    
    # Set the appearance mode
    customtkinter.set_appearance_mode("Dark")
    
    # Create and run the application
    app = App()
    app.mainloop()
