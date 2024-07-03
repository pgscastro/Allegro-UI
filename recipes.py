import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import os

DATABASE_PATH = 'food_supplier.db'


def connect_to_db():
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        return conn
    except sqlite3.Error as e:
        messagebox.showerror("Erro de Conexão", f"Erro ao conectar-se ao banco de dados: {e}")
        return None


def initialize_database():
    conn = connect_to_db()
    if conn is not None:
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Receitas (
            recipe_id INTEGER PRIMARY KEY,
            recipe_name TEXT NOT NULL,
            total_price REAL NOT NULL,
            selling_price REAL NOT NULL
        )
        ''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Recipe_Ingredients (
            id INTEGER PRIMARY KEY,
            recipe_id INTEGER NOT NULL,
            ingredient_id INTEGER NOT NULL,
            quantity REAL NOT NULL,
            FOREIGN KEY (recipe_id) REFERENCES Receitas(recipe_id),
            FOREIGN KEY (ingredient_id) REFERENCES Ingredientes(ingredient_id)
        )
        ''')
        conn.commit()
        conn.close()


def delete_recipe(recipe_listbox, status_label):
    selected_item = recipe_listbox.curselection()
    if not selected_item:
        messagebox.showwarning("Erro de Seleção", "Nenhuma receita selecionada", parent=status_label.master)
        return
    recipe_id = int(recipe_listbox.get(selected_item[0]).split(' ')[0])
    conn = connect_to_db()
    if conn is not None:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM Receitas WHERE recipe_id = ?', (recipe_id,))
        cursor.execute('DELETE FROM Recipe_Ingredients WHERE recipe_id = ?', (recipe_id,))
        conn.commit()
        conn.close()
        messagebox.showinfo("Sucesso", "Receita excluída com sucesso!", parent=status_label.master)
        update_recipe_list(recipe_listbox)
        status_label.config(text=f"Receita ID '{recipe_id}' excluída com sucesso.")


def update_recipe_list(listbox):
    conn = connect_to_db()
    if conn is not None:
        cursor = conn.cursor()
        cursor.execute('SELECT recipe_id, recipe_name, total_price, selling_price FROM Receitas')
        recipes = cursor.fetchall()
        listbox.delete(0, tk.END)
        for recipe in recipes:
            profit = recipe[3] - recipe[2]  # Calculate profit
            listbox.insert(tk.END, f"{recipe[0]} - {recipe[1]} - Custo: R${recipe[2]:.2f} - Preço de venda: R${recipe[3]:.2f} - Lucro: R${profit:.2f}")
        conn.close()



def display_ingredients(event, listbox, ingredient_listbox):
    selected_item = listbox.curselection()
    if not selected_item:
        return
    recipe_id = int(listbox.get(selected_item[0]).split(' ')[0])
    conn = connect_to_db()
    if conn is not None:
        cursor = conn.cursor()
        cursor.execute('''
        SELECT i.ingredient_name, ri.quantity, i.price_per_unit
        FROM Recipe_Ingredients ri
        JOIN Ingredientes i ON ri.ingredient_id = i.ingredient_id
        WHERE ri.recipe_id = ?
        ''', (recipe_id,))
        ingredients = cursor.fetchall()
        ingredient_listbox.delete(0, tk.END)
        for ingredient in ingredients:
            ingredient_listbox.insert(tk.END,
                                      f"{ingredient[0]} - Quantidade: {ingredient[1]} - Preço por unidade: R${ingredient[2]:.2f}")
        conn.close()


def add_recipe(recipe_name, selling_price, ingredients, status_label, recipe_listbox, recipe_name_entry,
               selling_price_entry, ingredient_frames):
    if not recipe_name or not selling_price or not ingredients:
        status_label.config(text="Todos os campos são obrigatórios", foreground="red")
        return

    try:
        selling_price = float(selling_price.replace(',', '.'))
    except ValueError:
        status_label.config(text="Preço deve ser um número", foreground="red")
        return

    total_price = sum(ingredient['price_per_unit'] * ingredient['quantity'] for ingredient in ingredients.values())

    conn = connect_to_db()
    if conn is not None:
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO Receitas (recipe_name, total_price, selling_price) VALUES (?, ?, ?)
        ''', (recipe_name, total_price, selling_price))
        recipe_id = cursor.lastrowid
        for ingredient_id, ingredient in ingredients.items():
            cursor.execute('''
            INSERT INTO Recipe_Ingredients (recipe_id, ingredient_id, quantity) VALUES (?, ?, ?)
            ''', (recipe_id, ingredient_id, ingredient['quantity']))
        conn.commit()
        conn.close()
        status_label.config(text=f"Receita '{recipe_name}' adicionada com sucesso", foreground="green")
        update_recipe_list(recipe_listbox)
        clear_form(recipe_name_entry, selling_price_entry)
        for frame in ingredient_frames:
            frame.destroy()


def clear_form(*fields):
    for field in fields:
        field.delete(0, tk.END)


def load_icon(icon_path, size=(20, 20)):
    if os.path.exists(icon_path):
        return ImageTk.PhotoImage(Image.open(icon_path).resize(size, Image.Resampling.LANCZOS))
    return None


def get_ingredients():
    conn = connect_to_db()
    if conn is not None:
        cursor = conn.cursor()
        cursor.execute('SELECT ingredient_id, ingredient_name, price_per_unit FROM Ingredientes WHERE is_active = 1')
        ingredients = cursor.fetchall()
        conn.close()
        return ingredients
    return []


def add_ingredient_frame(main_frame, ingredients, ingredient_frames, ingredient_vars, price_vars, quantity_vars,
                         total_cost_var):
    frame = ttk.Frame(main_frame)
    frame.pack(fill=tk.X, pady=5)

    ingredient_var = tk.StringVar()
    ingredient_vars.append(ingredient_var)
    ingredient_dropdown = ttk.Combobox(frame, textvariable=ingredient_var,
                                       values=[f"{i[1]} - R${i[2]:.2f}" for i in ingredients])
    ingredient_dropdown.grid(row=0, column=0, padx=(0, 10), sticky="ew")
    ingredient_dropdown.current(0)

    price_var = tk.DoubleVar(value=ingredients[0][2])
    price_vars.append(price_var)
    # Removed the price_label that was causing the issue
    # price_label = ttk.Label(frame, textvariable=price_var)
    # price_label.grid(row=0, column=1, padx=(0, 10), sticky="ew")

    # Quantity label and entry
    ttk.Label(frame, text="Quantidade:").grid(row=0, column=1, sticky="w", padx=(5, 2))
    quantity_var = tk.DoubleVar(value=1.0)  # Default quantity
    quantity_vars.append(quantity_var)
    quantity_entry = ttk.Entry(frame, textvariable=quantity_var)
    quantity_entry.grid(row=0, column=2, padx=(0, 10), sticky="ew")

    def update_total_cost(*args):
        try:
            total_cost = sum(price.get() * float(quantity.get()) for price, quantity in zip(price_vars, quantity_vars))
            total_cost_var.set(f"Total: R${total_cost:.2f}")
        except ValueError:
            total_cost_var.set("Total: R$0.00")

    ingredient_var.trace_add("write", update_total_cost)
    quantity_var.trace_add("write", update_total_cost)

    ingredient_frames.append(frame)


def open_add_recipe_window(root):
    initialize_database()

    add_recipe_window = tk.Toplevel(root)
    add_recipe_window.title("Adicionar Receita")
    add_recipe_window.geometry("700x700")
    add_recipe_window.minsize(700, 700)

    # Create the main frame
    main_frame = ttk.Frame(add_recipe_window, padding="20 20 20 20")
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Header
    header_label = ttk.Label(main_frame, text="Adicionar Nova Receita", font=("Helvetica", 18, "bold"))
    header_label.grid(row=0, column=0, columnspan=4, pady=(0, 20))

    # Form labels and entries
    form_frame = ttk.Frame(main_frame)
    form_frame.grid(row=1, column=0, columnspan=4, pady=10, sticky="ew")

    ttk.Label(form_frame, text="Nome da Receita:").grid(row=0, column=0, sticky="e", padx=(0, 10))
    recipe_name_entry = ttk.Entry(form_frame)
    recipe_name_entry.grid(row=0, column=1, columnspan=3, sticky="ew")

    ttk.Label(form_frame, text="Preço de Venda (R$):").grid(row=1, column=0, sticky="e", padx=(0, 10), pady=(10, 0))
    selling_price_entry = ttk.Entry(form_frame)
    selling_price_entry.insert(0, "0,00")
    selling_price_entry.grid(row=1, column=1, columnspan=3, sticky="ew")

    # Ingredients section
    ingredient_label = ttk.Label(form_frame, text="Ingredientes:", font=("Helvetica", 12))
    ingredient_label.grid(row=2, column=0, sticky="e", padx=(0, 10), pady=(10, 0))

    ingredient_frame_container = ttk.Frame(form_frame)
    ingredient_frame_container.grid(row=2, column=1, columnspan=3, sticky="ew")

    ingredient_frames = []
    ingredient_vars = []
    price_vars = []
    quantity_vars = []
    total_cost_var = tk.StringVar(value="Total: R$0.00")
    full_price_var = tk.StringVar(value="Preço Total: R$0.00")
    profit_var = tk.StringVar(value="Lucro: R$0.00")

    ingredients = get_ingredients()
    if not ingredients:
        messagebox.showerror("Erro", "Nenhum ingrediente encontrado.", parent=add_recipe_window)
        add_recipe_window.destroy()
        return

    add_ingredient_frame(ingredient_frame_container, ingredients, ingredient_frames, ingredient_vars, price_vars, quantity_vars, total_cost_var)

    add_ingredient_button = ttk.Button(form_frame, text="Adicionar Ingrediente", command=lambda: add_ingredient_frame(ingredient_frame_container, ingredients, ingredient_frames, ingredient_vars, price_vars, quantity_vars, total_cost_var))
    add_ingredient_button.grid(row=3, column=3, pady=(10, 20), sticky="e")

    total_cost_label = ttk.Label(form_frame, textvariable=total_cost_var, font=("Helvetica", 12, "bold"))
    total_cost_label.grid(row=4, column=0, columnspan=4, pady=(0, 20))

    # Full price and profit labels
    full_price_label = ttk.Label(form_frame, textvariable=full_price_var, font=("Helvetica", 12, "bold"))
    full_price_label.grid(row=5, column=0, columnspan=4, pady=(0, 20))

    profit_label = ttk.Label(form_frame, textvariable=profit_var, font=("Helvetica", 12, "bold"))
    profit_label.grid(row=6, column=0, columnspan=4, pady=(0, 20))

    form_frame.grid_columnconfigure(1, weight=1)

    # Status label for messages in this window
    status_label = ttk.Label(form_frame, text="", font=("Helvetica", 10))
    status_label.grid(row=7, column=0, columnspan=4, pady=(10, 0), sticky="ew")

    # Load icons
    add_update_icon = load_icon("icons/add_update.png")
    delete_icon = load_icon("icons/delete.png")

    # Buttons with icons
    button_frame = ttk.Frame(main_frame)
    button_frame.grid(row=8, column=0, columnspan=4, pady=20, sticky="ew")

    add_recipe_button = ttk.Button(button_frame, text="Adicionar Receita", image=add_update_icon, compound=tk.LEFT,
                                   command=lambda: add_recipe(
                                       recipe_name_entry.get(),
                                       selling_price_entry.get(),
                                       {ingredients[i][0]: {'price_per_unit': price.get(), 'quantity': quantity.get()} for i, (price, quantity) in enumerate(zip(price_vars, quantity_vars))},
                                       status_label,
                                       recipe_listbox,
                                       recipe_name_entry,
                                       selling_price_entry,
                                       ingredient_frames
                                   ))
    add_recipe_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 10))

    delete_recipe_button = ttk.Button(button_frame, text="Excluir Receita", image=delete_icon, compound=tk.LEFT,
                                      command=lambda: delete_recipe(recipe_listbox, status_label))
    delete_recipe_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 10))

    # Recipe list
    list_frame = ttk.Frame(main_frame)
    list_frame.grid(row=9, column=0, columnspan=4, pady=20, sticky="nsew")

    recipe_listbox = tk.Listbox(list_frame, width=50, height=10)
    recipe_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    recipe_listbox.bind('<<ListboxSelect>>', lambda event: display_ingredients(event, recipe_listbox, ingredient_listbox))

    scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=recipe_listbox.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    recipe_listbox.config(yscrollcommand=scrollbar.set)

    # Ingredient list display for selected recipe
    ingredient_listbox = tk.Listbox(main_frame, width=50, height=10)
    ingredient_listbox.grid(row=10, column=0, columnspan=4, pady=10, sticky="nsew")

    main_frame.grid_rowconfigure(9, weight=1)
    main_frame.grid_rowconfigure(10, weight=1)
    main_frame.grid_columnconfigure(0, weight=1)

    update_recipe_list(recipe_listbox)

    add_recipe_window.mainloop()
