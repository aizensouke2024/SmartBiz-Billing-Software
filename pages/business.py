
import customtkinter as ctk
from tkinter import messagebox
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
from database import (
    add_business,
    get_businesses,
    move_business_to_trash,
    update_business
)
from pages.business_dashboard import show_business_dashboard


def show_business_page(parent):

    # Keep the original main content frame
    page_parent = parent

    # Clear previous page
    for widget in page_parent.winfo_children():
        widget.destroy()

    # Create scrollable page
    scroll_frame = ctk.CTkScrollableFrame(
        parent,
        fg_color="transparent"
    )
    scroll_frame.pack(
        fill="both",
        expand=True,
        padx=0,
        pady=0
    )

    parent = scroll_frame

    # Page heading
    heading = ctk.CTkLabel(
        parent,
        text="Business Registration",
        font=("Arial", 26, "bold")
    )
    heading.pack(pady=20)

    # Input fields
    fields = [
        "Business Name",
        "Owner Name",
        "Phone Number",
        "Email",
        "Business Address",
        "GSTIN"
    ]

    entries = {}

    for field in fields:
        ctk.CTkLabel(
            parent,
            text=field,
            font=("Arial", 14)
        ).pack(pady=(8, 2))

        entry = ctk.CTkEntry(
            parent,
            width=350,
            height=35,
            placeholder_text="Enter " + field
        )
        entry.pack(pady=3)

        entries[field] = entry

    # Message
    message = ctk.CTkLabel(
        parent,
        text="",
        font=("Arial", 14)
    )
    message.pack(pady=5)

    # Registered businesses heading
    ctk.CTkLabel(
        parent,
        text="Registered Businesses",
        font=("Arial", 20, "bold")
    ).pack(pady=15)


    # Business search box
    search_frame = ctk.CTkFrame(parent)
    search_frame.pack(fill="x", padx=20, pady=5)

    search_entry = ctk.CTkEntry(
        search_frame,
        placeholder_text="Search business or owner name...",
        width=300
    )
    search_entry.pack(side="left", padx=10, pady=10)

    ctk.CTkButton(
        search_frame,
        text="Search",
        width=90,
        command=lambda: refresh_businesses()
    ).pack(side="left", padx=5)

    ctk.CTkButton(
        search_frame,
        text="Clear",
        width=90,
        command=lambda: clear_search()
    ).pack(side="left", padx=5)


    business_list_frame = ctk.CTkFrame(parent)
    business_list_frame.pack(
        fill="x",
        padx=20,
        pady=10
    )

    # View business information
    def view_business_info(business):
        info_window = ctk.CTkToplevel(parent)
        info_window.title("Business Information")
        info_window.geometry("450x500")
        info_window.resizable(False, False)

        # Scrollable information area
        scroll_frame = ctk.CTkScrollableFrame(info_window)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

        info_window.transient(parent.winfo_toplevel())
        info_window.grab_set()

        ctk.CTkLabel(
            scroll_frame,
            text="Business Information",
            font=("Arial", 23, "bold")
        ).pack(pady=20)

        details = [
            ("Business Name", business[1]),
            ("Owner Name", business[2] or "Not provided"),
            ("Phone Number", business[3] or "Not provided"),
            ("Email", business[4] or "Not provided"),
            ("Business Address", business[5] or "Not provided"),
            ("GSTIN", business[6] or "Not provided")
        ]

        for label, value in details:

            row = ctk.CTkFrame(scroll_frame)
            row.pack(fill="x", padx=20, pady=5)

            ctk.CTkLabel(
                row,
                text=label + ":",
                font=("Arial", 13, "bold"),
                width=140,
                anchor="w"
            ).pack(side="left", padx=8, pady=8)

            ctk.CTkLabel(
                row,
                text=str(value),
                font=("Arial", 13),
                wraplength=230,
                anchor="w",
                justify="left"
            ).pack(side="left", padx=5, pady=8)

        ctk.CTkButton(
            info_window,
            text="Close",
            width=120,
            command=info_window.destroy
        ).pack(pady=15)


    # Edit business information
    def edit_business(business):

        edit_window = ctk.CTkToplevel(parent)
        edit_window.title("Edit Business")
        edit_window.geometry("450x600")
        edit_window.transient(parent.winfo_toplevel())
        edit_window.grab_set()

        ctk.CTkLabel(
            edit_window,
            text="Edit Business Details",
            font=("Arial", 22, "bold")
        ).pack(pady=15)

        fields = [
            "Business Name",
            "Owner Name",
            "Phone Number",
            "Email",
            "Business Address",
            "GSTIN"
        ]

        values = [
            business[1],
            business[2] or "",
            business[3] or "",
            business[4] or "",
            business[5] or "",
            business[6] or ""
        ]

        edit_entries = {}

        for field, value in zip(fields, values):

            ctk.CTkLabel(
                edit_window,
                text=field
            ).pack(pady=(8, 2))

            entry = ctk.CTkEntry(
                edit_window,
                width=320
            )
            entry.pack(pady=3)
            entry.insert(0, value)

            edit_entries[field] = entry

        def save_changes():

            name = edit_entries["Business Name"].get().strip()

            if not name:
                messagebox.showerror(
                    "Error",
                    "Business name cannot be empty."
                )
                return

            try:
                success = update_business(
                    business[0],
                    name,
                    edit_entries["Owner Name"].get(),
                    edit_entries["Phone Number"].get(),
                    edit_entries["Email"].get(),
                    edit_entries["Business Address"].get(),
                    edit_entries["GSTIN"].get()
                )

                if success:
                    messagebox.showinfo(
                        "Success",
                        "Business details updated successfully!"
                    )

                    edit_window.destroy()
                    refresh_businesses()

                else:
                    messagebox.showerror(
                        "Error",
                        "Business could not be updated."
                    )

            except Exception as e:
                messagebox.showerror("Error", str(e))

        ctk.CTkButton(
            edit_window,
            text="Save Changes",
            width=180,
            command=save_changes
        ).pack(pady=20)


    # Move business to Trash
    def delete_business(business_id, business_name):

        confirm = messagebox.askyesno(
            "Move Business to Trash",
            f"Move '{business_name}' to the Recycle Bin?\n\n"
            "Its active products, customers and invoices "
            "will also move to the Recycle Bin.\n\n"
            "You can restore them later from Settings."
        )

        if not confirm:
            return

        try:
            move_business_to_trash(business_id)

            messagebox.showinfo(
                "Success",
                "Business moved to Recycle Bin."
            )

            refresh_businesses()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    # Save a newly registered business
    def save_business():
        name = entries["Business Name"].get().strip()

        if not name:
            messagebox.showerror("Error", "Business name cannot be empty.")
            return

        try:
            add_business(
                name,
                entries["Owner Name"].get().strip(),
                entries["Phone Number"].get().strip(),
                entries["Email"].get().strip(),
                entries["Business Address"].get().strip(),
                entries["GSTIN"].get().strip()
            )

            for entry in entries.values():
                entry.delete(0, "end")

            message.configure(text="Business registered successfully.")
            refresh_businesses()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def clear_search():
        search_entry.delete(0, "end")
        refresh_businesses()

    # Refresh business list
    def refresh_businesses():

        # Clear old rows
        for widget in business_list_frame.winfo_children():
            widget.destroy()

        search_text = search_entry.get().strip().lower()

        businesses = get_businesses()

        # Search by business name or owner name
        if search_text:
            businesses = [
                business for business in businesses
                if search_text in str(business[1] or "").lower()
                or search_text in str(business[2] or "").lower()
            ]

        # If no businesses are found
        if not businesses:

            if search_text:
                text = "No matching businesses found."
            else:
                text = "No businesses registered yet."

            ctk.CTkLabel(
                business_list_frame,
                text=text,
                font=("Arial", 14)
            ).pack(pady=15)

            return

        # Display businesses
        for business in businesses:

            business_id = business[0]
            business_name = business[1]
            owner_name = business[2] or "No owner name"

            row = ctk.CTkFrame(business_list_frame)
            row.pack(fill="x", padx=8, pady=5)

            # Business name
            ctk.CTkLabel(
                row,
                text=f"{business_name} | Owner: {owner_name}",
                anchor="w"
            ).pack(
                side="left",
                padx=10,
                pady=10,
                fill="x",
                expand=True
            )

            # Dashboard
            ctk.CTkButton(
                row,
                text="Dashboard",
                width=100,
                fg_color="#16805D",
                hover_color="#105C43",
                command=lambda bid=business_id, name=business_name:
                show_business_dashboard(bid, name, page_parent)
            ).pack(side="right", padx=5, pady=5)

            # View Info
            ctk.CTkButton(
                row,
                text="View Info",
                width=100,
                command=lambda b=business:
                    view_business_info(b)
            ).pack(side="right", padx=5, pady=5)

            # Edit Business
            ctk.CTkButton(
                row,
                text="Edit Business",
                width=110,
                fg_color="#2463A6",
                hover_color="#174477",
                command=lambda b=business:
                    edit_business(b)
            ).pack(side="right", padx=5, pady=5)

            # Move to Trash
            ctk.CTkButton(
                row,
                text="Move to Trash",
                width=120,
                fg_color="#B83232",
                hover_color="#8F2020",
                command=lambda bid=business_id, name=business_name:
                    delete_business(bid, name)
            ).pack(side="right", padx=5, pady=5)

    # Save button
    ctk.CTkButton(
        parent,
        text="Save Business",
        width=180,
        height=40,
        command=save_business
    ).pack(pady=15)

    # Initial business list
    refresh_businesses()
