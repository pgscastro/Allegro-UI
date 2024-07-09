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
            selling_price REAL NOT NULL,
            mao_de_obra REAL DEFAULT 0,
            gas_agua_luz REAL DEFAULT 0,
            porcoes INTEGER DEFAULT 1
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
        # Check if columns exist, and add them if not
        cursor.execute("PRAGMA table_info(Receitas)")
        columns = [column[1] for column in cursor.fetchall()]
        if "mao_de_obra" not in columns:
            cursor.execute("ALTER TABLE Receitas ADD COLUMN mao_de_obra REAL DEFAULT 0")
        if "gas_agua_luz" not in columns:
            cursor.execute("ALTER TABLE Receitas ADD COLUMN gas_agua_luz REAL DEFAULT 0")
        if "porcoes" not in columns:
            cursor.execute("ALTER TABLE Receitas ADD COLUMN porcoes INTEGER DEFAULT 1")
        conn.commit()
        conn.close()


def delete_recipe(recipe_listbox, status_label):
    selected_item = recipe_listbox.selection()
    if not selected_item:
        messagebox.showwarning("Erro de Seleção", "Nenhuma receita selecionada", parent=status_label.master)
        return
    recipe_id = int(recipe_listbox.item(selected_item[0], 'values')[0])
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


def update_recipe_list(treeview):
    conn = connect_to_db()
    if conn is not None:
        cursor = conn.cursor()
        cursor.execute('SELECT recipe_id, recipe_name, total_price, selling_price, mao_de_obra, gas_agua_luz, porcoes FROM Receitas')
        recipes = cursor.fetchall()
        for row in treeview.get_children():
            treeview.delete(row)
        for recipe in recipes:
            gastos = recipe[2] + (recipe[4] / 100 * recipe[2]) + (recipe[5] / 100 * recipe[2])
            total_price = recipe[3] * recipe[6]
            profit = total_price - gastos
            treeview.insert('', tk.END, values=(recipe[0], recipe[1], gastos, total_price, recipe[4], recipe[5], profit))
        conn.close()


def add_recipe(recipe_name, selling_price, mao_de_obra, gas_agua_luz, porcoes, ingredients, status_label, treeview, recipe_name_entry,
               selling_price_entry, mao_de_obra_entry, gas_agua_luz_entry, porcoes_entry, ingredient_frames):
    if not recipe_name or not selling_price or not mao_de_obra or not gas_agua_luz or not porcoes or not ingredients:
        status_label.config(text="Todos os campos são obrigatórios", foreground="red")
        return

    try:
        selling_price = float(selling_price.replace(',', '.'))
        mao_de_obra = float(mao_de_obra)
        gas_agua_luz = float(gas_agua_luz)
        porcoes = int(porcoes)
    except ValueError:
        status_label.config(text="Preços e porcentagens devem ser números", foreground="red")
        return

    total_price = sum(ingredient['price_per_unit'] * ingredient['quantity'] for ingredient in ingredients.values())
    gastos = total_price + (mao_de_obra / 100 * total_price) + (gas_agua_luz / 100 * total_price)

    conn = connect_to_db()
    if conn is not None:
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO Receitas (recipe_name, total_price, selling_price, mao_de_obra, gas_agua_luz, porcoes) VALUES (?, ?, ?, ?, ?, ?)
        ''', (recipe_name, total_price, selling_price, mao_de_obra, gas_agua_luz, porcoes))
        recipe_id = cursor.lastrowid
        for ingredient_id, ingredient in ingredients.items():
            cursor.execute('''
            INSERT INTO Recipe_Ingredients (recipe_id, ingredient_id, quantity) VALUES (?, ?, ?)
            ''', (recipe_id, ingredient_id, ingredient['quantity']))
        conn.commit()
        conn.close()
        status_label.config(text=f"Receita '{recipe_name}' adicionada com sucesso", foreground="green")
        update_recipe_list(treeview)
        clear_form(recipe_name_entry, selling_price_entry, mao_de_obra_entry, gas_agua_luz_entry, porcoes_entry)
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


def safe_float_conversion(value):
    if value in [None, '']:
        return 0.0
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0


def add_ingredient_frame(main_frame, ingredients, ingredient_frames, ingredient_vars, price_vars, quantity_vars, total_cost_var, full_price_var, profit_var, selling_price_entry, porcoes_entry, mao_de_obra_entry, gas_agua_luz_entry):
    frame = ttk.Frame(main_frame)
    frame.pack(fill=tk.X, pady=5)

    ingredient_var = tk.StringVar()
    ingredient_vars.append(ingredient_var)
    ingredient_dropdown = ttk.Combobox(frame, textvariable=ingredient_var, values=[f"{i[1]} - R${i[2]:.2f}" for i in ingredients])
    ingredient_dropdown.grid(row=0, column=0, padx=(0, 10), sticky="ew")
    ingredient_dropdown.current(0)

    price_var = tk.DoubleVar(value=ingredients[0][2])
    price_vars.append(price_var)

    ttk.Label(frame, text="Quantidade:").grid(row=0, column=1, sticky="w", padx=(5, 2))
    quantity_var = tk.StringVar(value="1.0")  # Default quantity
    quantity_vars.append(quantity_var)
    quantity_entry = ttk.Entry(frame, textvariable=quantity_var)
    quantity_entry.grid(row=0, column=2, padx=(0, 10), sticky="ew")

    def update_total_cost(*args):
        total_cost = sum(safe_float_conversion(price.get()) * safe_float_conversion(quantity.get()) for price, quantity in zip(price_vars, quantity_vars))
        total_cost_var.set(f"Gastos: R${total_cost:.2f}")

        try:
            selling_price = float(selling_price_entry.get().replace(',', '.'))
            porcoes = int(porcoes_entry.get())
            mao_de_obra = float(mao_de_obra_entry.get().replace(',', '.'))
            gas_agua_luz = float(gas_agua_luz_entry.get().replace(',', '.'))

            total_price = selling_price * porcoes
            full_price_var.set(f"Preço Total: R${total_price:.2f}")

            gastos = total_cost + (mao_de_obra / 100 * total_cost) + (gas_agua_luz / 100 * total_cost)
            lucro = total_price - gastos
            profit_var.set(f"Lucro: R${lucro:.2f}")
        except ValueError:
            full_price_var.set("Preço Total: R$0.00")
            profit_var.set("Lucro: R$0.00")

    ingredient_var.trace_add("write", update_total_cost)
    quantity_var.trace_add("write", update_total_cost)
    selling_price_entry.bind("<KeyRelease>", update_total_cost)
    porcoes_entry.bind("<KeyRelease>", update_total_cost)
    mao_de_obra_entry.bind("<KeyRelease>", update_total_cost)
    gas_agua_luz_entry.bind("<KeyRelease>", update_total_cost)

    ingredient_frames.append(frame)

    # Trigger the update function initially
    update_total_cost()


def open_add_recipe_window(root):
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

    ttk.Label(form_frame, text="Mão de Obra (%):").grid(row=2, column=0, sticky="e", padx=(0, 10), pady=(10, 0))
    mao_de_obra_entry = ttk.Entry(form_frame)
    mao_de_obra_entry.insert(0, "0")
    mao_de_obra_entry.grid(row=2, column=1, columnspan=3, sticky="ew")

    ttk.Label(form_frame, text="Gás/Água/Luz (%):").grid(row=3, column=0, sticky="e", padx=(0, 10), pady=(10, 0))
    gas_agua_luz_entry = ttk.Entry(form_frame)
    gas_agua_luz_entry.insert(0, "0")
    gas_agua_luz_entry.grid(row=3, column=1, columnspan=3, sticky="ew")

    ttk.Label(form_frame, text="Porções:").grid(row=4, column=0, sticky="e", padx=(0, 10), pady=(10, 0))
    porcoes_entry = ttk.Entry(form_frame)
    porcoes_entry.insert(0, "1")
    porcoes_entry.grid(row=4, column=1, columnspan=3, sticky="ew")

    # Ingredients section
    ingredient_label = ttk.Label(form_frame, text="Ingredientes:", font=("Helvetica", 12))
    ingredient_label.grid(row=5, column=0, sticky="e", padx=(0, 10), pady=(10, 0))

    ingredient_frame_container = ttk.Frame(form_frame)
    ingredient_frame_container.grid(row=5, column=1, columnspan=3, sticky="ew")

    ingredient_frames = []
    ingredient_vars = []
    price_vars = []
    quantity_vars = []
    total_cost_var = tk.StringVar(value="Gastos: R$0.00")
    full_price_var = tk.StringVar(value="Preço Total: R$0.00")
    profit_var = tk.StringVar(value="Lucro: R$0.00")

    ingredients = get_ingredients()
    if not ingredients:
        messagebox.showerror("Erro", "Nenhum ingrediente encontrado.", parent=add_recipe_window)
        add_recipe_window.destroy()
        return

    add_ingredient_frame(ingredient_frame_container, ingredients, ingredient_frames, ingredient_vars, price_vars, quantity_vars, total_cost_var, full_price_var, profit_var, selling_price_entry, porcoes_entry, mao_de_obra_entry, gas_agua_luz_entry)

    add_ingredient_button = ttk.Button(form_frame, text="Adicionar Ingrediente", command=lambda: add_ingredient_frame(ingredient_frame_container, ingredients, ingredient_frames, ingredient_vars, price_vars, quantity_vars, total_cost_var, full_price_var, profit_var, selling_price_entry, porcoes_entry, mao_de_obra_entry, gas_agua_luz_entry))
    add_ingredient_button.grid(row=6, column=3, pady=(10, 20), sticky="e")

    total_cost_label = ttk.Label(form_frame, textvariable=total_cost_var, font=("Helvetica", 12, "bold"))
    total_cost_label.grid(row=7, column=0, columnspan=4, pady=(0, 20))

    # Full price and profit labels
    full_price_label = ttk.Label(form_frame, textvariable=full_price_var, font=("Helvetica", 12, "bold"))
    full_price_label.grid(row=8, column=0, columnspan=4, pady=(0, 20))

    profit_label = ttk.Label(form_frame, textvariable=profit_var, font=("Helvetica", 12, "bold"))
    profit_label.grid(row=9, column=0, columnspan=4, pady=(0, 20))

    form_frame.grid_columnconfigure(1, weight=1)

    # Status label for messages in this window
    status_label = ttk.Label(form_frame, text="", font=("Helvetica", 10))
    status_label.grid(row=10, column=0, columnspan=4, pady=(10, 0), sticky="ew")

    # Load icons
    add_update_icon = load_icon("icons/add_update.png")
    delete_icon = load_icon("icons/delete.png")

    # Buttons with icons
    button_frame = ttk.Frame(main_frame)
    button_frame.grid(row=11, column=0, columnspan=4, pady=20, sticky="ew")

    add_recipe_button = ttk.Button(button_frame, text="Adicionar Receita", image=add_update_icon, compound=tk.LEFT,
                                   command=lambda: add_recipe(
                                       recipe_name_entry.get(),
                                       selling_price_entry.get(),
                                       mao_de_obra_entry.get(),
                                       gas_agua_luz_entry.get(),
                                       porcoes_entry.get(),
                                       {ingredients[i][0]: {'price_per_unit': price.get(), 'quantity': safe_float_conversion(quantity.get())} for i, (price, quantity) in enumerate(zip(price_vars, quantity_vars))},
                                       status_label,
                                       recipe_listbox,
                                       recipe_name_entry,
                                       selling_price_entry,
                                       mao_de_obra_entry,
                                       gas_agua_luz_entry,
                                       porcoes_entry,
                                       ingredient_frames
                                   ))
    add_recipe_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 10))

    delete_recipe_button = ttk.Button(button_frame, text="Excluir Receita", image=delete_icon, compound=tk.LEFT,
                                      command=lambda: delete_recipe(recipe_listbox, status_label))
    delete_recipe_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 10))

    # Recipe list with Treeview
    list_frame = ttk.Frame(main_frame)
    list_frame.grid(row=12, column=0, columnspan=4, pady=20, sticky="nsew")

    columns = ('ID', 'Nome', 'Gastos', 'Preço Total', 'Mão de Obra (%)', 'Gás/Água/Luz (%)', 'Lucro')
    recipe_listbox = ttk.Treeview(list_frame, columns=columns, show='headings')
    for col in columns:
        recipe_listbox.heading(col, text=col)
    recipe_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=recipe_listbox.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    recipe_listbox.config(yscrollcommand=scrollbar.set)

    main_frame.grid_rowconfigure(12, weight=1)
    main_frame.grid_columnconfigure(0, weight=1)

    update_recipe_list(recipe_listbox)

    add_recipe_window.mainloop()


def main():
    root = tk.Tk()
    root.title("Gerenciador de Receitas")
    root.geometry("800x600")
    root.minsize(800, 600)

    main_frame = ttk.Frame(root, padding="20 20 20 20")
    main_frame.pack(fill=tk.BOTH, expand=True)

    header_label = ttk.Label(main_frame, text="Gerenciador de Receitas", font=("Helvetica", 18, "bold"))
    header_label.pack(pady=(0, 20))

    recipe_button = ttk.Button(main_frame, text="Adicionar Receita", command=lambda: open_add_recipe_window(root))
    recipe_button.pack(pady=(0, 20))

    initialize_database()

    root.mainloop()


if __name__ == "__main__":
    main()
