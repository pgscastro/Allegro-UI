import tkinter as tk
from tkinter import ttk
import sqlite3
from datetime import datetime

def show_upcoming_birthdays():
    upcoming_birthdays_window = tk.Toplevel()
    upcoming_birthdays_window.title("Upcoming Birthdays")
    upcoming_birthdays_window.geometry("600x400")
    upcoming_birthdays_window.minsize(600, 400)

    main_frame = ttk.Frame(upcoming_birthdays_window, padding="20 20 20 20")
    main_frame.pack(fill=tk.BOTH, expand=True)

    header_label = ttk.Label(main_frame, text="Upcoming Birthdays", font=("Helvetica", 18, "bold"))
    header_label.grid(row=0, column=0, pady=(0, 20))

    tree = ttk.Treeview(main_frame, columns=("Client", "Birthday"), show='headings')
    tree.heading("Client", text="Client")
    tree.heading("Birthday", text="Birthday")
    tree.grid(row=1, column=0, sticky='nsew')

    main_frame.grid_rowconfigure(1, weight=1)
    main_frame.grid_columnconfigure(0, weight=1)

    conn = sqlite3.connect('food_supplier.db')
    cursor = conn.cursor()

    today = datetime.now().strftime('%m-%d')
    cursor.execute('''
    SELECT name, birthday 
    FROM Clients 
    WHERE strftime('%m-%d', birthday) >= ? 
    ORDER BY strftime('%m-%d', birthday)
    LIMIT 10
    ''', (today,))
    birthdays = cursor.fetchall()
    conn.close()

    for birthday in birthdays:
        tree.insert('', tk.END, values=birthday)

if __name__ == "__main__":
    root = tk.Tk()
    show_upcoming_birthdays()
    root.mainloop()
