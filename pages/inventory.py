
import customtkinter as ctk
from database import (
    get_inventory_products,
    get_businesses,
    update_product_stock,
    add_product_stock
)
from tkinter import messagebox


def show_inventory_page(parent):

    for widget in parent.winfo_children():
        widget.destroy()

    title = ctk.CTkLabel(
        parent,
        text="Inventory Management",
        font=("Arial", 28, "bold"),
        text_color="#172B4D"
    )
    title.pack(anchor="w", pady=(10, 5))

    subtitle = ctk.CTkLabel(
        parent,
        text="Manage your product stock and inventory",
        font=("Arial", 15),
        text_color="#64748B"
    )
    subtitle.pack(anchor="w", pady=5)

    # Get all businesses
    businesses = get_businesses()

    if not businesses:
        ctk.CTkLabel(
            parent,
            text="No businesses found. Please add a business first.",
            font=("Arial", 15)
        ).pack(pady=30)
        return

    # Company selection
    business_map = {
        business[1]: business[0]
        for business in businesses
    }

    company_label = ctk.CTkLabel(
        parent,
        text="Select Company",
        font=("Arial", 16, "bold"),
        text_color="#172B4D"
    )
    company_label.pack(anchor="w", pady=(20, 5))

    table_title = ctk.CTkLabel(
        parent,
        text="Product Stock Details",
        font=("Arial", 20, "bold"),
        text_color="#172B4D"
    )
    table_title.pack(anchor="w", pady=(20, 12))

    table_frame = ctk.CTkFrame(
        parent,
        fg_color="white",
        corner_radius=12
    )
    table_frame.pack(fill="both", expand=True, pady=10)

    def edit_stock(product_id, current_stock, business_id, company_name):
        dialog = ctk.CTkInputDialog(
            title="Edit Stock",
            text=f"Enter the new stock quantity (current: {current_stock}):"
        )
        new_value = dialog.get_input()

        if new_value is None:
            return

        try:
            new_stock = int(new_value.strip())
        except (AttributeError, ValueError):
            ctk.CTkLabel(
                table_frame,
                text="Please enter a valid whole-number stock quantity.",
                text_color="#DC2626"
            ).grid(row=1, column=0, columnspan=5, pady=10)
            return

        if new_stock < 0:
            ctk.CTkLabel(
                table_frame,
                text="Stock quantity cannot be negative.",
                text_color="#DC2626"
            ).grid(row=1, column=0, columnspan=5, pady=10)
            return

        update_product_stock(product_id, business_id, new_stock)
        load_inventory(company_name)

    def load_inventory(company_name):

        for widget in table_frame.winfo_children():
            widget.destroy()

        business_id = business_map[company_name]

        products = get_inventory_products(business_id)

        headers = [
                  "Product Name",
                  "Product Code",
                  "Price",
                  " Stock",
                  "Action"
                ]
        for column, header in enumerate(headers):
            label = ctk.CTkLabel(
                table_frame,
                text=header,
                font=("Arial", 14, "bold"),
                text_color="#172B4D"
            )
            label.grid(
                row=0,
                column=column,
                padx=15,
                pady=15,
                sticky="w"
            )

        if not products:
            ctk.CTkLabel(
                table_frame,
                text="No products found for this company.",
                font=("Arial", 14),
                text_color="#64748B"
            ).grid(
                row=1,
                column=0,
                columnspan=4,
                pady=30
            )
            return

        for row_index, product in enumerate(products, start=1):

            product_id, name, code, price, stock = product

            values = [
                name,
                code or "-",
                f"₹{price / 100:,.2f}",
                stock
            ]

            for column, value in enumerate(values):
                label = ctk.CTkLabel(
                    table_frame,
                    text=str(value),
                    font=("Arial", 13),
                    text_color="#334155"
                )
                label.grid(
                    row=row_index,
                    column=column,
                    padx=15,
                    pady=12,
                    sticky="w"
                )

            # Edit Stock Button
            edit_button = ctk.CTkButton(
                table_frame,
                text="Edit Stock",
                width=90,
                command=lambda pid=product_id, s=stock: edit_stock(pid, s, business_id, company_name)
            )
            edit_button.grid(
                row=row_index,
                column=4,
                padx=10,
                pady=12
            )


    def add_stock_window():
        selected_company = company_dropdown.get()
        business_id = business_map[selected_company]

        products = get_inventory_products(business_id)

        if not products:
            messagebox.showwarning(
                "No Products",
                "Please add products first."
            )
            return

        stock_window = ctk.CTkToplevel(parent)
        stock_window.title("Add Stock")
        stock_window.geometry("400x300")
        stock_window.grab_set()

        ctk.CTkLabel(
            stock_window,
            text="Add New Stock",
            font=("Arial", 22, "bold")
        ).pack(pady=15)

        product_map = {
            f"{product[1]} ({product[2] or 'No Code'})": product[0]
            for product in products
        }

        product_dropdown = ctk.CTkOptionMenu(
            stock_window,
            values=list(product_map.keys()),
            width=250
        )
        product_dropdown.pack(pady=12)

        quantity_entry = ctk.CTkEntry(
            stock_window,
            placeholder_text="Enter quantity to add",
            width=250
        )
        quantity_entry.pack(pady=12)

        def save_stock():
            try:
                quantity = int(quantity_entry.get())

                if quantity <= 0:
                    raise ValueError

                product_id = product_map[product_dropdown.get()]

                add_product_stock(
                    business_id,
                    product_id,
                    quantity
                )

                load_inventory(company_dropdown.get())

                messagebox.showinfo(
                    "Success",
                    f"{quantity} units added successfully!"
                )
                stock_window.destroy()

            except ValueError:
                messagebox.showerror(
                    "Invalid Quantity",
                    "Enter a positive whole number."
                )
            except Exception as error:
                messagebox.showerror("Error", str(error))

        ctk.CTkButton(
            stock_window,
            text="Add Stock",
            command=save_stock,
            width=180,
            height=40
        ).pack(pady=20)

    company_dropdown = ctk.CTkOptionMenu(
        parent,
        values=list(business_map.keys()),
        command=load_inventory,
        width=250
    )
    company_dropdown.pack(anchor="w", pady=5)

    add_stock_button = ctk.CTkButton(
    parent,
    text="+ Add Stock",
    command=add_stock_window,
    width=150,
    height=38
)
    add_stock_button = ctk.CTkButton(
        parent,
        text="+ Add Stock",
        command=add_stock_window,
        width=150,
        height=38
    )
    add_stock_button.pack(anchor="w", pady=10)

    first_company = list(business_map.keys())[0]
    company_dropdown.set(first_company)
    load_inventory(first_company)