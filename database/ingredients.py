import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk
from ui import ui_config

DATABASE_PATH = 'food_supplier.db'

def connect_to_db():
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        return conn
    except sqlite3.Error as e:
        messagebox.showerror("Erro de Conexão", f"Erro ao conectar-se ao banco de dados: {e}")
        return None

def add_or_update_ingredient(ingredient_name, price_per_unit, unit, ingredient_listbox, status_label):
    if not ingredient_name or not price_per_unit or not unit:
        messagebox.showwarning("Erro de Entrada", "Todos os campos são obrigatórios")
        return
    try:
        price_per_unit = float(price_per_unit)
    except ValueError:
        messagebox.showwarning("Erro de Entrada", "O preço por unidade deve ser um número")
        return

    conn = connect_to_db()
    cursor = conn.cursor()

    cursor.execute('''
    SELECT ingredient_id FROM Ingredientes WHERE ingredient_name = ?
    ''', (ingredient_name,))
    ingredient = cursor.fetchone()

    if ingredient:
        cursor.execute('''
        UPDATE Ingredientes
        SET price_per_unit = ?, unit = ?, is_active = 1
        WHERE ingredient_id = ?
        ''', (price_per_unit, unit, ingredient[0]))
        messagebox.showinfo("Sucesso", "Ingrediente atualizado com sucesso!")
    else:
        cursor.execute('''
        INSERT INTO Ingredientes (ingredient_name, price_per_unit, unit) VALUES (?, ?, ?)
        ''', (ingredient_name, price_per_unit, unit))
        messagebox.showinfo("Sucesso", "Ingrediente adicionado com sucesso!")

    conn.commit()
    conn.close()
    update_ingredient_list(ingredient_listbox)
    status_label.config(text=f"Ingrediente '{ingredient_name}' adicionado/atualizado com sucesso.")

def update_ingredient_list(listbox):
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Ingredientes WHERE is_active = 1')
    ingredients = cursor.fetchall()
    listbox.delete(0, tk.END)
    for ingredient in ingredients:
        listbox.insert(tk.END, f"{ingredient[0]} - {ingredient[1]} - {ingredient[2]} por {ingredient[3]}")
    conn.close()

def delete_ingredient(ingredient_listbox, status_label):
    selected_item = ingredient_listbox.curselection()
    if not selected_item:
        messagebox.showwarning("Erro de Seleção", "Nenhum ingrediente selecionado")
        return
    ingredient_id = int(ingredient_listbox.get(selected_item[0]).split(' ')[0])
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute('UPDATE Ingredientes SET is_active = 0 WHERE ingredient_id = ?', (ingredient_id,))
    conn.commit()
    conn.close()
    messagebox.showinfo("Sucesso", "Ingrediente desativado com sucesso!")
    update_ingredient_list(ingredient_listbox)
    status_label.config(text=f"Ingrediente ID '{ingredient_id}' desativado com sucesso.")

def open_add_ingredient_window(root, status_label):
    ui_config.apply_styles(root)  # Apply styles

    add_ingredient_window = tk.Toplevel(root)
    add_ingredient_window.title("Adicionar Ingrediente")
    add_ingredient_window.geometry("500x400")
    add_ingredient_window.minsize(500, 400)
    add_ingredient_window.configure(bg=ui_config.bg_color)  # Set background color

    # Create the main frame
    main_frame = ttk.Frame(add_ingredient_window, padding="20 20 20 20", style="Main.TFrame")
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Header
    header_label = ttk.Label(main_frame, text="Adicionar Novo Ingrediente", style="Header.TLabel")
    header_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

    # Form labels and entries
    form_frame = ttk.Frame(main_frame, style="Main.TFrame")
    form_frame.grid(row=1, column=0, columnspan=2, pady=10, sticky="ew")

    ttk.Label(form_frame, text="Nome do Ingrediente:", style="Main.TLabel").grid(row=0, column=0, sticky="e", padx=(0, 10))
    ingredient_name_entry = ttk.Entry(form_frame, style="Main.TEntry")
    ingredient_name_entry.grid(row=0, column=1, sticky="ew")

    ttk.Label(form_frame, text="Preço por Unidade:", style="Main.TLabel").grid(row=1, column=0, sticky="e", padx=(0, 10), pady=(10, 0))
    price_per_unit_entry = ttk.Entry(form_frame, style="Main.TEntry")
    price_per_unit_entry.grid(row=1, column=1, sticky="ew")

    ttk.Label(form_frame, text="Unidade:", style="Main.TLabel").grid(row=2, column=0, sticky="e", padx=(0, 10), pady=(10, 0))
    unit_entry = ttk.Entry(form_frame, style="Main.TEntry")
    unit_entry.grid(row=2, column=1, sticky="ew")

    form_frame.grid_columnconfigure(1, weight=1)

    # Buttons with icons
    button_frame = ttk.Frame(main_frame, style="Main.TFrame")
    button_frame.grid(row=2, column=0, columnspan=2, pady=20, sticky="ew")

    add_update_button = ttk.Button(button_frame, text="Adicionar/Atualizar Ingrediente",
                                   command=lambda: add_or_update_ingredient(
                                       ingredient_name_entry.get(),
                                       price_per_unit_entry.get(),
                                       unit_entry.get(),
                                       ingredient_listbox,
                                       status_label
                                   ), style="Main.TButton")
    add_update_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 10))

    delete_button = ttk.Button(button_frame, text="Desativar Ingrediente",
                               command=lambda: delete_ingredient(
                                   ingredient_listbox,
                                   status_label
                               ), style="Main.TButton")
    delete_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 10))

    # Ingredient list
    ingredient_listbox = tk.Listbox(main_frame, width=50, height=10, bg=ui_config.bg_color, fg=ui_config.font_color, font=("Helvetica", 12))
    ingredient_listbox.grid(row=3, column=0, columnspan=2, pady=20, sticky="nsew")

    main_frame.grid_rowconfigure(3, weight=1)
    main_frame.grid_columnconfigure(0, weight=1)

    update_ingredient_list(ingredient_listbox)
    add_ingredient_window.mainloop()

# Ensure "icons/add_update.png" and "icons/delete.png" exist, or replace the paths with the correct ones.
