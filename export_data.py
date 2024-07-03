import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import pandas as pd

def export_data_to_excel():
    conn = sqlite3.connect('food_supplier.db')

    # Export Clients
    clients_df = pd.read_sql_query('SELECT * FROM Clients', conn)
    clients_df.to_excel('clients.xlsx', index=False)

    # Export Purchases
    purchases_df = pd.read_sql_query('SELECT * FROM Purchases', conn)
    purchases_df.to_excel('purchases.xlsx', index=False)

    conn.close()
    messagebox.showinfo("Export Data", "Data exported to Excel successfully!")

if __name__ == "__main__":
    root = tk.Tk()
    export_data_to_excel()
    root.mainloop()
