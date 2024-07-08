import matplotlib.pyplot as plt
import sqlite3
from datetime import datetime, timedelta
import matplotlib.ticker as mticker

DATABASE_PATH = 'food_supplier.db'

def connect_to_db():
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        return conn
    except sqlite3.Error as e:
        print(f"Erro ao conectar-se ao banco de dados: {e}")
        return None

def convert_date_format(date_str):
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').strftime('%Y-%m-%d')
    except ValueError:
        return '2001-01-01'

def get_all_months(start_date, end_date):
    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')
    current = start
    months = []
    while current <= end:
        months.append(current.strftime('%Y-%m'))
        current += timedelta(days=32)
        current = current.replace(day=1)
    return months

def get_expenses(start_date, end_date):
    conn = connect_to_db()
    if conn is None:
        return []

    cursor = conn.cursor()
    query = '''
    SELECT strftime('%Y-%m', substr(date, 7, 4) || '-' || substr(date, 4, 2) || '-' || substr(date, 1, 2)) as month, type, SUM(amount) 
    FROM Despesas 
    WHERE strftime('%Y-%m', substr(date, 7, 4) || '-' || substr(date, 4, 2) || '-' || substr(date, 1, 2)) BETWEEN ? AND ?
    GROUP BY strftime('%Y-%m', substr(date, 7, 4) || '-' || substr(date, 4, 2) || '-' || substr(date, 1, 2)), type
    '''
    start_date_formatted = convert_date_format(start_date)
    end_date_formatted = convert_date_format(end_date)
    print(f"Executing query: \n{query}\nWith parameters: {start_date_formatted}, {end_date_formatted}")
    cursor.execute(query, (start_date_formatted, end_date_formatted))
    expenses = cursor.fetchall()
    conn.close()
    print(f"Expenses fetched: {expenses}")
    return expenses

def fetch_data(start_date, end_date, client_filter=""):
    conn = connect_to_db()
    if conn is None:
        return []

    cursor = conn.cursor()
    query = '''
    SELECT strftime('%Y-%m', Compras.purchase_date) as month, SUM(Compras.total_amount)
    FROM Compras 
    WHERE date(Compras.purchase_date) BETWEEN date(?) AND date(?)
    GROUP BY strftime('%Y-%m', Compras.purchase_date)
    '''
    start_date_formatted = convert_date_format(start_date)
    end_date_formatted = convert_date_format(end_date)
    params = [start_date_formatted, end_date_formatted]
    print(f"Executing query: \n{query}\nWith parameters: {params}")
    cursor.execute(query, params)
    data = cursor.fetchall()
    conn.close()
    print(f"Data fetched: {data}")
    return data

def plot_monthly_purchases(start_date, end_date, plot_purchases, plot_investments, plot_materials, plot_total):
    print(f"Plotting data from {start_date} to {end_date}")
    expenses = get_expenses(start_date, end_date)
    purchases = fetch_data(start_date, end_date)

    # Extract unique months from expenses and purchases
    all_months = sorted(set([row[0] for row in expenses] + [row[0] for row in purchases]))
    print(f"All months: {all_months}")

    # Create dictionaries for purchases and expenses
    purchase_dict = {month: 0 for month in all_months}
    investment_expense_dict = {month: 0 for month in all_months}
    material_expense_dict = {month: 0 for month in all_months}

    for month, amount in purchases:
        purchase_dict[month] = amount

    for month, type_, amount in expenses:
        if type_ == 'Investimentos':
            investment_expense_dict[month] = amount
        elif type_ == 'Materiais':
            material_expense_dict[month] = amount

    # Calculate total expenses and net values
    total_expenses = {month: investment_expense_dict[month] + material_expense_dict[month] for month in all_months}
    net_values = {month: purchase_dict[month] - total_expenses[month] for month in all_months}

    # Plotting
    fig, ax = plt.subplots(figsize=(10, 6))

    if plot_purchases:
        purchase_amounts = [purchase_dict[month] for month in all_months]
        print(f"Purchase amounts: {purchase_amounts}")
        ax.plot(all_months, purchase_amounts, color='green', label='Compras')

    if plot_investments:
        investment_amounts = [investment_expense_dict[month] for month in all_months]
        print(f"Investment amounts: {investment_amounts}")
        ax.plot(all_months, investment_amounts, color='orange', label='Investimentos')

    if plot_materials:
        material_amounts = [material_expense_dict[month] for month in all_months]
        print(f"Material amounts: {material_amounts}")
        ax.plot(all_months, material_amounts, color='purple', label='Gastos com Materiais')

    if plot_investments and plot_materials:
        total_expenses_amounts = [total_expenses[month] for month in all_months]
        print(f"Total expenses: {total_expenses_amounts}")
        ax.plot(all_months, total_expenses_amounts, color='red', label='Total Despesas')

    if plot_total:
        net_values_amounts = [net_values[month] for month in all_months]
        print(f"Net values: {net_values_amounts}")
        ax.plot(all_months, net_values_amounts, color='yellow', label='Total', marker='o')

    ax.set_xlabel('Meses')
    ax.set_ylabel('Receita')
    ax.set_title('Compras Mensais e Despesas')
    ax.legend()

    # Format the y-axis as currency
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, pos: f'R${x:,.2f}'))

    plt.show()
