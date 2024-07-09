import tkinter as tk
from tkinter import ttk
from monthly_purchases import show_monthly_purchases
from top_customers import show_top_customers_interface
from ui_config import apply_styles
from upcoming_birthdays import show_upcoming_birthdays

def open_analytics_menu(root):
    window = tk.Toplevel(root)
    window.title("Análises")
    window.geometry("400x300")

    apply_styles(window)

    main_frame = ttk.Frame(window, padding="20 20 20 20")
    main_frame.pack(fill=tk.BOTH, expand=True)

    relatorio_button = ttk.Button(main_frame, text="Relatorio Mensal", command=show_monthly_purchases, style="TButton")
    relatorio_button.pack(fill=tk.X, pady=5)

    top_clientes_button = ttk.Button(main_frame, text="Top Clientes", command=show_top_customers_interface, style="TButton")
    top_clientes_button.pack(fill=tk.X, pady=5)

    aniversarios_button = ttk.Button(main_frame, text="Próximos Aniversários",
                                     command=show_upcoming_birthdays, style="TButton")
    aniversarios_button.pack(fill=tk.X, pady=5)

    exportar_button = ttk.Button(main_frame, text="Exportar Dados para Excel",
                                 command=lambda: print("Implementar Exportação de Dados"), style="TButton")
    exportar_button.pack(fill=tk.X, pady=5)

    window.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    apply_styles(root)
    open_analytics_menu(root)
    root.mainloop()
