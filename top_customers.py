import tkinter as tk
from tkinter import ttk
import sqlite3

def show_top_customers():
    top_customers_window = tk.Toplevel()
    top_customers_window.title("Top Customers")
    top_customers_window.geometry("600x400")
    top_customers_window.minsize(600, 400)

    main_frame = ttk.Frame(top_customers_window, padding="20 20 20 20")
    main_frame.pack(fill=tk.BOTH, expand=True)

    header_label = ttk.Label(main_frame, text="Top Customers", font=("Helvetica", 18, "bold"))
    header_label.grid(row=0, column=0, pady=(0, 20))

    tree = ttk.Treeview(main_frame, columns=("Client", "Total Amount Spent"), show='headings')
    tree.heading("Client", text="Client")
    tree.heading("Total Amount Spent", text="Total Amount Spent")
    tree.grid(row=1, column=0, sticky='nsew')

    main_frame.grid_rowconfigure(1, weight=1)
    main_frame.grid_columnconfigure(0, weight=1)

    conn = sqlite3.connect('food_supplier.db')
    cursor = conn.cursor()
    cursor.execute('''
    SELECT name, total_amount_spent 
    FROM Clients 
    ORDER BY total_amount_spent DESC
    LIMIT 10
    ''')
    customers = cursor.fetchall()
    conn.close()

    for customer in customers:
        tree.insert('', tk.END, values=customer)

if __name__ == "__main__":
    root = tk.Tk()
    show_top_customers()
    root.mainloop()
