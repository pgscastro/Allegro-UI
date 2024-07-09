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

def check_schema():
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(Recipes)")
    columns = cursor.fetchall()
    conn.close()
    return columns

if __name__ == "__main__":
    create_tables()
    columns = check_schema()
    print("Recipes Table Schema:")
    for column in columns:
        print(column)
