import shutil
from tkinter import messagebox, Tk
from database import DB_PATH, clear_all_customers

root = Tk()
root.withdraw()

confirm = messagebox.askyesno(
    "Delete Customers",
    "Delete all customer records?\n\n"
    "Businesses and products will remain."
)

if confirm:
    try:
        shutil.copy2(DB_PATH, DB_PATH + ".backup")

        clear_all_customers()

        messagebox.showinfo(
            "Success",
            "All customer records deleted!"
        )

    except Exception as e:
        messagebox.showerror("Error", str(e))

root.destroy()