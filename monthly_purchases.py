import tkinter as tk
from tkinter import ttk
from datetime import datetime
import graph

def show_monthly_purchases():
    def plot_data():
        start_date_str = start_year_var.get() + '-' + start_month_var.get() + '-01'
        end_date_str = end_year_var.get() + '-' + end_month_var.get() + '-01'
        graph.plot_monthly_purchases(start_date_str, end_date_str, purchases_var.get(), investments_var.get(), materials_var.get(), total_var.get())

    monthly_purchases_window = tk.Toplevel()
    monthly_purchases_window.title("Compras Mensais")
    monthly_purchases_window.geometry("400x300")
    monthly_purchases_window.minsize(400, 300)

    main_frame = ttk.Frame(monthly_purchases_window, padding="20 20 20 20")
    main_frame.pack(fill=tk.BOTH, expand=True)

    header_label = ttk.Label(main_frame, text="Compras Mensais", font=("Helvetica", 18, "bold"))
    header_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

    control_frame = ttk.Frame(main_frame)
    control_frame.grid(row=1, column=0, columnspan=2, pady=(0, 20))

    ttk.Label(control_frame, text="Período Inicial:").grid(row=0, column=0, padx=5)
    start_month_var = tk.StringVar(value=datetime.now().strftime('%m'))
    start_month_combobox = ttk.Combobox(control_frame, textvariable=start_month_var, values=[f"{i:02d}" for i in range(1, 13)], width=5)
    start_month_combobox.grid(row=0, column=1, padx=5)
    start_year_var = tk.StringVar(value=datetime.now().strftime('%Y'))
    start_year_combobox = ttk.Combobox(control_frame, textvariable=start_year_var, values=[str(i) for i in range(2000, datetime.now().year + 1)], width=7)
    start_year_combobox.grid(row=0, column=2, padx=5)

    ttk.Label(control_frame, text="Período Final:").grid(row=1, column=0, padx=5)
    end_month_var = tk.StringVar(value=datetime.now().strftime('%m'))
    end_month_combobox = ttk.Combobox(control_frame, textvariable=end_month_var, values=[f"{i:02d}" for i in range(1, 13)], width=5)
    end_month_combobox.grid(row=1, column=1, padx=5)
    end_year_var = tk.StringVar(value=datetime.now().strftime('%Y'))
    end_year_combobox = ttk.Combobox(control_frame, textvariable=end_year_var, values=[str(i) for i in range(2000, datetime.now().year + 1)], width=7)
    end_year_combobox.grid(row=1, column=2, padx=5)

    purchases_var = tk.BooleanVar(value=True)
    investments_var = tk.BooleanVar(value=True)
    materials_var = tk.BooleanVar(value=True)
    total_var = tk.BooleanVar(value=True)

    check_frame = ttk.Frame(main_frame)
    check_frame.grid(row=2, column=0, columnspan=2, pady=(10, 0), sticky="ew")
    ttk.Checkbutton(check_frame, text="Compras", variable=purchases_var).pack(side=tk.LEFT)
    ttk.Checkbutton(check_frame, text="Investimentos", variable=investments_var).pack(side=tk.LEFT)
    ttk.Checkbutton(check_frame, text="Gastos com Materiais", variable=materials_var).pack(side=tk.LEFT)
    ttk.Checkbutton(check_frame, text="Total", variable=total_var).pack(side=tk.LEFT)

    plot_button = ttk.Button(main_frame, text="Plotar", command=plot_data)
    plot_button.grid(row=3, column=0, columnspan=2, pady=(10, 0))

    main_frame.grid_rowconfigure(3, weight=1)
    main_frame.grid_columnconfigure(0, weight=1)

if __name__ == "__main__":
    root = tk.Tk()
    show_monthly_purchases()
    root.mainloop()
