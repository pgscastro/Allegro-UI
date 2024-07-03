import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt


def export_to_excel(data):
    df = pd.DataFrame(data, columns=["Client", "Date", "Amount Spent", "Items Purchased"])
    df.to_excel('monthly_purchases.xlsx', index=False)
    tk.messagebox.showinfo("Export Successful",
                           "Monthly purchases data exported to 'monthly_purchases.xlsx' successfully!")


def show_graph(data):
    clients = [row[0] for row in data]
    amounts = [row[2] for row in data]

    plt.figure(figsize=(10, 6))
    plt.bar(clients, amounts)
    plt.xlabel('Clients')
    plt.ylabel('Amount Spent')
    plt.title('Monthly Purchases by Client')
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.show()


def show_monthly_purchases():
    def fetch_data(month, year, client_filter=""):
        conn = sqlite3.connect('food_supplier.db')
        cursor = conn.cursor()
        if client_filter:
            cursor.execute('''
            SELECT Clients.name, Purchases.purchase_date, Purchases.amount_spent, Purchases.items_purchased 
            FROM Purchases 
            JOIN Clients ON Purchases.client_id = Clients.client_id 
            WHERE strftime('%m', Purchases.purchase_date) = ? 
            AND strftime('%Y', Purchases.purchase_date) = ? 
            AND Clients.name LIKE ?
            ''', (month, year, f"%{client_filter}%"))
        else:
            cursor.execute('''
            SELECT Clients.name, Purchases.purchase_date, Purchases.amount_spent, Purchases.items_purchased 
            FROM Purchases 
            JOIN Clients ON Purchases.client_id = Clients.client_id 
            WHERE strftime('%m', Purchases.purchase_date) = ? 
            AND strftime('%Y', Purchases.purchase_date) = ?
            ''', (month, year))
        data = cursor.fetchall()
        conn.close()
        return data

    def update_treeview(data):
        for row in tree.get_children():
            tree.delete(row)
        total_amount = 0
        for purchase in data:
            tree.insert('', tk.END, values=purchase)
            total_amount += purchase[2]
        total_label.config(text=f"Total Amount Spent: ${total_amount:.2f}")

    def on_filter_change(*args):
        month = month_var.get()
        year = year_var.get()
        client_filter = client_filter_var.get()
        data = fetch_data(month, year, client_filter)
        update_treeview(data)

    def on_view_details():
        selected_item = tree.selection()
        if not selected_item:
            tk.messagebox.showwarning("No Selection", "Please select a purchase to view details.")
            return
        item = tree.item(selected_item)
        details = item['values']
        tk.messagebox.showinfo("Purchase Details",
                               f"Client: {details[0]}\nDate: {details[1]}\nAmount Spent: ${details[2]:.2f}\nItems Purchased: {details[3]}")

    monthly_purchases_window = tk.Toplevel()
    monthly_purchases_window.title("Monthly Purchases")
    monthly_purchases_window.geometry("800x600")
    monthly_purchases_window.minsize(800, 600)

    main_frame = ttk.Frame(monthly_purchases_window, padding="20 20 20 20")
    main_frame.pack(fill=tk.BOTH, expand=True)

    header_label = ttk.Label(main_frame, text="Monthly Purchases", font=("Helvetica", 18, "bold"))
    header_label.grid(row=0, column=0, columnspan=4, pady=(0, 20))

    control_frame = ttk.Frame(main_frame)
    control_frame.grid(row=1, column=0, columnspan=4, pady=(0, 20))

    ttk.Label(control_frame, text="Month:").grid(row=0, column=0, padx=5)
    month_var = tk.StringVar(value=datetime.now().strftime('%m'))
    month_combobox = ttk.Combobox(control_frame, textvariable=month_var, values=[f"{i:02d}" for i in range(1, 13)],
                                  width=5)
    month_combobox.grid(row=0, column=1, padx=5)

    ttk.Label(control_frame, text="Year:").grid(row=0, column=2, padx=5)
    year_var = tk.StringVar(value=datetime.now().strftime('%Y'))
    year_combobox = ttk.Combobox(control_frame, textvariable=year_var,
                                 values=[str(i) for i in range(2000, datetime.now().year + 1)], width=7)
    year_combobox.grid(row=0, column=3, padx=5)

    ttk.Label(control_frame, text="Client Filter:").grid(row=0, column=4, padx=5)
    client_filter_var = tk.StringVar()
    client_filter_entry = ttk.Entry(control_frame, textvariable=client_filter_var)
    client_filter_entry.grid(row=0, column=5, padx=5)

    month_var.trace_add('write', on_filter_change)
    year_var.trace_add('write', on_filter_change)
    client_filter_var.trace_add('write', on_filter_change)

    tree = ttk.Treeview(main_frame, columns=("Client", "Date", "Amount Spent", "Items Purchased"), show='headings')
    tree.heading("Client", text="Client")
    tree.heading("Date", text="Date")
    tree.heading("Amount Spent", text="Amount Spent")
    tree.heading("Items Purchased", text="Items Purchased")
    tree.grid(row=2, column=0, columnspan=4, sticky='nsew')

    main_frame.grid_rowconfigure(2, weight=1)
    main_frame.grid_columnconfigure(0, weight=1)

    total_label = ttk.Label(main_frame, text="Total Amount Spent: $0.00", font=("Helvetica", 12, "bold"))
    total_label.grid(row=3, column=0, pady=(10, 0), sticky="w")

    export_button = ttk.Button(main_frame, text="Export to Excel", command=lambda: export_to_excel(
        fetch_data(month_var.get(), year_var.get(), client_filter_var.get())))
    export_button.grid(row=3, column=1, pady=(10, 0), sticky="e")

    details_button = ttk.Button(main_frame, text="View Details", command=on_view_details)
    details_button.grid(row=3, column=2, pady=(10, 0), sticky="e")

    graph_button = ttk.Button(main_frame, text="Show Graph", command=lambda: show_graph(
        fetch_data(month_var.get(), year_var.get(), client_filter_var.get())))
    graph_button.grid(row=3, column=3, pady=(10, 0), sticky="e")

    # Initial data fetch and display
    update_treeview(fetch_data(month_var.get(), year_var.get(), client_filter_var.get()))


if __name__ == "__main__":
    root = tk.Tk()
    show_monthly_purchases()
    root.mainloop()
