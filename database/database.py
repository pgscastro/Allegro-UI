import sqlite3

def initialize_database():
    conn = sqlite3.connect('food_supplier.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Ingredientes (
        ingredient_id INTEGER PRIMARY KEY,
        ingredient_name TEXT NOT NULL UNIQUE,
        price_per_unit REAL NOT NULL,
        unit TEXT NOT NULL,
        is_active INTEGER NOT NULL DEFAULT 1
    )
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Recipes (
        recipe_id INTEGER PRIMARY KEY,
        recipe_name TEXT NOT NULL,
        total_price REAL NOT NULL,
        selling_price REAL NOT NULL DEFAULT 0.0,
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
    conn.commit()
    conn.close()

def update_database_schema():
    conn = sqlite3.connect('food_supplier.db')
    cursor = conn.cursor()

    cursor.execute('PRAGMA table_info(Despesas)')
    columns = [info[1] for info in cursor.fetchall()]

    if 'expense_type' not in columns:
        cursor.execute('ALTER TABLE Despesas ADD COLUMN expense_type TEXT NOT NULL DEFAULT "General"')

    conn.commit()
    conn.close()
