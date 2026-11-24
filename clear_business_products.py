import shutil
from tkinter import messagebox, Tk
from database import DB_PATH, connect_db

root = Tk()
root.withdraw()

confirm = messagebox.askyesno(
    "Delete Business and Products",
    "This will permanently delete:\n\n"
    "• All businesses\n"
    "• All products\n"
    "• All customers\n"
    "• All invoices and invoice items\n\n"
    "Your SmartBiz software and database structure will remain.\n\n"
    "A backup will be created first.\n\n"
    "Are you sure?"
)

if confirm:
    try:
        # Backup database first
        shutil.copy2(DB_PATH, DB_PATH + ".backup")

        connection = connect_db()
        cursor = connection.cursor()

        try:
            cursor.execute("DELETE FROM invoice_items")
            cursor.execute("DELETE FROM invoices")
            cursor.execute("DELETE FROM customers")
            cursor.execute("DELETE FROM products")
            cursor.execute("DELETE FROM businesses")

            connection.commit()

            messagebox.showinfo(
                "Success",
                "All business and product data deleted successfully!"
            )

        except Exception:
            connection.rollback()
            raise

        finally:
            connection.close()

    except Exception as e:
        messagebox.showerror("Error", str(e))

root.destroy()