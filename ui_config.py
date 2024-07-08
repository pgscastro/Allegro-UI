import os
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

# Define the color palette based on the provided logo
bg_color = "#fff0db"  # White background
button_bg_color = "#81B29A"  # Light green button background
button_fg_color = "#000000"  # White text for buttons
font_color = "#000000"  # Black text
header_color = "#F4A261"  # Orange header color
header_font = ("Helvetica", 18, "bold")
label_font = ("Helvetica", 12)
entry_font = ("Helvetica", 12)


def apply_styles(root):
    style = ttk.Style(root)
    style.configure("TFrame", background=bg_color)
    style.configure("TLabel", background=bg_color, font=label_font)
    style.configure("TEntry", font=entry_font)
    style.configure("TButton", background=button_bg_color, foreground=button_fg_color, font=label_font)
    style.configure("Header.TLabel", font=header_font, background=bg_color)
    style.configure("Status.TLabel", font=("Helvetica", 10), background=bg_color)

    root.configure(background=bg_color)


def apply_color_palette(widget, widget_type):
    """
    Applies a color palette to a given tkinter widget based on its type.

    Parameters:
    widget (tkinter.Widget): The widget to which the color palette should be applied.
    widget_type (str): The type of the widget (e.g., "button", "label", "entry", "header").
    """
    # Define color variables (these should be defined somewhere in your code)
    button_bg_color = "#ffffff"  # Example color for button background
    button_fg_color = "#000000"  # Example color for button foreground
    bg_color = "#f0f0f0"  # Example color for background
    font_color = "#333333"  # Example color for font

    try:
        if widget_type == "button":
            # Configuring a Button widget
            if hasattr(widget, 'config'):
                widget.config(bg=button_bg_color, fg=button_fg_color, font=("Helvetica", 12))
        elif widget_type == "label":
            # Configuring a Label widget
            if hasattr(widget, 'config'):
                widget.config(bg=bg_color, fg=font_color, font=("Helvetica", 12))
        elif widget_type == "entry":
            # Configuring an Entry widget
            if hasattr(widget, 'config'):
                widget.config(bg=bg_color, fg=font_color, font=("Helvetica", 12), insertbackground=font_color)
        elif widget_type == "header":
            # Assuming header is a Label widget for custom styling
            if hasattr(widget, 'config'):
                widget.config(background=bg_color, font=("Helvetica", 18, "bold"))
        else:
            if hasattr(widget, 'config'):
                # Default configuration for any other widget type
                widget.config(background=bg_color)
    except tk.TclError as e:
        print(f"Error configuring widget: {e}")


# Example usage
# import tkinter as tk
# root = tk.Tk()
# header_label = tk.Label(root, text="Header")
# apply_color_palette(header_label, "header")
# header_label.pack()
# root.mainloop()


def set_global_styles(root):
    apply_styles(root)


def load_icon(icon_path, size=(20, 20)):
    if os.path.exists(icon_path):
        return ImageTk.PhotoImage(Image.open(icon_path).resize(size, Image.LANCZOS))
    return None