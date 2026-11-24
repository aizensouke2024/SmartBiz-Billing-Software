
import customtkinter as ctk
from tkinter import messagebox

from database import (
    add_customer,
    get_customers,
    get_businesses,
    move_customer_to_trash
)


def show_customers_page(parent):

    main_frame = ctk.CTkScrollableFrame(parent)
    main_frame.pack(fill="both", expand=True, padx=10, pady=10)

    parent = main_frame

    # Page heading
    title = ctk.CTkLabel(
        parent,
        text="Customer Management",
        font=("Arial", 26, "bold")
    )
    title.pack(pady=20)

    # Get registered businesses
    businesses = get_businesses()

    if not businesses:
        ctk.CTkLabel(
            parent,
            text="Please register a business first.",
            font=("Arial", 16)
        ).pack(pady=20)
        return

    # Business selection
    ctk.CTkLabel(parent, text="Select Business").pack(pady=5)

    business_options = {
        business[1]: business[0] for business in businesses
    }

    business_menu = ctk.CTkOptionMenu(
        parent,
        values=list(business_options.keys())
    )
    business_menu.pack(pady=5)

    # Customer name
    ctk.CTkLabel(parent, text="Customer Name").pack(pady=5)

    name_entry = ctk.CTkEntry(
        parent,
        placeholder_text="Enter customer name",
        width=300
    )
    name_entry.pack(pady=5)

    # Phone
    ctk.CTkLabel(parent, text="Phone Number").pack(pady=5)

    phone_entry = ctk.CTkEntry(
        parent,
        placeholder_text="Enter phone number",
        width=300
    )
    phone_entry.pack(pady=5)

    # Email
    ctk.CTkLabel(parent, text="Email").pack(pady=5)

    email_entry = ctk.CTkEntry(
        parent,
        placeholder_text="Enter email",
        width=300
    )
    email_entry.pack(pady=5)

    # Address
    ctk.CTkLabel(parent, text="Address").pack(pady=5)

    address_entry = ctk.CTkEntry(
        parent,
        placeholder_text="Enter address",
        width=300
    )
    address_entry.pack(pady=5)

    # GSTIN
    ctk.CTkLabel(parent, text="GSTIN (Optional)").pack(pady=5)

    gstin_entry = ctk.CTkEntry(
        parent,
        placeholder_text="Enter GSTIN",
        width=300
    )
    gstin_entry.pack(pady=5)

    # Customer list heading
    customer_list = ctk.CTkLabel(
        parent,
        text="Saved Customers",
        font=("Arial", 18, "bold")
    )
    customer_list.pack(pady=15)

    # Frame containing customer rows
    customer_rows_frame = ctk.CTkFrame(parent)
    customer_rows_frame.pack(fill="x", padx=10, pady=5)

    # Refresh customers
    def refresh_customers():

        for widget in customer_rows_frame.winfo_children():
            widget.destroy()

        business_id = business_options[business_menu.get()]
        customers = get_customers(business_id)

        if not customers:
            ctk.CTkLabel(
                customer_rows_frame,
                text="No customers added yet."
            ).pack(pady=15)
            return

        for customer in customers:

            customer_id = customer[0]
            customer_name = customer[2]
            customer_phone = customer[3] or "No phone"

            row = ctk.CTkFrame(customer_rows_frame)
            row.pack(fill="x", padx=8, pady=5)

            ctk.CTkLabel(
                row,
                text=f"{customer_name} | {customer_phone}",
                anchor="w"
            ).pack(
                side="left",
                padx=10,
                pady=10,
                fill="x",
                expand=True
            )

            ctk.CTkButton(
                row,
                text="Move to Trash",
                width=120,
                fg_color="#B83232",
                hover_color="#8F2020",
                command=lambda cid=customer_id, bid=business_id:
                    delete_customer(cid, bid)
            ).pack(side="right", padx=10, pady=5)

    # Move customer to Trash
    def delete_customer(customer_id, business_id):

        confirm = messagebox.askyesno(
            "Move to Trash",
            "Move this customer to the Recycle Bin?"
        )

        if not confirm:
            return

        try:
            move_customer_to_trash(customer_id, business_id)

            messagebox.showinfo(
                "Success",
                "Customer moved to Recycle Bin."
            )

            refresh_customers()

        except Exception as e:
            messagebox.showerror(
                "Error",
                str(e)
            )

    # Save customer
    def save_customer():

        name = name_entry.get().strip()

        if not name:
            messagebox.showerror(
                "Error",
                "Please enter customer name."
            )
            return

        business_id = business_options[business_menu.get()]

        try:
            add_customer(
                business_id,
                name,
                phone_entry.get().strip(),
                email_entry.get().strip(),
                address_entry.get().strip(),
                gstin_entry.get().strip()
            )

            messagebox.showinfo(
                "Success",
                "Customer saved successfully!"
            )

            name_entry.delete(0, "end")
            phone_entry.delete(0, "end")
            email_entry.delete(0, "end")
            address_entry.delete(0, "end")
            gstin_entry.delete(0, "end")

            refresh_customers()

        except Exception as e:
            messagebox.showerror(
                "Error",
                str(e)
            )

    # Save button
    save_button = ctk.CTkButton(
        parent,
        text="Save Customer",
        command=save_customer,
        width=200
    )
    save_button.pack(pady=15)

    # Refresh list when business changes
    business_menu.configure(command=lambda choice: refresh_customers())

    refresh_customers()
