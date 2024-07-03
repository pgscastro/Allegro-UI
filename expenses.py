import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
import os
import re
from PIL import ImageTk

DATABASE_PATH = 'food_supplier.db'

def connect_to_db():
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        return conn
    except sqlite3.Error as e:
        messagebox.showerror("Erro de Conexão", f"Erro ao conectar-se ao banco de dados: {e}")
        return None

def initialize_expenses_db():
    with connect_to_db() as conn:
        if conn is not None:
            cursor = conn.cursor()
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS Despesas (
                expense_id INTEGER PRIMARY KEY,
                expense_type TEXT NOT NULL,
                amount REAL NOT NULL,
                date TEXT NOT NULL
            )
            ''')
            conn.commit()

def add_expense(expense_type, amount, date, status_label, expense_listbox):
    if not expense_type or not amount or not date:
        status_label.config(text="Todos os campos são obrigatórios", foreground="red")
        return

    try:
        amount = float(amount.replace(',', '.'))
    except ValueError:
        status_label.config(text="Valor deve ser um número", foreground="red")
        return

    if not validate_date(date):
        status_label.config(text="Data inválida. Use DD/MM/AAAA.", foreground="red")
        return

    try:
        with connect_to_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
            INSERT INTO Despesas (expense_type, amount, date) VALUES (?, ?, ?)
            ''', (expense_type, amount, date))
            conn.commit()
            status_label.config(text="Despesa adicionada com sucesso", foreground="green")
            update_expense_list(expense_listbox)
    except sqlite3.Error as e:
        messagebox.showerror("Erro", f"Erro ao adicionar despesa: {e}")

def update_expense_list(listbox):
    try:
        with connect_to_db() as conn:
            if conn is not None:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM Despesas')
                expenses = cursor.fetchall()
                listbox.delete(0, tk.END)
                for expense in expenses:
                    listbox.insert(tk.END, f"{expense[0]} - Tipo: {expense[1]} - Valor: R${expense[2]:.2f} - Data: {expense[3]}")
    except sqlite3.Error as e:
        messagebox.showerror("Erro", f"Erro ao atualizar lista de despesas: {e}")

def validate_date(date_text):
    try:
        if re.match(r'^\d{2}/\d{2}/\d{4}$', date_text):
            day, month, year = map(int, date_text.split('/'))
            return 1 <= day <= 31 and 1 <= month <= 12 and year > 0
        return False
    except ValueError:
        return False

def open_expenses_window(root):
    initialize_expenses_db()

    expenses_window = tk.Toplevel(root)
    expenses_window.title("Despesas")
    expenses_window.geometry("600x400")

    # Create the main frame
    main_frame = ttk.Frame(expenses_window, padding="20 20 20 20")
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Header
    header_label = ttk.Label(main_frame, text="Adicionar Nova Despesa", font=("Helvetica", 18, "bold"))
    header_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

    # Form labels and entries
    ttk.Label(main_frame, text="Tipo de Despesa:").grid(row=1, column=0, sticky="e", padx=(0, 10))
    expense_type_var = tk.StringVar()
    expense_type_dropdown = ttk.Combobox(main_frame, textvariable=expense_type_var, values=["Investimentos", "Materiais"])
    expense_type_dropdown.grid(row=1, column=1, sticky="ew")

    ttk.Label(main_frame, text="Valor:").grid(row=2, column=0, sticky="e", padx=(0, 10), pady=(10, 0))
    amount_var = tk.StringVar()
    amount_entry = ttk.Entry(main_frame, textvariable=amount_var)
    amount_entry.grid(row=2, column=1, sticky="ew")

    ttk.Label(main_frame, text="Data (DD/MM/AAAA):").grid(row=3, column=0, sticky="e", padx=(0, 10), pady=(10, 0))
    date_var = tk.StringVar(value=datetime.now().strftime("%d/%m/%Y"))  # Set the current date as default value
    date_entry = ttk.Entry(main_frame, textvariable=date_var)
    date_entry.grid(row=3, column=1, sticky="ew")

    date_entry.bind("<KeyRelease>", format_date)

    # Status label for messages in this window
    status_label = ttk.Label(main_frame, text="", font=("Helvetica", 10))
    status_label.grid(row=4, column=0, columnspan=2, pady=(10, 0), sticky="ew")

    # Load icons
    add_update_icon = load_icon("icons/add_update.png")

    # Buttons with icons
    button_frame = ttk.Frame(main_frame)
    button_frame.grid(row=5, column=0, columnspan=2, pady=20, sticky="ew")

    add_expense_button = ttk.Button(button_frame, text="Adicionar Despesa", image=add_update_icon, compound=tk.LEFT,
                                     command=lambda: add_expense(
                                         expense_type_var.get(),
                                         amount_entry.get(),
                                         date_entry.get(),
                                         status_label,
                                         expense_listbox
                                     ))
    add_expense_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 10))

    # Expense list
    list_frame = ttk.Frame(main_frame)
    list_frame.grid(row=6, column=0, columnspan=2, pady=20, sticky="nsew")

    expense_listbox = tk.Listbox(list_frame, width=50, height=10)
    expense_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=expense_listbox.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    expense_listbox.config(yscrollcommand=scrollbar.set)

    main_frame.grid_rowconfigure(6, weight=1)
    main_frame.grid_columnconfigure(0, weight=1)

    update_expense_list(expense_listbox)

    expenses_window.mainloop()

def load_icon(icon_path, size=(20, 20)):
    if os.path.exists(icon_path):
        return ImageTk.PhotoImage(Image.open(icon_path).resize(size, Image.LANCZOS))
    return None

def format_date(event):
    content = event.widget.get()
    if len(content) == 2 or len(content) == 5:
        event.widget.insert(tk.END, '/')
    elif len(content) > 10:
        event.widget.delete(10, tk.END)
