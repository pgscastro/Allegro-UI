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
    if widget_type == "button":
        widget.config(bg=button_bg_color, fg=button_fg_color, font=("Helvetica", 12))
    elif widget_type == "label":
        widget.config(bg=bg_color, fg=font_color, font=("Helvetica", 12))
    elif widget_type == "entry":
        widget.config(bg=bg_color, fg=font_color, font=("Helvetica", 12), insertbackground=font_color)
    elif widget_type == "header":
        widget.config(bg=bg_color, fg=header_color, font=("Helvetica", 18, "bold"))
    else:
        widget.config(bg=bg_color, fg=font_color)


def set_global_styles(root):
    apply_styles(root)


def load_icon(icon_path, size=(20, 20)):
    if os.path.exists(icon_path):
        return ImageTk.PhotoImage(Image.open(icon_path).resize(size, Image.LANCZOS))
    return None