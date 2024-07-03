import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk
from tkcalendar import DateEntry  # You may need to install tkcalendar
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime

DATABASE_PATH = 'food_supplier.db'

def connect_to_db():
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        return conn
    except sqlite3.Error as e:
        messagebox.showerror("Erro de Conexão", f"Erro ao conectar-se ao banco de dados: {e}")
        return None

def get_monthly_purchases(start_month, end_month):
    with connect_to_db() as conn:
        if conn is not None:
            cursor = conn.cursor()
            cursor.execute('''
            SELECT strftime('%Y-%m', purchase_date) as month, SUM(total_amount)
            FROM Compras
            WHERE purchase_date BETWEEN ? AND ?
            GROUP BY strftime('%Y-%m', purchase_date)
            ''', (start_month, end_month))
            purchases = cursor.fetchall()
            return purchases
    return []

def get_expenses(start_month, end_month):
    with connect_to_db() as conn:
        if conn is not None:
            cursor = conn.cursor()
            cursor.execute('''
            SELECT strftime('%Y-%m', date) as month, expense_type, SUM(amount)
            FROM Despesas
            WHERE date BETWEEN ? AND ?
            GROUP BY strftime('%Y-%m', date), expense_type
            ''', (start_month, end_month))
            expenses = cursor.fetchall()
            return expenses
    return []

def plot_monthly_purchases(canvas, start_month, end_month):
    purchases = get_monthly_purchases(start_month, end_month)
    expenses = get_expenses(start_month, end_month)

    months = [datetime.strptime(month, '%Y-%m').strftime('%b %Y') for month, _ in purchases]
    purchase_totals = [total for _, total in purchases]

    inv_expenses = [sum(expense[2] for expense in expenses if expense[1] == "Investimentos")]
    mat_expenses = [sum(expense[2] for expense in expenses if expense[1] == "Materiais")]
    total_expenses = [inv + mat for inv, mat in zip(inv_expenses, mat_expenses)]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(months, purchase_totals, label='Compras')
    ax.plot(months, inv_expenses, label='Investimentos', color='orange')
    ax.plot(months, mat_expenses, label='Materiais', color='purple')
    ax.plot(months, total_expenses, label='Total Despesas', color='red')

    ax.set_xlabel('Meses')
    ax.set_ylabel('Total em R$')
    ax.set_title('Compras Mensais e Despesas')
    ax.legend()

    canvas.draw()

def open_monthly_purchases_window(root):
    window = tk.Toplevel(root)
    window.title("Compras Mensais")
    window.geometry("800x600")

    # Create the main frame
    main_frame = ttk.Frame(window, padding="20 20 20 20")
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Date range selection
    ttk.Label(main_frame, text="Período Inicial:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
    start_date = DateEntry(main_frame, date_pattern='dd/MM/yyyy')
    start_date.grid(row=0, column=1, padx=5, pady=5)

    ttk.Label(main_frame, text="Período Final:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
    end_date = DateEntry(main_frame, date_pattern='dd/MM/yyyy')
    end_date.grid(row=0, column=3, padx=5, pady=5)

    # Canvas for plotting
    fig = plt.Figure(figsize=(10, 6))
    canvas = FigureCanvasTkAgg(fig, master=main_frame)
    canvas.get_tk_widget().grid(row=1, column=0, columnspan=4, padx=5, pady=5, sticky="nsew")

    main_frame.grid_rowconfigure(1, weight=1)
    main_frame.grid_columnconfigure(0, weight=1)

    # Plot button
    plot_button = ttk.Button(main_frame, text="Plotar", command=lambda: plot_monthly_purchases(canvas, start_date.get_date(), end_date.get_date()))
    plot_button.grid(row=2, column=0, columnspan=4, pady=10)

    window.mainloop()

def open_analytics_menu(root):
    window = tk.Toplevel(root)
    window.title("Análises")
    window.geometry("400x300")

    # Create the main frame
    main_frame = ttk.Frame(window, padding="20 20 20 20")
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Add buttons for each analytic option
    ttk.Button(main_frame, text="Relatorio Mensal", command=lambda: open_monthly_purchases_window(root)).pack(fill=tk.X, pady=5)
    ttk.Button(main_frame, text="Top Clientes", command=lambda: print("Implementar Top Clientes")).pack(fill=tk.X, pady=5)
    ttk.Button(main_frame, text="Próximos Aniversários", command=lambda: print("Implementar Próximos Aniversários")).pack(fill=tk.X, pady=5)
    ttk.Button(main_frame, text="Exportar Dados para Excel", command=lambda: print("Implementar Exportação de Dados")).pack(fill=tk.X, pady=5)

    window.mainloop()
