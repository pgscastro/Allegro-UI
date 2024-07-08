import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
from ui_config import apply_styles


def convert_date_format(date_str):
    try:
        # Try to parse the date in DD/MM/YYYY format and convert to YYYY-MM-DD
        converted_date = datetime.strptime(date_str, '%d/%m/%Y').strftime('%Y-%m-%d')
    except ValueError:
        # If parsing fails, assume the date is already in the correct format
        converted_date = date_str
    return converted_date


def get_next_birthday(birthday):
    current_year = datetime.now().year
    birthday_this_year = datetime.strptime(birthday, "%Y-%m-%d").replace(year=current_year)
    if birthday_this_year < datetime.now():
        birthday_next_year = birthday_this_year.replace(year=current_year + 1)
        return birthday_next_year
    return birthday_this_year


def show_upcoming_birthdays(num_items):
    conn = sqlite3.connect('../database/food_supplier.db')
    cursor = conn.cursor()

    cursor.execute('''
    SELECT client_name, birthday 
    FROM Clientes
    ''')
    birthdays = cursor.fetchall()
    conn.close()

    # Convert all birthdays to YYYY-MM-DD format for sorting
    converted_birthdays = [(name, convert_date_format(bday)) for name, bday in birthdays]

    today = datetime.now()
    sorted_birthdays = sorted(converted_birthdays, key=lambda x: (get_next_birthday(x[1]) - today).days)

    return sorted_birthdays[:num_items]  # Return the number of birthdays specified by user


def open_upcoming_birthdays_window():
    upcoming_birthdays_window = tk.Toplevel()
    upcoming_birthdays_window.title("Próximos Aniversários")
    upcoming_birthdays_window.geometry("600x400")
    upcoming_birthdays_window.minsize(600, 400)

    apply_styles(upcoming_birthdays_window)  # Apply styles

    main_frame = ttk.Frame(upcoming_birthdays_window, padding="20 20 20 20")
    main_frame.pack(fill=tk.BOTH, expand=True)

    header_label = ttk.Label(main_frame, text="Próximos Aniversários", style="Header.TLabel")
    header_label.grid(row=0, column=0, pady=(0, 20))

    tree = ttk.Treeview(main_frame, columns=("Cliente", "Aniversário"), show='headings')
    tree.heading("Cliente", text="Cliente")
    tree.heading("Aniversário", text="Aniversário")
    tree.grid(row=2, column=0, sticky='nsew')

    main_frame.grid_rowconfigure(2, weight=1)
    main_frame.grid_columnconfigure(0, weight=1)

    control_frame = ttk.Frame(main_frame)
    control_frame.grid(row=1, column=0, pady=(0, 10))

    ttk.Label(control_frame, text="Número de clientes a ser exibido:", style="TLabel").pack(side=tk.LEFT, padx=(0, 10))
    num_items_var = tk.StringVar(value="10")
    num_items_entry = ttk.Entry(control_frame, textvariable=num_items_var)
    num_items_entry.pack(side=tk.LEFT, padx=(0, 10))

    def update_tree():
        try:
            num_items = int(num_items_var.get())
            if num_items <= 0:
                raise ValueError
            birthdays = show_upcoming_birthdays(num_items)
            tree.delete(*tree.get_children())
            for birthday in birthdays:
                tree.insert('', tk.END,
                            values=(birthday[0], datetime.strptime(birthday[1], "%Y-%m-%d").strftime('%d/%m/%Y')))
        except ValueError:
            messagebox.showerror("Erro", "Por favor, insira um número válido.")

    update_button = ttk.Button(control_frame, text="Atualizar", command=update_tree, style="TButton")
    update_button.pack(side=tk.LEFT)

    update_tree()  # Initial load

    upcoming_birthdays_window.mainloop()


if __name__ == "__main__":
    root = tk.Tk()
    open_upcoming_birthdays_window()
    root.mainloop()
