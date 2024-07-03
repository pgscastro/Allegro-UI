from tkinter import ttk

# Define the original color palette
BACKGROUND_COLOR = "#FFFFFF"  # Dark background
TEXT_COLOR = "#000000"  # White text
BUTTON_BACKGROUND_COLOR = "#F7C646"  # Warm Yellow for buttons
BUTTON_TEXT_COLOR = "#1C1C1C"  # Dark text for buttons
STATUS_BACKGROUND_COLOR = "#1C1C1C"  # Same as background
STATUS_TEXT_COLOR = "#FFFFFF"  # White status text


def configure_styles():
    style = ttk.Style()
    style.theme_use("default")

    # Main frame style
    style.configure("Main.TFrame", background=BACKGROUND_COLOR)

    # Button style
    style.configure("TButton", padding=6, relief="flat", background=BUTTON_BACKGROUND_COLOR, foreground=BUTTON_TEXT_COLOR, font=("Helvetica", 12))
    style.map("TButton", background=[('active', BUTTON_BACKGROUND_COLOR)])

    # Label style
    style.configure("TLabel", background=BACKGROUND_COLOR, foreground=TEXT_COLOR, font=("Helvetica", 12))

    # Status label style
    style.configure("Status.TLabel", background=STATUS_BACKGROUND_COLOR, foreground=STATUS_TEXT_COLOR, font=("Helvetica", 10))

def load_icon(icon_path, size=(20, 20)):
    from PIL import Image, ImageTk
    import os
    if os.path.exists(icon_path):
        try:
            return ImageTk.PhotoImage(Image.open(icon_path).resize(size, Image.LANCZOS))
        except Exception as e:
            print(f"Error loading image {icon_path}: {e}")
    return None
