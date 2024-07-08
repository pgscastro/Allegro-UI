# top_customers.py

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from ui_config import apply_styles
import sqlite3
from datetime import datetime

DATABASE_PATH = '../database/food_supplier.db'


def connect_to_db():
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        return conn
    except sqlite3.Error as e:
        print(f"Erro ao conectar-se ao banco de dados: {e}")
        return None


def get_top_customers(n):
    conn = connect_to_db()
    if conn is None:
        return []

    cursor = conn.cursor()
    query = '''
    SELECT Clientes.client_name, SUM(Compras.total_amount) as total_spent
    FROM Compras
    JOIN Clientes ON Compras.client_id = Clientes.client_id
    GROUP BY Clientes.client_name
    ORDER BY total_spent DESC
    LIMIT ?
    '''
    print(f"Executing query: \n{query}\nWith parameter: {n}")
    cursor.execute(query, (n,))
    top_customers = cursor.fetchall()
    print(f"Top customers fetched: {top_customers}")
    conn.close()
    return top_customers


def get_top_customers_current_month(n):
    conn = connect_to_db()
    if conn is None:
        return []

    cursor = conn.cursor()
    current_month = datetime.now().strftime('%Y-%m')
    query = '''
    SELECT Clientes.client_name, SUM(Compras.total_amount) as total_spent
    FROM Compras
    JOIN Clientes ON Compras.client_id = Clientes.client_id
    WHERE strftime('%Y-%m', Compras.purchase_date) = ?
    GROUP BY Clientes.client_name
    ORDER BY total_spent DESC
    LIMIT ?
    '''
    print(f"Executing query: \n{query}\nWith parameters: {current_month}, {n}")
    cursor.execute(query, (current_month, n))
    top_customers = cursor.fetchall()
    print(f"Top customers fetched for current month: {top_customers}")
    conn.close()
    return top_customers


def show_top_customers_interface():
    def display_top_customers():
        try:
            n = int(number_of_customers_var.get())
            print(f"Number of customers to display: {n}")
        except ValueError:
            messagebox.showerror("Erro", "Por favor, insira um número válido.")
            return

        if selected_option.get() == "overall":
            top_customers = get_top_customers(n)
        else:
            top_customers = get_top_customers_current_month(n)

        results_text.delete('1.0', tk.END)  # Clear previous results
        for i, (name, total_spent) in enumerate(top_customers, start=1):
            results_text.insert(tk.END, f"{i}. {name}: R${total_spent:.2f}\n")

    top_customers_window = tk.Toplevel()
    top_customers_window.title("Top Clientes")
    top_customers_window.geometry("400x400")

    apply_styles(top_customers_window)  # Apply styles

    main_frame = ttk.Frame(top_customers_window, padding="20 20 20 20")
    main_frame.pack(fill=tk.BOTH, expand=True)

    ttk.Label(main_frame, text="Número de Clientes:", style="TLabel").pack()
    number_of_customers_var = tk.StringVar()
    number_of_customers_entry = ttk.Entry(main_frame, textvariable=number_of_customers_var, style="TEntry")
    number_of_customers_entry.pack(pady=5)

    selected_option = tk.StringVar(value="overall")
    overall_button = ttk.Radiobutton(main_frame, text="Top Clientes Geral", variable=selected_option, value="overall",
                                     style="TRadiobutton")
    overall_button.pack(pady=5)

    monthly_button = ttk.Radiobutton(main_frame, text="Top Clientes do Mês Atual", variable=selected_option,
                                     value="monthly", style="TRadiobutton")
    monthly_button.pack(pady=5)

    display_button = ttk.Button(main_frame, text="Mostrar Top Clientes", command=display_top_customers, style="TButton")
    display_button.pack(pady=5)

    results_text = tk.Text(main_frame, height=10, width=40)
    results_text.pack(pady=5)

    main_frame.grid_rowconfigure(1, weight=1)
    main_frame.grid_columnconfigure(0, weight=1)


if __name__ == "__main__":
    root = tk.Tk()
    apply_styles(root)  # Apply styles
    show_top_customers_interface()
    root.mainloop()
