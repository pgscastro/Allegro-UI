import sqlite3
from datetime import datetime, timedelta
import random

DATABASE_PATH = 'food_supplier.db'

def connect_to_db():
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        return conn
    except sqlite3.Error as e:
        print(f"Erro ao conectar-se ao banco de dados: {e}")
        return None

def create_sample_data():
    conn = connect_to_db()
    if conn is None:
        return

    cursor = conn.cursor()

    # Populate Clientes table
    cursor.execute('DELETE FROM Clientes')
    clients = [
        ('Alice Smith', '01/01/1985', '123 Maple Street'),
        ('Bob Johnson', '02/02/1970', '456 Oak Avenue'),
        ('Charlie Davis', '03/03/1995', '789 Pine Road'),
        ('Diana Miller', '04/04/1980', '101 Birch Boulevard'),
        ('Evan Wilson', '05/05/1990', '202 Cedar Lane'),
        ('Fiona Brown', '06/06/1975', '303 Elm Circle'),
        ('George Clark', '07/07/1988', '404 Spruce Drive'),
        ('Hannah Lewis', '08/08/1992', '505 Willow Court'),
        ('Ivan Walker', '09/09/1983', '606 Aspen Way'),
        ('Jane Hall', '10/10/1976', '707 Redwood Street')
    ]
    cursor.executemany('INSERT INTO Clientes (client_name, birthday, address) VALUES (?, ?, ?)', clients)

    # Populate Receitas table
    cursor.execute('DELETE FROM Receitas')
    recipes = [
        ('Spaghetti Bolognese', 12.50, 15.00),
        ('Margherita Pizza', 8.75, 10.00),
        ('Caesar Salad', 9.00, 10.50),
        ('Lasagna', 11.00, 13.00),
        ('Risotto', 13.25, 16.00),
        ('Tiramisu', 5.50, 6.50),
        ('Bruschetta', 4.50, 5.50),
        ('Carbonara', 10.50, 12.50),
        ('Minestrone Soup', 7.25, 8.50),
        ('Panna Cotta', 6.00, 7.00)
    ]
    cursor.executemany('INSERT INTO Receitas (recipe_name, selling_price, total_price) VALUES (?, ?, ?)', recipes)

    # Populate Compras table
    cursor.execute('DELETE FROM Compras')
    purchases = []
    for _ in range(50):
        client_id = random.randint(1, 10)
        purchase_date = (datetime.now() - timedelta(days=random.randint(1, 365))).strftime('%Y-%m-%d')
        total_amount = round(random.uniform(20, 200), 2)
        purchases.append((client_id, purchase_date, total_amount))
    cursor.executemany('INSERT INTO Compras (client_id, purchase_date, total_amount) VALUES (?, ?, ?)', purchases)

    # Populate Despesas table
    cursor.execute('DELETE FROM Despesas')
    expenses = [
        ('Equipment', '01/01/2023', 1500.00, 'Investimentos'),
        ('Supplies', '15/01/2023', 300.00, 'Materiais'),
        ('Marketing', '01/02/2023', 500.00, 'Investimentos'),
        ('Repairs', '20/02/2023', 250.00, 'Materiais'),
        ('Utilities', '01/03/2023', 400.00, 'Materiais'),
        ('Renovation', '10/03/2023', 2000.00, 'Investimentos'),
        ('Inventory', '01/04/2023', 1200.00, 'Materiais'),
        ('Training', '15/04/2023', 600.00, 'Investimentos'),
        ('Maintenance', '01/05/2023', 800.00, 'Materiais'),
        ('Expansion', '20/05/2023', 2500.00, 'Investimentos'),
        ('Insurance', '01/06/2023', 700.00, 'Materiais'),
        ('Consulting', '15/06/2023', 1300.00, 'Investimentos'),
        ('Licenses', '01/07/2023', 900.00, 'Materiais'),
        ('Leasing', '20/07/2023', 1800.00, 'Investimentos'),
        ('Raw Materials', '01/08/2023', 1700.00, 'Materiais'),
        ('Security', '15/08/2023', 400.00, 'Investimentos'),
        ('Office Supplies', '01/09/2023', 100.00, 'Materiais'),
        ('Software', '20/09/2023', 600.00, 'Investimentos'),
        ('Furniture', '01/10/2023', 1600.00, 'Materiais'),
        ('Legal Fees', '15/10/2023', 900.00, 'Investimentos'),
        ('Wages', '01/11/2023', 2200.00, 'Materiais'),
        ('Travel', '20/11/2023', 800.00, 'Investimentos'),
        ('Cleaning', '01/12/2023', 300.00, 'Materiais'),
        ('Advertising', '15/12/2023', 1100.00, 'Investimentos')
    ]
    cursor.executemany('INSERT INTO Despesas (description, date, amount, type) VALUES (?, ?, ?, ?)', expenses)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_sample_data()
    print("Sample data inserted successfully.")
