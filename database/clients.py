import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk
import re

from ui import ui_config
from ui.ui_config import apply_styles, load_icon

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
        CREATE TABLE IF NOT EXISTS Clientes (
            client_id INTEGER PRIMARY KEY,
            client_name TEXT NOT NULL,
            birthday TEXT NOT NULL,
            address TEXT NOT NULL
        )
        ''')
        conn.commit()
        conn.close()

def validate_inputs(client_name, birthday, address):
    errors = []
    if not client_name:
        errors.append("Nome do Cliente é obrigatório")
    if not birthday:
        errors.append("Data de Aniversário é obrigatória")
    elif not re.match(r'\d{2}/\d{2}/\d{4}', birthday):
        errors.append("Data de Aniversário deve estar no formato DD/MM/YYYY")
    if not address:
        errors.append("Endereço é obrigatório")
    return errors

def add_or_update_client(client_name, birthday, address, status_label, client_listbox, client_name_entry,
                         birthday_entry, address_entry):
    errors = validate_inputs(client_name, birthday, address)
    if errors:
        status_label.config(text="; ".join(errors), foreground="red")
        highlight_fields(client_name_entry, birthday_entry, address_entry)
        return

    conn = connect_to_db()
    if conn is not None:
        cursor = conn.cursor()
        cursor.execute('''
        SELECT client_id FROM Clientes WHERE client_name = ?
        ''', (client_name,))
        client = cursor.fetchone()

        if client:
            if tk.messagebox.askyesno("Confirmar Atualização",
                                      f"Você tem certeza que deseja atualizar o cliente '{client_name}'?"):
                cursor.execute('''
                UPDATE Clientes
                SET birthday = ?, address = ?
                WHERE client_id = ?
                ''', (birthday, address, client[0]))
                status_label.config(text=f"Cliente '{client_name}' atualizado com sucesso.", foreground="green")
        else:
            cursor.execute('''
            INSERT INTO Clientes (client_name, birthday, address) VALUES (?, ?, ?)
            ''', (client_name, birthday, address))
            status_label.config(text=f"Cliente '{client_name}' adicionado com sucesso.", foreground="green")
        conn.commit()
        conn.close()
        update_client_list(client_listbox)
        clear_form(client_name_entry, birthday_entry, address_entry)

def highlight_fields(*fields):
    for field in fields:
        field.config(background="pink")

def clear_highlight(*fields):
    for field in fields:
        field.config(background="white")

def clear_form(*fields):
    for field in fields:
        field.delete(0, tk.END)
        clear_highlight(field)

def update_client_list(listbox):
    conn = connect_to_db()
    if conn is not None:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Clientes ORDER BY client_name')
        clients = cursor.fetchall()
        listbox.delete(0, tk.END)
        for client in clients:
            listbox.insert(tk.END, f"{client[0]} - {client[1]} - {client[2]} - {client[3]}")
        conn.close()

def delete_client(client_listbox, status_label):
    selected_item = client_listbox.curselection()
    if not selected_item:
        status_label.config(text="Erro de Seleção: Nenhum cliente selecionado", foreground="red")
        return
    client_id = int(client_listbox.get(selected_item[0]).split(' ')[0])
    if tk.messagebox.askyesno("Confirmar Exclusão", "Você tem certeza que deseja desativar este cliente?"):
        conn = connect_to_db()
        if conn is not None:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM Clientes WHERE client_id = ?', (client_id,))
            conn.commit()
            conn.close()
            status_label.config(text=f"Cliente ID '{client_id}' desativado com sucesso.", foreground="green")
            update_client_list(client_listbox)

def search_clients(search_term, listbox):
    conn = connect_to_db()
    if conn is not None:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Clientes WHERE client_name LIKE ? ORDER BY client_name',
                       ('%' + search_term + '%',))
        clients = cursor.fetchall()
        listbox.delete(0, tk.END)
        for client in clients:
            listbox.insert(tk.END, f"{client[0]} - {client[1]} - {client[2]} - {client[3]}")
        conn.close()

def format_date(event):
    content = event.widget.get()
    if len(content) == 2 or len(content) == 5:
        event.widget.insert(tk.END, '/')
    elif len(content) > 10:
        event.widget.delete(10, tk.END)

def open_add_client_window(root):
    initialize_database()
    apply_styles(root)

    add_client_window = tk.Toplevel(root)
    add_client_window.title("Adicionar Cliente")
    add_client_window.geometry("750x500")
    add_client_window.minsize(750, 500)
    add_client_window.configure(bg=ui_config.bg_color)  # Set background color

    # Create the main frame
    main_frame = ttk.Frame(add_client_window, padding="20 20 20 20", style="Main.TFrame")
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Header
    header_label = ttk.Label(main_frame, text="Adicionar Novo Cliente", style="Header.TLabel")
    header_label.grid(row=0, column=0, columnspan=4, pady=(0, 20))

    # Form labels and entries
    form_frame = ttk.Frame(main_frame, style="Main.TFrame")
    form_frame.grid(row=1, column=0, columnspan=4, pady=10, sticky="ew")

    ttk.Label(form_frame, text="Nome do Cliente:", style="Main.TLabel").grid(row=0, column=0, sticky="e", padx=(0, 10))
    client_name_entry = ttk.Entry(form_frame, style="Main.TEntry")
    client_name_entry.grid(row=0, column=1, columnspan=3, sticky="ew")

    ttk.Label(form_frame, text="Data de Aniversário (DD/MM/YYYY):", style="Main.TLabel").grid(row=1, column=0, sticky="e", padx=(0, 10), pady=(10, 0))
    birthday_entry = ttk.Entry(form_frame, style="Main.TEntry")
    birthday_entry.grid(row=1, column=1, columnspan=3, sticky="ew")
    birthday_entry.bind('<KeyRelease>', format_date)

    ttk.Label(form_frame, text="Endereço:", style="Main.TLabel").grid(row=2, column=0, sticky="e", padx=(0, 10), pady=(10, 0))
    address_entry = ttk.Entry(form_frame, style="Main.TEntry")
    address_entry.grid(row=2, column=1, columnspan=3, sticky="ew")

    form_frame.grid_columnconfigure(1, weight=1)

    # Load icons
    add_update_icon = load_icon("../icons/add_update.png")
    delete_icon = load_icon("../icons/delete.png")
    search_icon = load_icon("icons/search.png")

    # Buttons with icons
    button_frame = ttk.Frame(main_frame, style="Main.TFrame")
    button_frame.grid(row=2, column=0, columnspan=4, pady=20, sticky="ew")

    add_update_button = ttk.Button(button_frame, text="Adicionar/Atualizar Cliente", image=add_update_icon,
                                   compound=tk.LEFT,
                                   command=lambda: add_or_update_client(
                                       client_name_entry.get(),
                                       birthday_entry.get(),
                                       address_entry.get(),
                                       status_label,
                                       client_listbox,
                                       client_name_entry,
                                       birthday_entry,
                                       address_entry
                                   ), style="Main.TButton")
    add_update_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 10))

    delete_button = ttk.Button(button_frame, text="Desativar Cliente", image=delete_icon, compound=tk.LEFT,
                               command=lambda: delete_client(
                                   client_listbox,
                                   status_label
                               ), style="Main.TButton")
    delete_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 10))

    search_label = ttk.Label(button_frame, text="Buscar: ", style="Main.TLabel")
    search_label.pack(side=tk.LEFT, padx=(10, 0))

    search_entry = ttk.Entry(button_frame, style="Main.TEntry")
    search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

    search_button = ttk.Button(button_frame, text="Buscar", image=search_icon, compound=tk.LEFT,
                               command=lambda: search_clients(search_entry.get(), client_listbox), style="Main.TButton")
    search_button.pack(side=tk.LEFT, padx=(0, 10))

    # Client list
    list_frame = ttk.Frame(main_frame, style="Main.TFrame")
    list_frame.grid(row=3, column=0, columnspan=4, pady=20, sticky="nsew")

    client_listbox = tk.Listbox(list_frame, width=50, height=10)
    client_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=client_listbox.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    client_listbox.config(yscrollcommand=scrollbar.set)

    main_frame.grid_rowconfigure(3, weight=1)
    main_frame.grid_columnconfigure(0, weight=1)

    # Status label
    status_label = ttk.Label(main_frame, text="", style="Status.TLabel")
    status_label.grid(row=4, column=0, columnspan=4, pady=(10, 0), sticky="ew")

    update_client_list(client_listbox)

    add_client_window.mainloop()

# Ensure "icons/add_update.png", "icons/delete.png", and "icons/search.png" exist, or replace the paths with the correct ones.
