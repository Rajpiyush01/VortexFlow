# theme.py
# This is our dedicated design file. It holds all the styling information for the app,
# acting like a CSS stylesheet but in Python.

import customtkinter

class Theme:
    # --- COLOR PALETTE ---
    GREEN = "#2CC985"
    GREEN_HOVER = "#27B376"
    BLACK = "#000000"
    DARK_GRAY = "#1D1E1E"
    LIGHT_GRAY = "#242424"
    BORDER = "#323332"
    RED = "#E53935"
    RED_HOVER = "#C62828"

    # --- FONTS ---
    TITLE_FONT = ("Arial", 16, "bold")
    BODY_FONT = ("Arial", 14)
    REPORT_FONT = ("Consolas", 12)

    # --- WIDGET STYLES ---
    # We can define reusable style dictionaries here
    
    BUTTON_STYLE = {
        "height": 40,
        "fg_color": GREEN,
        "hover_color": GREEN_HOVER,
        "text_color": BLACK,
        "corner_radius": 8
    }

    TEXTBOX_STYLE = {
        "corner_radius": 8,
        "border_width": 1,
        "border_color": BORDER
    }

    STATS_FRAME_STYLE = {
        "fg_color": DARK_GRAY,
        "border_color": BORDER,
        "border_width": 1
    }