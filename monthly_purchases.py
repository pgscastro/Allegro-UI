import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt


def export_to_excel(data):
    df = pd.DataFrame(data, columns=["Cliente", "Data", "Valor Gasto", "Itens Comprados"])
    df.to_excel('compras_mensais.xlsx', index=False)
    tk.messagebox.showinfo("Exportação Bem Sucedida", "Dados de compras mensais exportados para 'compras_mensais.xlsx' com sucesso!")


def show_graph(data, expenses):
    clients = [row[0] for row in data]
    amounts = [row[2] for row in data]

    plt.figure(figsize=(10, 6))
    plt.bar(clients, amounts, label='Compras')

    # Plotting expenses
    months = list(set(row[1][:7] for row in data))  # Extract unique months in YYYY-MM format
    months.sort()  # Ensure months are sorted

    inv_expenses = [sum(expense[2] for expense in expenses if expense[1] == 'investimentos' and expense[0][:7] == month) for month in months]
    mat_expenses = [sum(expense[2] for expense in expenses if expense[1] == 'materiais' and expense[0][:7] == month) for month in months]
    total_expenses = [inv + mat for inv, mat in zip(inv_expenses, mat_expenses)]

    plt.plot(months, inv_expenses, color='orange', label='Investimentos')
    plt.plot(months, mat_expenses, color='purple', label='Materiais')
    plt.plot(months, total_expenses, color='red', label='Total Despesas')

    plt.xlabel('Meses')
    plt.ylabel('Valor Gasto')
    plt.title('Compras Mensais por Cliente')
    plt.xticks(rotation=45, ha="right")
    plt.legend()
    plt.tight_layout()
    plt.show()


def show_monthly_purchases():
    def fetch_data(start_month, start_year, end_month, end_year, client_filter=""):
        conn = sqlite3.connect('food_supplier.db')
        cursor = conn.cursor()
        query = '''
        SELECT Clients.name, Purchases.purchase_date, Purchases.amount_spent, Purchases.items_purchased 
        FROM Purchases 
        JOIN Clients ON Purchases.client_id = Clients.client_id 
        WHERE (strftime('%m', Purchases.purchase_date) BETWEEN ? AND ?)
        AND (strftime('%Y', Purchases.purchase_date) BETWEEN ? AND ?)
        '''
        params = [start_month, end_month, start_year, end_year]
        if client_filter:
            query += ' AND Clients.name LIKE ?'
            params.append(f"%{client_filter}%")
        cursor.execute(query, params)
        data = cursor.fetchall()
        conn.close()
        return data

    def fetch_expenses():
        conn = sqlite3.connect('food_supplier.db')
        cursor = conn.cursor()
        cursor.execute('SELECT purchase_date, category, amount FROM Despesas')
        expenses = cursor.fetchall()
        conn.close()
        return expenses

    def update_treeview(data):
        for row in tree.get_children():
            tree.delete(row)
        total_amount = 0
        for purchase in data:
            tree.insert('', tk.END, values=purchase)
            total_amount += purchase[2]
        total_label.config(text=f"Valor Total Gasto: R${total_amount:.2f}")

    def on_filter_change(*args):
        start_month = start_month_var.get()
        start_year = start_year_var.get()
        end_month = end_month_var.get()
        end_year = end_year_var.get()
        client_filter = client_filter_var.get()
        data = fetch_data(start_month, start_year, end_month, end_year, client_filter)
        update_treeview(data)

    def on_view_details():
        selected_item = tree.selection()
        if not selected_item:
            tk.messagebox.showwarning("Nenhuma Seleção", "Por favor, selecione uma compra para ver os detalhes.")
            return
        item = tree.item(selected_item)
        details = item['values']
        tk.messagebox.showinfo("Detalhes da Compra", f"Cliente: {details[0]}\nData: {details[1]}\nValor Gasto: R${details[2]:.2f}\nItens Comprados: {details[3]}")

    monthly_purchases_window = tk.Toplevel()
    monthly_purchases_window.title("Compras Mensais")
    monthly_purchases_window.geometry("800x600")
    monthly_purchases_window.minsize(800, 600)

    main_frame = ttk.Frame(monthly_purchases_window, padding="20 20 20 20")
    main_frame.pack(fill=tk.BOTH, expand=True)

    header_label = ttk.Label(main_frame, text="Compras Mensais", font=("Helvetica", 18, "bold"))
    header_label.grid(row=0, column=0, columnspan=6, pady=(0, 20))

    control_frame = ttk.Frame(main_frame)
    control_frame.grid(row=1, column=0, columnspan=6, pady=(0, 20))

    ttk.Label(control_frame, text="Mês Início:").grid(row=0, column=0, padx=5)
    start_month_var = tk.StringVar(value=datetime.now().strftime('%m'))
    start_month_combobox = ttk.Combobox(control_frame, textvariable=start_month_var, values=[f"{i:02d}" for i in range(1, 13)], width=5)
    start_month_combobox.grid(row=0, column=1, padx=5)

    ttk.Label(control_frame, text="Ano Início:").grid(row=0, column=2, padx=5)
    start_year_var = tk.StringVar(value=datetime.now().strftime('%Y'))
    start_year_combobox = ttk.Combobox(control_frame, textvariable=start_year_var, values=[str(i) for i in range(2000, datetime.now().year + 1)], width=7)
    start_year_combobox.grid(row=0, column=3, padx=5)

    ttk.Label(control_frame, text="Mês Fim:").grid(row=1, column=0, padx=5)
    end_month_var = tk.StringVar(value=datetime.now().strftime('%m'))
    end_month_combobox = ttk.Combobox(control_frame, textvariable=end_month_var, values=[f"{i:02d}" for i in range(1, 13)], width=5)
    end_month_combobox.grid(row=1, column=1, padx=5)

    ttk.Label(control_frame, text="Ano Fim:").grid(row=1, column=2, padx=5)
    end_year_var = tk.StringVar(value=datetime.now().strftime('%Y'))
    end_year_combobox = ttk.Combobox(control_frame, textvariable=end_year_var, values=[str(i) for i in range(2000, datetime.now().year + 1)], width=7)
    end_year_combobox.grid(row=1, column=3, padx=5)

    ttk.Label(control_frame, text="Filtro Cliente:").grid(row=2, column=0, padx=5)
    client_filter_var = tk.StringVar()
    client_filter_entry = ttk.Entry(control_frame, textvariable=client_filter_var)
    client_filter_entry.grid(row=2, column=1, columnspan=3, padx=5, sticky="ew")

    start_month_var.trace_add('write', on_filter_change)
    start_year_var.trace_add('write', on_filter_change)
    end_month_var.trace_add('write', on_filter_change)
    end_year_var.trace_add('write', on_filter_change)
    client_filter_var.trace_add('write', on_filter_change)

    tree = ttk.Treeview(main_frame, columns=("Cliente", "Data", "Valor Gasto", "Itens Comprados"), show='headings')
    tree.heading("Cliente", text="Cliente")
    tree.heading("Data", text="Data")
    tree.heading("Valor Gasto", text="Valor Gasto")
    tree.heading("Itens Comprados", text="Itens Comprados")
    tree.grid(row=2, column=0, columnspan=6, sticky='nsew')

    main_frame.grid_rowconfigure(2, weight=1)
    main_frame.grid_columnconfigure(0, weight=1)

    total_label = ttk.Label(main_frame, text="Valor Total Gasto: R$0.00", font=("Helvetica", 12, "bold"))
    total_label.grid(row=3, column=0, pady=(10, 0), sticky="w")

    export_button = ttk.Button(main_frame, text="Exportar para Excel", command=lambda: export_to_excel(fetch_data(start_month_var.get(), start_year_var.get(), end_month_var.get(), end_year_var.get(), client_filter_var.get())))
    export_button.grid(row=3, column=1, pady=(10, 0), sticky="e")

    details_button = ttk.Button(main_frame, text="Ver Detalhes", command=on_view_details)
    details_button.grid(row=3, column=2, pady=(10, 0), sticky="e")

    graph_button = ttk.Button(main_frame, text="Mostrar Gráfico", command=lambda: show_graph(fetch_data(start_month_var.get(), start_year_var.get(), end_month_var.get(), end_year_var.get(), client_filter_var.get()), fetch_expenses()))
    graph_button.grid(row=3, column=3, pady=(10, 0), sticky="e")

    # Initial data fetch and display
    update_treeview(fetch_data(start_month_var.get(), start_year_var.get(), end_month_var.get(), end_year_var.get(), client_filter_var.get()))


if __name__ == "__main__":
    root = tk.Tk()
    show_monthly_purchases()
    root.mainloop()
