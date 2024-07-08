import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import sqlite3
import pandas as pd
from datetime import datetime
from ui_config import apply_styles, apply_color_palette


def validate_date_format(date_text):
    try:
        datetime.strptime(date_text, '%Y-%m-%d')
        return True
    except ValueError:
        return False


def validate_date_range(start_date, end_date):
    if not validate_date_format(start_date) or not validate_date_format(end_date):
        return False, "Date must be in YYYY-MM-DD format."
    if start_date > end_date:
        return False, "Start date must be before or equal to the end date."
    return True, ""


def export_data_to_excel(db_path, tables, start_date, end_date, file_path):
    conn = sqlite3.connect(db_path)
    writer = pd.ExcelWriter(file_path, engine='xlsxwriter')

    for table in tables:
        query = f'SELECT * FROM {table}'
        if 'date' in get_column_names(conn, table):
            query += f" WHERE date BETWEEN '{start_date}' AND '{end_date}'"

        df = pd.read_sql_query(query, conn)
        df.to_excel(writer, sheet_name=table, index=False)

    writer.close()
    conn.close()
    messagebox.showinfo("Export Data", "Data exported to Excel successfully!")


def get_column_names(conn, table_name):
    cursor = conn.cursor()
    cursor.execute(f'PRAGMA table_info({table_name})')
    columns = cursor.fetchall()
    return [column[1] for column in columns]


def get_database_schema(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    conn.close()
    return [table[0] for table in tables]


def select_file():
    file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
    if not file_path:
        return

    db_path = 'food_supplier.db'
    selected_tables = [table for table in table_vars if table_vars[table].get()]
    start_date = start_date_var.get()
    end_date = end_date_var.get()

    is_valid, message = validate_date_range(start_date, end_date)
    if not is_valid:
        messagebox.showerror("Invalid Date", message)
        return

    if not selected_tables:
        messagebox.showerror("No Selection", "Please select at least one table to export.")
        return

    export_data_to_excel(db_path, selected_tables, start_date, end_date, file_path)


def show_export_window():
    export_window = tk.Toplevel()
    export_window.title("Export Data to Excel")
    export_window.geometry("400x500")
    apply_styles(export_window)

    main_frame = ttk.Frame(export_window, padding="20 20 20 20")
    main_frame.pack(fill=tk.BOTH, expand=True)

    header_label = ttk.Label(main_frame, text="Export Data to Excel", style="Header.TLabel")
    header_label.pack(pady=(0, 20))

    ttk.Label(main_frame, text="Select Tables to Export:", style="TLabel").pack(anchor='w', pady=(0, 5))

    global table_vars
    table_vars = {}
    tables = get_database_schema('food_supplier.db')

    tables_frame = ttk.Frame(main_frame)
    tables_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

    for table in tables:
        var = tk.BooleanVar()
        table_vars[table] = var
        check_button = ttk.Checkbutton(tables_frame, text=table, variable=var, style="TCheckbutton")
        check_button.pack(anchor='w')

    date_frame = ttk.Frame(main_frame)
    date_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 10))

    ttk.Label(date_frame, text="Start Date (YYYY-MM-DD):", style="TLabel").grid(row=0, column=0, sticky='e', padx=(0, 10))
    global start_date_var
    start_date_var = tk.StringVar()
    start_date_entry = ttk.Entry(date_frame, textvariable=start_date_var, style="TEntry")
    start_date_entry.grid(row=0, column=1, sticky='w')
    start_date_entry.insert(0, 'YYYY-MM-DD')  # Placeholder text

    ttk.Label(date_frame, text="End Date (YYYY-MM-DD):", style="TLabel").grid(row=1, column=0, sticky='e', padx=(0, 10), pady=(10, 0))
    global end_date_var
    end_date_var = tk.StringVar()
    end_date_entry = ttk.Entry(date_frame, textvariable=end_date_var, style="TEntry")
    end_date_entry.grid(row=1, column=1, sticky='w', pady=(10, 0))
    end_date_entry.insert(0, 'YYYY-MM-DD')  # Placeholder text

    export_button = ttk.Button(main_frame, text="Export", command=select_file, style="TButton")
    export_button.pack(pady=(20, 0))

    apply_color_palette(header_label, "header")
    apply_color_palette(tables_frame, "frame")
    apply_color_palette(date_frame, "frame")
    apply_color_palette(export_button, "button")


if __name__ == "__main__":
    root = tk.Tk()
    apply_styles(root)
    show_export_window()
    root.mainloop()
