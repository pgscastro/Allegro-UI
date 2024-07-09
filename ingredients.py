import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import os
import ui_config
import tkinter.font as tkFont

DATABASE_PATH = 'food_supplier.db'


def connect_to_db():
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        return conn
    except sqlite3.Error as e:
        messagebox.showerror("Erro de Conexão", f"Erro ao conectar-se ao banco de dados: {e}")
        return None


def add_or_update_ingredient(ingredient_name, price_per_unit, unit, quantity, tree, status_label):
    if not ingredient_name or not price_per_unit or not unit or not quantity:
        messagebox.showwarning("Erro de Entrada", "Todos os campos são obrigatórios")
        return
    try:
        price_per_unit = float(price_per_unit)
        quantity = float(quantity)
    except ValueError:
        messagebox.showwarning("Erro de Entrada", "O preço e a quantidade devem ser números")
        return

    conn = connect_to_db()
    cursor = conn.cursor()

    cursor.execute('''
    SELECT ingredient_id FROM Ingredientes WHERE ingredient_name = ?
    ''', (ingredient_name,))
    ingredient = cursor.fetchone()

    if ingredient:
        cursor.execute('''
        UPDATE Ingredientes
        SET price_per_unit = ?, unit = ?, quantity = ?, is_active = 1
        WHERE ingredient_id = ?
        ''', (price_per_unit, unit, quantity, ingredient[0]))
        messagebox.showinfo("Sucesso", "Ingrediente atualizado com sucesso!")
    else:
        cursor.execute('''
        INSERT INTO Ingredientes (ingredient_name, price_per_unit, unit, quantity) VALUES (?, ?, ?, ?)
        ''', (ingredient_name, price_per_unit, unit, quantity))
        messagebox.showinfo("Sucesso", "Ingrediente adicionado com sucesso!")

    conn.commit()
    conn.close()
    update_ingredient_list(tree)
    status_label.config(text=f"Ingrediente '{ingredient_name}' adicionado/atualizado com sucesso.")


def delete_ingredient(ingredient_id, tree, status_label):
    if not ingredient_id:
        messagebox.showwarning("Erro de Entrada", "Por favor, selecione um ingrediente para deletar")
        return

    conn = connect_to_db()
    cursor = conn.cursor()

    cursor.execute('''
    UPDATE Ingredientes
    SET is_active = 0
    WHERE ingredient_id = ?
    ''', (ingredient_id,))

    print(f"Rows affected: {cursor.rowcount}")  # Debugging statement
    conn.commit()
    conn.close()
    update_ingredient_list(tree)
    status_label.config(text=f"Ingrediente '{ingredient_id}' deletado com sucesso.")


def update_ingredient_list(tree):
    for i in tree.get_children():
        tree.delete(i)
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT ingredient_id, ingredient_name, price_per_unit, unit, quantity FROM Ingredientes WHERE is_active = 1')
    ingredients = cursor.fetchall()
    conn.close()

    for ingredient in ingredients:
        ingredient_id, name, price, unit, quantity = ingredient
        price_per_unit = price / quantity if quantity > 0 else 0
        tree.insert("", "end", iid=ingredient_id, values=(name, f"{price_per_unit:.2f}", unit, quantity))

    for col in tree["columns"]:
        max_width = max(tkFont.Font().measure(tree.set(item, col)) for item in tree.get_children())
        tree.column(col, width=max_width + 20, anchor='center')  # Center the text in columns
    for col in tree["columns"]:
        tree.heading(col, anchor='center')  # Center the heading text

    for col in tree["columns"]:
        max_width = max(tkFont.Font().measure(tree.set(item, col)) for item in tree.get_children())
        tree.column(col, width=max_width + 20)




def open_add_ingredient_window(root):
    window = tk.Toplevel(root)
    window.title("Adicionar Ingrediente")
    window.geometry("600x500")

    # Apply styles to the window
    ui_config.apply_styles(window)

    frame = ttk.Frame(window, padding="10 10 10 10")
    frame.pack(fill=tk.BOTH, expand=True)

    # Define grid layout
    frame.columnconfigure(0, weight=1)
    frame.columnconfigure(1, weight=2)

    # Labels and entries
    ttk.Label(frame, text="Nome do Ingrediente:").grid(row=0, column=0, sticky=tk.W, pady=5)
    nome_entry = ttk.Entry(frame)
    nome_entry.grid(row=0, column=1, pady=5)

    ttk.Label(frame, text="Unidade:").grid(row=1, column=0, sticky=tk.W, pady=5)
    unidade_entry = ttk.Entry(frame)
    unidade_entry.grid(row=1, column=1, pady=5)

    ttk.Label(frame, text="Preço Total:").grid(row=2, column=0, sticky=tk.W, pady=5)
    preco_total_entry = ttk.Entry(frame)
    preco_total_entry.grid(row=2, column=1, pady=5)

    ttk.Label(frame, text="Quantidade:").grid(row=3, column=0, sticky=tk.W, pady=5)
    quantidade_entry = ttk.Entry(frame)
    quantidade_entry.grid(row=3, column=1, pady=5)

    # Buttons for adding/updating and deleting ingredients
    add_button = ttk.Button(frame, text="Adicionar/Atualizar Ingrediente", command=lambda: add_ingredient(
        nome_entry.get(), unidade_entry.get(), preco_total_entry.get(), quantidade_entry.get(),
        tree, status_label))
    add_button.grid(row=4, columnspan=2, pady=10)

    delete_button = ttk.Button(frame, text="Deletar Ingrediente", command=lambda: delete_selected_ingredient(
        tree, status_label))
    delete_button.grid(row=5, columnspan=2, pady=5)

    status_label = ttk.Label(frame, text="", font=("Helvetica", 10))
    status_label.grid(row=6, columnspan=2, pady=5)

    # Treeview widget for displaying ingredients
    columns = ("Nome", "Preço por Unidade", "Unidade", "Quantidade")
    tree = ttk.Treeview(frame, columns=columns, show='headings')
    tree.heading("Nome", text="Nome")
    tree.heading("Preço por Unidade", text="Preço por Unidade")
    tree.heading("Unidade", text="Unidade")
    tree.heading("Quantidade", text="Quantidade")
    tree.grid(row=7, columnspan=2, pady=10, sticky='nsew')

    # Scrollbar for the treeview
    scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.grid(row=7, column=2, sticky='ns')

    update_ingredient_list(tree)

    def add_ingredient(nome, unidade, preco_total, quantidade, tree, status_label):
        add_or_update_ingredient(nome, preco_total, unidade, quantidade, tree, status_label)
        # Clear the input fields
        nome_entry.delete(0, tk.END)
        unidade_entry.delete(0, tk.END)
        preco_total_entry.delete(0, tk.END)
        quantidade_entry.delete(0, tk.END)

    def delete_selected_ingredient(tree, status_label):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Erro de Entrada", "Por favor, selecione um ingrediente para deletar")
            return
        # Assuming 'iid' holds the actual ID
        ingredient_id = selected[0]  # The selected item's identifier (ID)
        print(f"Selected ingredient ID: {ingredient_id}")  # Debugging statement
        delete_ingredient(ingredient_id, tree, status_label)


if __name__ == "__main__":
    root = tk.Tk()
    open_add_ingredient_window(root)
    root.mainloop()
