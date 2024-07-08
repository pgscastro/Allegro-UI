import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk
from tkinter import TclError
from PIL import Image, ImageTk
import os
import re
from datetime import datetime  # Import datetime module

DATABASE_PATH = 'database/food_supplier.db'


def connect_to_db():
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        return conn
    except sqlite3.Error as e:
        log_error(f"Erro ao conectar-se ao banco de dados: {e}")
        messagebox.showerror("Erro de Conexão", f"Erro ao conectar-se ao banco de dados: {e}")
        return None


def initialize_database():
    with connect_to_db() as conn:
        if conn is not None:
            cursor = conn.cursor()
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS Compras (
                purchase_id INTEGER PRIMARY KEY,
                client_id INTEGER NOT NULL,
                purchase_date TEXT NOT NULL,
                total_amount REAL NOT NULL,
                FOREIGN KEY (client_id) REFERENCES Clientes(client_id)
            )
            ''')
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS Purchase_Items (
                id INTEGER PRIMARY KEY,
                purchase_id INTEGER NOT NULL,
                recipe_id INTEGER NOT NULL,
                quantity REAL NOT NULL,
                FOREIGN KEY (purchase_id) REFERENCES Compras(purchase_id),
                FOREIGN KEY (recipe_id) REFERENCES Receitas(recipe_id)
            )
            ''')
            conn.commit()


def load_icon(icon_path, size=(20, 20)):
    if os.path.exists(icon_path):
        return ImageTk.PhotoImage(Image.open(icon_path).resize(size, Image.LANCZOS))
    return None


def get_clients():
    with connect_to_db() as conn:
        if conn is not None:
            cursor = conn.cursor()
            cursor.execute('SELECT client_id, client_name FROM Clientes')
            clients = cursor.fetchall()
            return clients
    return []


def get_recipes():
    with connect_to_db() as conn:
        if conn is not None:
            cursor = conn.cursor()
            cursor.execute('SELECT recipe_id, recipe_name, selling_price FROM Receitas')
            recipes = cursor.fetchall()
            return recipes
    return []


def add_purchase(client_id, purchase_date, total_amount, items, status_label, purchase_listbox, client_dropdown,
                 date_entry, item_frames, item_vars, quantity_vars, total_amount_var, item_frame_container,
                 discount_var, discount_percentage_var, discount_check_var, recipes):
    if not client_id or not purchase_date or not items:
        status_label.config(text="Todos os campos são obrigatórios", foreground="red")
        return

    try:
        total_amount = float(total_amount.replace(',', '.'))
    except ValueError:
        status_label.config(text="Total deve ser um número", foreground="red")
        return

    if not validate_date(purchase_date):
        status_label.config(text="Data inválida. Use DD/MM/AAAA.", foreground="red")
        return

    try:
        formatted_purchase_date = datetime.strptime(purchase_date, "%d/%m/%Y").strftime("%Y-%m-%d")
        with connect_to_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
            INSERT INTO Compras (client_id, purchase_date, total_amount) VALUES (?, ?, ?)
            ''', (client_id, formatted_purchase_date, total_amount))
            purchase_id = cursor.lastrowid
            for item in items:
                cursor.execute('''
                INSERT INTO Purchase_Items (purchase_id, recipe_id, quantity) VALUES (?, ?, ?)
                ''', (purchase_id, item['recipe_id'], item['quantity']))
            conn.commit()
            status_label.config(text=f"Compra adicionada com sucesso", foreground="green")
            update_purchase_list(purchase_listbox)
            clear_form(client_dropdown, date_entry, total_amount_var, item_frame_container, item_frames, item_vars,
                       quantity_vars, discount_var, discount_percentage_var, discount_check_var, recipes)
    except sqlite3.Error as e:
        log_error(f"Erro ao adicionar compra: {e}")
        messagebox.showerror("Erro", f"Erro ao adicionar compra: {e}")


def clear_form(client_dropdown, date_entry, total_amount_var, item_frame_container, item_frames, item_vars,
               quantity_vars, discount_var, discount_percentage_var, discount_check_var, recipes):
    client_dropdown.set('')
    date_entry.delete(0, tk.END)
    date_entry.insert(0, datetime.now().strftime("%d/%m/%Y"))
    total_amount_var.set("Total: R$0.00")
    discount_var.set("0,00")
    discount_percentage_var.set("0,00")
    discount_check_var.set(False)

    for frame in item_frames:
        frame.destroy()
    item_frames.clear()
    item_vars.clear()
    quantity_vars.clear()

    add_item_frame(item_frame_container, recipes, item_frames, item_vars, quantity_vars, total_amount_var, discount_var,
                   discount_percentage_var, discount_check_var)


def update_purchase_list(listbox):
    try:
        with connect_to_db() as conn:
            if conn is not None:
                cursor = conn.cursor()
                cursor.execute('''
                SELECT c.purchase_id, cl.client_name, c.purchase_date, c.total_amount
                FROM Compras c
                JOIN Clientes cl ON c.client_id = cl.client_id
                ''')
                purchases = cursor.fetchall()
                listbox.delete(0, tk.END)
                for purchase in purchases:
                    listbox.insert(tk.END,
                                   f"{purchase[0]} - Cliente: {purchase[1]} - Data: {purchase[2]} - Total: R${purchase[3]:.2f}")
    except sqlite3.Error as e:
        log_error(f"Erro ao atualizar lista de compras: {e}")
        messagebox.showerror("Erro", f"Erro ao atualizar lista de compras: {e}")


def add_item_frame(main_frame, recipes, item_frames, item_vars, quantity_vars, total_amount_var, discount_var,
                   discount_percentage_var, discount_check_var):
    frame = ttk.Frame(main_frame)
    frame.pack(fill=tk.X, pady=5)

    item_var = tk.StringVar()
    item_vars.append(item_var)
    item_dropdown = ttk.Combobox(frame, textvariable=item_var, values=[f"{i[1]} - R${i[2]:.2f}" for i in recipes])
    item_dropdown.grid(row=0, column=0, padx=(0, 10), sticky="ew")
    item_dropdown.current(0)

    # Quantity label and entry
    ttk.Label(frame, text="Quantidade:").grid(row=0, column=1, sticky="w", padx=(5, 2))
    quantity_var = tk.DoubleVar(value=1.0)  # Default quantity
    quantity_vars.append(quantity_var)
    quantity_entry = ttk.Entry(frame, textvariable=quantity_var)
    quantity_entry.grid(row=0, column=2, padx=(0, 10), sticky="ew")

    # **Highlight: Add callbacks to update total amount when item or quantity changes**
    def on_item_change(*args):
        update_total_amount(item_vars, quantity_vars, total_amount_var, discount_var, discount_percentage_var,
                            discount_check_var, recipes)

    item_var.trace_add("write", on_item_change)
    quantity_var.trace_add("write", on_item_change)

    item_frames.append(frame)


def update_total_amount(item_vars, quantity_vars, total_amount_var, discount_var, discount_percentage_var,
                        discount_check_var, recipes):
    try:
        total_amount = 0
        for item_var, quantity_var in zip(item_vars, quantity_vars):
            item_name_price = item_var.get()
            quantity = float(quantity_var.get() or 0)
            price = next((r[2] for r in recipes if f"{r[1]} - R${r[2]:.2f}" == item_name_price), 0)
            total_amount += price * quantity
        if discount_check_var.get():
            discount = float(discount_var.get().replace(',', '.')) if discount_var.get() else 0
            discount_percentage = float(
                discount_percentage_var.get().replace(',', '.')) if discount_percentage_var.get() else 0
            total_amount -= discount
            total_amount -= (total_amount * (discount_percentage / 100))
        total_amount_var.set(f"Total: R${total_amount:.2f}")
    except (ValueError, TclError):
        total_amount_var.set("Total: R$0.00")


def apply_discount(item_vars, quantity_vars, total_amount_var, discount_var, discount_percentage_var,
                   discount_check_var, recipes):
    update_total_amount(item_vars, quantity_vars, total_amount_var, discount_var, discount_percentage_var,
                        discount_check_var, recipes)


def log_error(message):
    with open('error.log', 'a') as f:
        f.write(message + '\n')


def validate_date(date_text):
    try:
        if re.match(r'^\d{2}/\d{2}/\d{4}$', date_text):
            day, month, year = map(int, date_text.split('/'))
            return 1 <= day <= 31 and 1 <= month <= 12 and year > 0
        return False
    except ValueError:
        return False


def format_date(event):
    content = event.widget.get()
    if len(content) == 2 or len(content) == 5:
        event.widget.insert(tk.END, '/')
    elif len(content) > 10:
        event.widget.delete(10, tk.END)


def open_add_purchase_window(root, status_label):
    initialize_database()

    add_purchase_window = tk.Toplevel(root)
    add_purchase_window.title("Adicionar Compra")
    add_purchase_window.geometry("700x700")
    add_purchase_window.minsize(700, 700)

    # Create the main frame
    main_frame = ttk.Frame(add_purchase_window, padding="20 20 20 20")
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Header
    header_label = ttk.Label(main_frame, text="Adicionar Nova Compra", font=("Helvetica", 18, "bold"))
    header_label.grid(row=0, column=0, columnspan=4, pady=(0, 20))

    # Form labels and entries
    form_frame = ttk.Frame(main_frame)
    form_frame.grid(row=1, column=0, columnspan=4, pady=10, sticky="ew")

    clients = get_clients()
    recipes = get_recipes()

    if not recipes:
        messagebox.showerror("Erro", "Nenhuma receita encontrada.", parent=add_purchase_window)
        add_purchase_window.destroy()
        return

    ttk.Label(form_frame, text="Cliente:").grid(row=0, column=0, sticky="e", padx=(0, 10))
    client_var = tk.StringVar()
    client_dropdown = ttk.Combobox(form_frame, textvariable=client_var, values=[f"{c[1]}" for c in clients])
    client_dropdown.grid(row=0, column=1, columnspan=3, sticky="ew")

    ttk.Label(form_frame, text="Data da Compra (DD/MM/AAAA):").grid(row=1, column=0, sticky="e", padx=(0, 10),
                                                                    pady=(10, 0))
    date_var = tk.StringVar(value=datetime.now().strftime("%d/%m/%Y"))  # Set the current date as default value
    date_entry = ttk.Entry(form_frame, textvariable=date_var)
    date_entry.grid(row=1, column=1, columnspan=3, sticky="ew")

    # Corrected formatting and validation callback for the date entry
    date_entry.bind("<KeyRelease>", format_date)

    # Items section
    item_label = ttk.Label(form_frame, text="Itens:", font=("Helvetica", 12))
    item_label.grid(row=2, column=0, sticky="e", padx=(0, 10), pady=(10, 0))

    item_frame_container = ttk.Frame(form_frame)
    item_frame_container.grid(row=2, column=1, columnspan=3, sticky="ew")

    item_frames = []
    item_vars = []
    quantity_vars = []
    total_amount_var = tk.StringVar(value="Total: R$0.00")

    # Discount section
    discount_check_var = tk.BooleanVar()
    discount_checkbutton = ttk.Checkbutton(form_frame, text="Habilitar Descontos", variable=discount_check_var)
    discount_checkbutton.grid(row=3, column=0, columnspan=4, pady=(10, 0), sticky="ew")

    ttk.Label(form_frame, text="Desconto (R$):").grid(row=4, column=0, sticky="e", padx=(0, 10), pady=(10, 0))
    discount_var = tk.StringVar(value="0,00")
    discount_entry = ttk.Entry(form_frame, textvariable=discount_var, state='disabled')
    discount_entry.grid(row=4, column=1, columnspan=3, sticky="ew")

    ttk.Label(form_frame, text="Desconto (%):").grid(row=5, column=0, sticky="e", padx=(0, 10), pady=(10, 0))
    discount_percentage_var = tk.StringVar(value="0,00")
    discount_percentage_entry = ttk.Entry(form_frame, textvariable=discount_percentage_var, state='disabled')
    discount_percentage_entry.grid(row=5, column=1, columnspan=3, sticky="ew")

    apply_discount_button = ttk.Button(form_frame, text="Aplicar Descontos", state='disabled',
                                       command=lambda: apply_discount(item_vars, quantity_vars, total_amount_var,
                                                                      discount_var, discount_percentage_var,
                                                                      discount_check_var, recipes))
    apply_discount_button.grid(row=6, column=0, columnspan=4, pady=(10, 20), sticky="ew")

    def toggle_discount_entries():
        state = 'normal' if discount_check_var.get() else 'disabled'
        discount_entry.config(state=state)
        discount_percentage_entry.config(state=state)
        apply_discount_button.config(state=state)

    discount_check_var.trace_add("write", lambda *args: toggle_discount_entries())

    add_item_frame(item_frame_container, recipes, item_frames, item_vars, quantity_vars, total_amount_var, discount_var,
                   discount_percentage_var, discount_check_var)

    add_item_button = ttk.Button(form_frame, text="Adicionar Item",
                                 command=lambda: add_item_frame(item_frame_container, recipes, item_frames, item_vars,
                                                                quantity_vars, total_amount_var, discount_var,
                                                                discount_percentage_var, discount_check_var))
    add_item_button.grid(row=7, column=3, pady=(10, 20), sticky="e")

    total_amount_label = ttk.Label(form_frame, textvariable=total_amount_var, font=("Helvetica", 12, "bold"))
    total_amount_label.grid(row=8, column=0, columnspan=4, pady=(0, 20))

    form_frame.grid_columnconfigure(1, weight=1)

    # Status label for messages in this window
    status_label = ttk.Label(form_frame, text="", font=("Helvetica", 10))
    status_label.grid(row=9, column=0, columnspan=4, pady=(10, 0), sticky="ew")

    # Load icons
    add_update_icon = load_icon("icons/add_update.png")

    # Buttons with icons
    button_frame = ttk.Frame(main_frame)
    button_frame.grid(row=10, column=0, columnspan=4, pady=20, sticky="ew")

    add_purchase_button = ttk.Button(button_frame, text="Adicionar Compra", image=add_update_icon, compound=tk.LEFT,
                                     command=lambda: add_purchase(
                                         clients[client_dropdown.current()][0],
                                         date_entry.get(),
                                         total_amount_var.get().split(': R$')[1],
                                         [{'recipe_id': recipes[item_vars.index(item_var)][0],
                                           'quantity': quantity.get()} for item_var, quantity in
                                          zip(item_vars, quantity_vars)],
                                         status_label,
                                         purchase_listbox,
                                         client_dropdown,
                                         date_entry,
                                         item_frames,
                                         item_vars,
                                         quantity_vars,
                                         total_amount_var,
                                         item_frame_container,
                                         discount_var,
                                         discount_percentage_var,
                                         discount_check_var,
                                         recipes
                                     ))
    add_purchase_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 10))

    def delete_purchase():
        selected = purchase_listbox.curselection()
        if not selected:
            messagebox.showerror("Erro", "Nenhuma compra selecionada.")
            return
        purchase_id = purchase_listbox.get(selected[0]).split(' - ')[0]
        try:
            with connect_to_db() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM Purchase_Items WHERE purchase_id = ?', (purchase_id,))
                cursor.execute('DELETE FROM Compras WHERE purchase_id = ?', (purchase_id,))
                conn.commit()
                update_purchase_list(purchase_listbox)
                status_label.config(text=f"Compra {purchase_id} deletada com sucesso", foreground="green")
        except sqlite3.Error as e:
            log_error(f"Erro ao deletar compra: {e}")
            messagebox.showerror("Erro", f"Erro ao deletar compra: {e}")

    delete_button = ttk.Button(button_frame, text="Deletar Compra", command=delete_purchase)
    delete_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(10, 0))

    # Purchase list
    list_frame = ttk.Frame(main_frame)
    list_frame.grid(row=11, column=0, columnspan=4, pady=20, sticky="nsew")

    purchase_listbox = tk.Listbox(list_frame, width=50, height=10)
    purchase_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=purchase_listbox.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    purchase_listbox.config(yscrollcommand=scrollbar.set)

    main_frame.grid_rowconfigure(11, weight=1)
    main_frame.grid_columnconfigure(0, weight=1)

    update_purchase_list(purchase_listbox)

    add_purchase_window.mainloop()
