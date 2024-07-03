import tkinter as tk
from tkinter import ttk
from analytics import open_analytics_menu
from expenses import open_expenses_window
from clients import open_add_client_window
from ingredients import open_add_ingredient_window
from recipes import open_add_recipe_window
from purchases import open_add_purchase_window
from ui_config import configure_styles, load_icon, BACKGROUND_COLOR

def main():
    root = tk.Tk()
    root.title("Recipe Manager")
    root.geometry("500x350")
    root.minsize(500, 350)
    root.configure(bg=BACKGROUND_COLOR)

    # Apply styles
    configure_styles()

    # Create the main frame
    main_frame = ttk.Frame(root, padding="20 20 20 20", style="Main.TFrame")
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Create buttons frame
    button_frame = ttk.Frame(main_frame, style="Main.TFrame")
    button_frame.pack(fill=tk.BOTH, expand=True)

    # Add buttons
    add_ingredient_icon = load_icon("icons/add_ingredient.png")
    ingredient_button = ttk.Button(button_frame, text="Adicionar Ingrediente", image=add_ingredient_icon, compound=tk.LEFT, command=lambda: open_add_ingredient_window(root, None))
    ingredient_button.pack(side=tk.TOP, fill=tk.X, pady=5)

    add_recipe_icon = load_icon("icons/add_recipe.png")
    recipe_button = ttk.Button(button_frame, text="Adicionar Receita", image=add_recipe_icon, compound=tk.LEFT, command=lambda: open_add_recipe_window(root))
    recipe_button.pack(side=tk.TOP, fill=tk.X, pady=5)

    add_client_icon = load_icon("icons/add_client.png")
    client_button = ttk.Button(button_frame, text="Adicionar Cliente", image=add_client_icon, compound=tk.LEFT, command=lambda: open_add_client_window(root))
    client_button.pack(side=tk.TOP, fill=tk.X, pady=5)

    add_purchase_icon = load_icon("icons/add_purchase.png")
    purchase_button = ttk.Button(button_frame, text="Adicionar Compra", image=add_purchase_icon, compound=tk.LEFT, command=lambda: open_add_purchase_window(root, None))
    purchase_button.pack(side=tk.TOP, fill=tk.X, pady=5)

    analytics_button = ttk.Button(button_frame, text="Análises", command=lambda: open_analytics_menu(root))
    analytics_button.pack(side=tk.TOP, fill=tk.X, pady=5)

    expenses_button = ttk.Button(button_frame, text="Despesas", command=lambda: open_expenses_window(root))
    expenses_button.pack(side=tk.TOP, fill=tk.X, pady=5)

    root.mainloop()

if __name__ == "__main__":
    main()
