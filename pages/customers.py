
import customtkinter as ctk
from tkinter import messagebox
from database import add_customer, get_customers, get_businesses


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

    # Customer list
    customer_list = ctk.CTkLabel(
        parent,
        text="Saved Customers",
        font=("Arial", 18, "bold")
    )
    customer_list.pack(pady=15)

    customer_display = ctk.CTkLabel(
        parent,
        text="",
        justify="left"
    )
    customer_display.pack(pady=5)

    def refresh_customers():
        business_id = business_options[business_menu.get()]
        customers = get_customers(business_id)

        if customers:
            customer_text = "\n".join(
                [f"{customer[2]}  |  {customer[3] or 'No phone'}"
                 for customer in customers]
            )
        else:
            customer_text = "No customers added yet."

        customer_display.configure(text=customer_text)

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

    # Save button
    save_button = ctk.CTkButton(
        parent,
        text="Save Customer",
        command=save_customer,
        width=200
    )
    save_button.pack(pady=15)

    refresh_customers()
