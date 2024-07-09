import sqlite3
from tkinter import messagebox

from ingredients import update_ingredient_list

import sqlite3

DATABASE_PATH = 'food_supplier.db'

def connect_to_db():
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        return conn
    except sqlite3.Error as e:
        print(f"Erro ao conectar-se ao banco de dados: {e}")
        return None

def create_tables():
    conn = connect_to_db()
    if conn:
        cursor = conn.cursor()
        # Create Ingredientes table with the new 'quantity' column
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Ingredientes (
                ingredient_id INTEGER PRIMARY KEY,
                ingredient_name TEXT NOT NULL UNIQUE,
                price_per_unit REAL NOT NULL,
                unit TEXT NOT NULL,
                quantity REAL NOT NULL DEFAULT 0.0,
                is_active INTEGER NOT NULL DEFAULT 1
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Recipes (
                recipe_id INTEGER PRIMARY KEY,
                recipe_name TEXT NOT NULL,
                total_price REAL NOT NULL,
                selling_price REAL NOT NULL DEFAULT 0.0,
                mao_de_obra REAL DEFAULT 0,
                gas_agua_luz REAL DEFAULT 0,
                porcoes INTEGER DEFAULT 1,
                is_active INTEGER NOT NULL DEFAULT 1
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Recipe_Ingredients (
                recipe_id INTEGER,
                ingredient_id INTEGER,
                quantity REAL NOT NULL,
                FOREIGN KEY (recipe_id) REFERENCES Recipes (recipe_id),
                FOREIGN KEY (ingredient_id) REFERENCES Ingredientes (ingredient_id)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Clients (
                client_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                birthday DATE NOT NULL,
                address TEXT NOT NULL,
                purchases INTEGER NOT NULL DEFAULT 0,
                amount_spent_month REAL NOT NULL DEFAULT 0.0,
                total_amount_spent REAL NOT NULL DEFAULT 0.0
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Despesas (
                expense_id INTEGER PRIMARY KEY,
                description TEXT NOT NULL,
                date TEXT NOT NULL,
                amount REAL NOT NULL,
                expense_type TEXT NOT NULL
            )
        ''')

        # Check if the necessary columns exist and add them if they don't
        cursor.execute("PRAGMA table_info(Recipes)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'mao_de_obra' not in columns:
            cursor.execute("ALTER TABLE Recipes ADD COLUMN mao_de_obra REAL DEFAULT 0")
        if 'gas_agua_luz' not in columns:
            cursor.execute("ALTER TABLE Recipes ADD COLUMN gas_agua_luz REAL DEFAULT 0")
        if 'porcoes' not in columns:
            cursor.execute("ALTER TABLE Recipes ADD COLUMN porcoes INTEGER DEFAULT 1")

        cursor.execute("PRAGMA table_info(Ingredientes)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'quantity' not in columns:
            cursor.execute("ALTER TABLE Ingredientes ADD COLUMN quantity REAL NOT NULL DEFAULT 0.0")

        conn.commit()
        conn.close()

def add_ingredient_to_db(nome, unidade, preco_total, quantidade):
    conn = connect_to_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO Ingredientes (ingredient_name, price_per_unit, unit, quantity)
            VALUES (?, ?, ?, ?)
        ''', (nome, preco_total, unidade, quantidade))
        conn.commit()
        conn.close()

def add_or_update_ingredient(ingredient_name, price_per_unit, unit, quantity, ingredient_listbox, status_label):
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
    update_ingredient_list(ingredient_listbox)
    status_label.config(text=f"Ingrediente '{ingredient_name}' adicionado/atualizado com sucesso.")

def fetch_ingredients():
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute('SELECT ingredient_name, unit, price_per_unit, quantity FROM Ingredientes')
    ingredients = cursor.fetchall()
    conn.close()
    return ingredients

def display_ingredients():
    ingredients = fetch_ingredients()
    for ingredient in ingredients:
        nome, unidade, preco_total, quantidade = ingredient
        preco_por_unidade = preco_total / quantidade
        print(f"Nome: {nome}, Unidade: {unidade}, Preço Total: {preco_total}, Quantidade: {quantidade}, Preço por Unidade: {preco_por_unidade:.2f}")

def update_database_schema():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute('PRAGMA table_info(Despesas)')
    columns = [info[1] for info in cursor.fetchall()]

    if 'expense_type' not in columns:
        cursor.execute('ALTER TABLE Despesas ADD COLUMN expense_type TEXT NOT NULL DEFAULT "General"')

    conn.commit()
    conn.close()

# Ensure to run the create_tables function to set up the database schema
create_tables()
