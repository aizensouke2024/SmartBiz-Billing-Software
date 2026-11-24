
import customtkinter as ctk
import sqlite3
from tkinter import filedialog, messagebox

from database import (
    DB_PATH,
    get_recycle_bin_items,
    restore_business,
    restore_product,
    restore_customer,
    restore_invoice,
    permanently_delete_business,
    permanently_delete_product,
    permanently_delete_customer,
    permanently_delete_invoice
)



def show_settings_page(parent):

    for widget in parent.winfo_children():
        widget.destroy()

    scroll_frame = ctk.CTkScrollableFrame(parent)
    scroll_frame.pack(fill="both", expand=True)

    parent = scroll_frame

    ctk.CTkLabel(
        parent,
        text="Settings",
        font=("Arial", 28, "bold")
    ).pack(pady=20)

    # Appearance settings
    appearance_frame = ctk.CTkFrame(parent)
    appearance_frame.pack(fill="x", padx=25, pady=10)

    ctk.CTkLabel(
        appearance_frame,
        text="Appearance",
        font=("Arial", 20, "bold")
    ).pack(anchor="w", padx=15, pady=10)

    ctk.CTkLabel(
        appearance_frame,
        text="Choose application theme"
    ).pack(anchor="w", padx=15)

    theme_menu = ctk.CTkOptionMenu(
        appearance_frame,
        values=["Light", "Dark", "System"],
        command=lambda choice: ctk.set_appearance_mode(choice)
    )
    theme_menu.pack(anchor="w", padx=15, pady=15)

    # Database backup
    backup_frame = ctk.CTkFrame(parent)
    backup_frame.pack(fill="x", padx=25, pady=10)

    ctk.CTkLabel(
        backup_frame,
        text="Database Backup",
        font=("Arial", 20, "bold")
    ).pack(anchor="w", padx=15, pady=10)

    ctk.CTkLabel(
        backup_frame,
        text="Save a copy of your SmartBiz database."
    ).pack(anchor="w", padx=15)

    def backup_database():

        file_path = filedialog.asksaveasfilename(
            defaultextension=".db",
            filetypes=[("SQLite Database", "*.db")],
            title="Save Database Backup",
            initialfile="SmartBiz_Backup.db"
        )

        if not file_path:
            return

        try:
            source = sqlite3.connect(DB_PATH)
            destination = sqlite3.connect(file_path)

            source.backup(destination)

            destination.close()
            source.close()

            messagebox.showinfo(
                "Backup Successful",
                "Database backup saved successfully!"
            )

        except Exception as e:
            messagebox.showerror(
                "Backup Error",
                str(e)
            )

    ctk.CTkButton(
        backup_frame,
        text="Backup Database",
        command=backup_database
    ).pack(anchor="w", padx=15, pady=15)

    # Software information
    info_frame = ctk.CTkFrame(parent)
    info_frame.pack(fill="x", padx=25, pady=10)

    ctk.CTkLabel(
        info_frame,
        text="Software Information",
        font=("Arial", 20, "bold")
    ).pack(anchor="w", padx=15, pady=10)

    information = [
        "Software Name: SmartBiz Billing Software",
        "Version: 1.0",
        "Database: SQLite",
        "Developed using: Python"
    ]

    for info in information:
        ctk.CTkLabel(
            info_frame,
            text=info,
            font=("Arial", 14)
        ).pack(anchor="w", padx=20, pady=5)

    # Recycle Bin
    recycle_frame = ctk.CTkFrame(parent)
    recycle_frame.pack(fill="x", padx=25, pady=10)

    ctk.CTkLabel(
        recycle_frame,
        text="Recycle Bin",
        font=("Arial", 20, "bold")
    ).pack(anchor="w", padx=15, pady=10)

    ctk.CTkLabel(
        recycle_frame,
        text="Restore deleted records or permanently delete them."
    ).pack(anchor="w", padx=15, pady=5)

    items_frame = ctk.CTkFrame(recycle_frame)
    items_frame.pack(fill="x", padx=10, pady=10)

    def refresh_recycle_bin():

        for widget in items_frame.winfo_children():
            widget.destroy()

        try:
            items = get_recycle_bin_items()

            if not items:
                ctk.CTkLabel(
                    items_frame,
                    text="Recycle Bin is empty.",
                    font=("Arial", 14)
                ).pack(pady=15)
                return

            for category, record_id, name, deleted_at in items:

                row = ctk.CTkFrame(items_frame)
                row.pack(fill="x", padx=8, pady=5)

                details = (
                    f"{category}: {name} "
                    f"(Deleted: {deleted_at})"
                )

                ctk.CTkLabel(
                    row,
                    text=details,
                    anchor="w",
                    wraplength=350
                ).pack(
                    side="left",
                    padx=10,
                    pady=10,
                    fill="x",
                    expand=True
                )

                ctk.CTkButton(
                    row,
                    text="Restore",
                    width=85,
                    command=lambda c=category, i=record_id:
                        restore_item(c, i)
                ).pack(side="left", padx=5, pady=5)

                ctk.CTkButton(
                    row,
                    text="Delete Permanently",
                    width=145,
                    fg_color="#B83232",
                    hover_color="#8F2020",
                    command=lambda c=category, i=record_id, n=name:
                        delete_item(c, i, n)
                ).pack(side="left", padx=5, pady=5)

        except Exception as e:
            messagebox.showerror(
                "Recycle Bin Error",
                str(e),
                parent=parent
            )

    def restore_item(category, record_id):

        restore_functions = {
            "Business": restore_business,
            "Product": restore_product,
            "Customer": restore_customer,
            "Invoice": restore_invoice
        }

        try:
            restore_functions[category](record_id)

            messagebox.showinfo(
                "Restored",
                f"{category} restored successfully!",
                parent=parent
            )

            refresh_recycle_bin()

        except Exception as e:
            messagebox.showerror(
                "Restore Error",
                str(e),
                parent=parent
            )

    def delete_item(category, record_id, name):

        warning = (
            f"Are you sure you want to permanently delete "
            f"{category}: {name}?\n\n"
            "This action cannot be undone."
        )

        if category == "Business":
            warning += (
                "\n\nAll related products, customers, "
                "invoices and invoice history will also be deleted."
            )

        if not messagebox.askyesno(
            "Confirm Permanent Deletion",
            warning,
            parent=parent
        ):
            return

        delete_functions = {
            "Business": permanently_delete_business,
            "Product": permanently_delete_product,
            "Customer": permanently_delete_customer,
            "Invoice": permanently_delete_invoice
        }

        try:
            # Protect customer records linked to invoice history.
            if category == "Customer":
                connection = sqlite3.connect(DB_PATH)
                try:
                    cursor = connection.cursor()
                    cursor.execute(
                        "SELECT COUNT(*) FROM invoices WHERE customer_id = ?",
                        (record_id,)
                    )
                    invoice_count = cursor.fetchone()[0]
                finally:
                    connection.close()

                if invoice_count > 0:
                    messagebox.showwarning(
                        "Customer Cannot Be Deleted",
                        "This customer is linked to invoice history. "
                        "Keep the customer record to protect your "
                        "historical invoices.",
                        parent=parent
                    )
                    return

            delete_functions[category](record_id)

            messagebox.showinfo(
                "Deleted",
                f"{category} permanently deleted.",
                parent=parent
            )

            refresh_recycle_bin()

        except Exception as e:
            messagebox.showerror(
                "Deletion Error",
                str(e),
                parent=parent
            )

    ctk.CTkButton(
        recycle_frame,
        text="Refresh Recycle Bin",
        command=refresh_recycle_bin
    ).pack(anchor="w", padx=15, pady=10)

    refresh_recycle_bin()
