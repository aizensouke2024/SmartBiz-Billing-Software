import os
import shutil
from tkinter import messagebox, Tk
from database import DB_PATH, clear_sales_and_invoice_history

root = Tk()
root.withdraw()

confirm = messagebox.askyesno(
    "Clear History",
    "This will permanently delete all invoices and sales history.\n\n"
    "Businesses, customers, products and stock will remain.\n\n"
    "Continue?"
)

if confirm:
    try:
        # Create a backup first
        backup_path = DB_PATH + ".backup"

        shutil.copy2(DB_PATH, backup_path)

        # Delete invoice and sales history
        clear_sales_and_invoice_history()

        messagebox.showinfo(
            "Success",
            "Invoice and sales history cleared!\n\n"
            "A database backup was also created."
        )

    except Exception as e:
        messagebox.showerror("Error", str(e))

root.destroy()