import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk
from ui.ui_config import apply_styles
import re
from datetime import datetime
import pandas as pd

DATABASE_PATH = 'food_supplier.db'


def connect_to_db():
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        return conn
    except sqlite3.Error as e:
        log_error(f"Erro de Conexão: {e}")
        messagebox.showerror("Erro de Conexão", f"Erro ao conectar-se ao banco de dados: {e}")
        return None


def log_error(error_message):
    with open("error.log", "a") as error_log:
        error_log.write(f"{datetime.now()}: {error_message}\n")


def initialize_database():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Despesas (
        expense_id INTEGER PRIMARY KEY,
        description TEXT NOT NULL,
        date TEXT NOT NULL,
        amount REAL NOT NULL,
        type TEXT NOT NULL
    )
    ''')

    conn.commit()
    conn.close()


def validate_date(date_text):
    try:
        if re.match(r'^\d{2}/\d{2}/\d{4}$', date_text):
            datetime.strptime(date_text, '%d/%m/%Y')
            return True
        return False
    except ValueError:
        return False


def add_expense(description, date, amount, expense_type, status_label, expense_listbox):
    if not description or not date or not amount or not expense_type:
        messagebox.showwarning("Erro de Entrada", "Todos os campos são obrigatórios")
        return
    if not validate_date(date):
        messagebox.showwarning("Erro de Entrada", "Data inválida. Use o formato DD/MM/AAAA.")
        return
    try:
        amount = float(amount.replace(',', '.'))
    except ValueError:
        messagebox.showwarning("Erro de Entrada", "O valor deve ser um número")
        return

    conn = connect_to_db()
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO Despesas (description, date, amount, type) VALUES (?, ?, ?, ?)
    ''', (description, date, amount, expense_type))
    messagebox.showinfo("Sucesso", "Despesa adicionada com sucesso!")

    conn.commit()
    conn.close()
    update_expense_list(expense_listbox)
    status_label.config(text=f"Despesa '{description}' adicionada com sucesso.")


def update_expense_list(listbox, search_term=""):
    conn = connect_to_db()
    cursor = conn.cursor()
    if search_term:
        cursor.execute('''
        SELECT * FROM Despesas WHERE description LIKE ? OR type LIKE ? ORDER BY date
        ''', (f"%{search_term}%", f"%{search_term}%"))
    else:
        cursor.execute('SELECT * FROM Despesas ORDER BY date')
    expenses = cursor.fetchall()
    listbox.delete(0, tk.END)
    for expense in expenses:
        listbox.insert(tk.END, f"{expense[0]} - {expense[1]} - {expense[2]} - R${expense[3]:.2f} - {expense[4]}")
    conn.close()


def delete_expense(expense_listbox, status_label):
    selected_item = expense_listbox.curselection()
    if not selected_item:
        messagebox.showwarning("Erro de Seleção", "Nenhuma despesa selecionada")
        return
    expense_id = int(expense_listbox.get(selected_item[0]).split(' ')[0])
    if tk.messagebox.askyesno("Confirmar Exclusão", "Você tem certeza que deseja excluir esta despesa?"):
        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM Despesas WHERE expense_id = ?', (expense_id,))
        conn.commit()
        conn.close()
        messagebox.showinfo("Sucesso", "Despesa excluída com sucesso!")
        update_expense_list(expense_listbox)
        status_label.config(text=f"Despesa ID '{expense_id}' excluída com sucesso.")


def format_date(event):
    content = event.widget.get()
    if len(content) == 2 or len(content) == 5:
        event.widget.insert(tk.END, '/')
    elif len(content) > 10:
        event.widget.delete(10, tk.END)


def export_to_excel(listbox):
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Despesas')
    expenses = cursor.fetchall()
    conn.close()

    df = pd.DataFrame(expenses, columns=["ID", "Descrição", "Data", "Valor", "Tipo"])
    df.to_excel('despesas.xlsx', index=False)
    messagebox.showinfo("Exportação Bem-Sucedida", "Despesas exportadas para 'despesas.xlsx' com sucesso!")


def open_expenses_window(root):
    initialize_database()
    expenses_window = tk.Toplevel(root)
    expenses_window.title("Despesas")
    expenses_window.geometry("600x500")
    expenses_window.minsize(600, 500)

    # Create the main frame
    main_frame = ttk.Frame(expenses_window, padding="20 20 20 20", style="Main.TFrame")
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Header
    header_label = ttk.Label(main_frame, text="Despesas", font=("Helvetica", 18, "bold"))
    header_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

    # Form labels and entries
    form_frame = ttk.Frame(main_frame)
    form_frame.grid(row=1, column=0, columnspan=2, pady=10, sticky="ew")

    ttk.Label(form_frame, text="Descrição:").grid(row=0, column=0, sticky="e", padx=(0, 10))
    description_entry = ttk.Entry(form_frame)
    description_entry.grid(row=0, column=1, sticky="ew")

    ttk.Label(form_frame, text="Data (DD/MM/AAAA):").grid(row=1, column=0, sticky="e", padx=(0, 10), pady=(10, 0))
    date_entry = ttk.Entry(form_frame)
    date_entry.grid(row=1, column=1, sticky="ew")
    date_entry.bind('<KeyRelease>', format_date)

    ttk.Label(form_frame, text="Valor (R$):").grid(row=2, column=0, sticky="e", padx=(0, 10), pady=(10, 0))
    amount_entry = ttk.Entry(form_frame)
    amount_entry.grid(row=2, column=1, sticky="ew")

    ttk.Label(form_frame, text="Tipo:").grid(row=3, column=0, sticky="e", padx=(0, 10), pady=(10, 0))
    expense_type_combobox = ttk.Combobox(form_frame, values=["Investimentos", "Materiais"])
    expense_type_combobox.grid(row=3, column=1, sticky="ew")

    form_frame.grid_columnconfigure(1, weight=1)

    # Buttons with icons
    button_frame = ttk.Frame(main_frame)
    button_frame.grid(row=2, column=0, columnspan=2, pady=20, sticky="ew")

    add_button = ttk.Button(button_frame, text="Adicionar Despesa",
                            command=lambda: add_expense(
                                description_entry.get(),
                                date_entry.get(),
                                amount_entry.get(),
                                expense_type_combobox.get(),
                                status_label,
                                expense_listbox
                            ), style="TButton")
    add_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 10))

    delete_button = ttk.Button(button_frame, text="Excluir Despesa",
                               command=lambda: delete_expense(
                                   expense_listbox,
                                   status_label
                               ), style="TButton")
    delete_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 10))

    export_button = ttk.Button(button_frame, text="Exportar para Excel",
                               command=lambda: export_to_excel(expense_listbox))
    export_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 10))

    # Search box
    search_frame = ttk.Frame(main_frame)
    search_frame.grid(row=3, column=0, columnspan=2, pady=10, sticky="ew")

    ttk.Label(search_frame, text="Buscar:").grid(row=0, column=0, sticky="e", padx=(0, 10))
    search_entry = ttk.Entry(search_frame)
    search_entry.grid(row=0, column=1, sticky="ew")
    search_entry.bind('<KeyRelease>', lambda event: update_expense_list(expense_listbox, search_entry.get()))

    search_frame.grid_columnconfigure(1, weight=1)

    # Expense list
    expense_listbox = tk.Listbox(main_frame, width=50, height=10)
    expense_listbox.grid(row=4, column=0, columnspan=2, pady=20, sticky="nsew")

    main_frame.grid_rowconfigure(4, weight=1)
    main_frame.grid_columnconfigure(0, weight=1)

    # Status label
    status_label = ttk.Label(main_frame, text="", font=("Helvetica", 10))
    status_label.grid(row=5, column=0, columnspan=2, pady=(10, 0), sticky="ew")

    apply_styles(expenses_window)  # Apply styles
    update_expense_list(expense_listbox)
    expenses_window.mainloop()
