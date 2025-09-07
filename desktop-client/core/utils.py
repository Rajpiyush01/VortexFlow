# core/utils.py
# A toolbox for helper functions that can be used across the application.

import tkinter as tk

def get_screen_center_position(window_size: tuple[int, int]) -> tuple[int, int]:
    """
    Calculates the screen position needed to center the app window.
    
    Args:
        window_size (tuple): A tuple containing the window's (width, height).

    Returns:
        tuple: A tuple containing the (x, y) coordinates for the top-left corner.
    """
    root = tk.Tk()
    root.withdraw()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    
    x = (screen_width / 2) - (window_size[0] / 2)
    y = (screen_height / 2) - (window_size[1] / 2)
    return int(x), int(y)
