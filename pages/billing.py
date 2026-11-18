import customtkinter as ctk
from tkinter import messagebox
from database import (
    get_businesses,
    get_customers,
    get_products,
    save_invoice,
    get_business_details
)
from datetime import datetime
from invoice_pdf import generate_invoice


def show_billing_page(parent):

    # Scrollable billing page
    main_frame = ctk.CTkScrollableFrame(parent)
    main_frame.pack(fill="both", expand=True, padx=10, pady=10)

    # Page heading
    title = ctk.CTkLabel(
        main_frame,
        text="Create New Bill",
        font=("Arial", 26, "bold")
    )
    title.pack(pady=20)

    # Welcome text
    subtitle = ctk.CTkLabel(
        main_frame,
        text="Create and manage customer invoices",
        font=("Arial", 15)
    )
    subtitle.pack(pady=5)
# Business selection
    business_label = ctk.CTkLabel(
        main_frame,
        text="Select Business",
        font=("Arial", 18, "bold")
    )
    business_label.pack(pady=15)

    businesses = get_businesses()

    if not businesses:
        ctk.CTkLabel(
            main_frame,
            text="Please register a business first."
        ).pack(pady=10)
        return

    business_options = {
        business[1]: business[0] for business in businesses
    }

    business_menu = ctk.CTkOptionMenu(
        main_frame,
        values=list(business_options.keys())
    )
    business_menu.pack(pady=10)
        # Customer selection
    customer_label = ctk.CTkLabel(
        main_frame,
        text="Select Customer",
        font=("Arial", 18, "bold")
    )
    customer_label.pack(pady=15)

    customer_menu = ctk.CTkOptionMenu(
        main_frame,
        values=["Select a business first"]
    )
    customer_menu.pack(pady=10)

    # Update customers when business changes
    def update_customers(selected_business):
        business_id = business_options[selected_business]

        customers = get_customers(business_id)

        if customers:
            customer_names = [
                customer[2] for customer in customers
            ]
        else:
            customer_names = ["No customers found"]

        customer_menu.configure(values=customer_names)
        customer_menu.set(customer_names[0])

    business_menu.configure(command=update_customers)

    update_customers(business_menu.get())
        # Product selection
    product_label = ctk.CTkLabel(
        main_frame,
        text="Select Product",
        font=("Arial", 18, "bold")
    )
    product_label.pack(pady=15)

    product_menu = ctk.CTkOptionMenu(
        main_frame,
        values=["Select a business first"]
    )
    product_menu.pack(pady=10)

    # Update products when business changes
    def update_products(selected_business):
        business_id = business_options[selected_business]

        products = get_products(business_id)

        if products:
            product_names = [
                product[2] for product in products
            ]
        else:
            product_names = ["No products found"]

        product_menu.configure(values=product_names)
        product_menu.set(product_names[0])

    business_menu.configure(command=lambda selected_business: (
        update_customers(selected_business),
        update_products(selected_business)
    ))

    update_products(business_menu.get())
        # Quantity
    quantity_label = ctk.CTkLabel(
        main_frame,
        text="Enter Quantity",
        font=("Arial", 18, "bold")
    )
    quantity_label.pack(pady=15)

    quantity_entry = ctk.CTkEntry(
        main_frame,
        placeholder_text="Enter quantity",
        width=250
    )
    quantity_entry.pack(pady=10)

    # Selected products
    selected_items = []

    items_label = ctk.CTkLabel(
        main_frame,
        text="Bill Items",
        font=("Arial", 18, "bold")
    )
    items_label.pack(pady=15)

    items_display = ctk.CTkLabel(
        main_frame,
        text="No products added yet",
        justify="left"
    )
    items_display.pack(pady=10)
        
    total_label = ctk.CTkLabel(
        main_frame,
        text="Grand Total: ₹0.00",
        font=("Arial", 22, "bold")
    )
    total_label.pack(pady=15)

    # Add product to bill

    def add_to_bill():
        quantity_text = quantity_entry.get().strip()

        try:
            quantity = int(quantity_text)
            if quantity <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror(
                "Error",
                "Please enter a valid quantity."
            )
            return

        business_id = business_options[business_menu.get()]
        products = get_products(business_id)

        selected_product = next(
            (p for p in products if p[2] == product_menu.get()),
            None
        )

        if selected_product is None:
            messagebox.showerror(
                "Error",
                "Please select a valid product."
            )
            return

        if quantity > selected_product[5]:
            messagebox.showerror(
                "Error",
                "Not enough stock available."
            )
            return

        product_id = selected_product[0]
        product_name = selected_product[2]
        price = selected_product[4]
        gst_rate = selected_product[6]

        subtotal = price * quantity
        tax = subtotal * gst_rate / 100
        total = subtotal + tax

        selected_items.append({
            "product_id": product_id,
            "product_name": product_name,
            "quantity": quantity,
            "unit_price_paise": price,
            "gst_rate": gst_rate,
            "subtotal_paise": subtotal,
            "tax_paise": tax,
            "total_paise": total
        })

        display_text = ""

        for item in selected_items:
            display_text += (
                f"{item['product_name']} | "
                f"Qty: {item['quantity']} | "
                f"Subtotal: ₹{item['subtotal_paise']/100:.2f} | "
                f"GST: ₹{item['tax_paise']/100:.2f} | "
                f"Total: ₹{item['total_paise']/100:.2f}\n"
            )

        grand_total = sum(
            item["total_paise"] for item in selected_items
        )

        items_display.configure(text=display_text.strip())

        total_label.configure(
            text=f"Grand Total: ₹{grand_total/100:.2f}"
        )

        quantity_entry.delete(0, "end")

       
    add_button = ctk.CTkButton(
        main_frame,
        text="Add to Bill",
        command=add_to_bill,
        width=200
    )
    add_button.pack(pady=20)

    # Generate PDF Invoice
    def create_pdf_invoice():
        print("PDF BUTTON CLICKED!")

        if not selected_items:
            messagebox.showerror(
                "Error",
                "Please add products to the bill first."
            )
            return

        selected_business = business_menu.get()
        selected_customer = customer_menu.get()

        business_id = business_options[selected_business]

        business_data = get_business_details(business_id)

        if business_data is None:
            messagebox.showerror(
                "Error",
                "Business details not found."
            )
            return

        customers = get_customers(business_id)

        customer_data = next(
            (c for c in customers if c[2] == selected_customer),
            None
        )

        if customer_data is None:
            messagebox.showerror(
                "Error",
                "Customer details not found."
            )
            return

        grand_total = sum(item["total_paise"] for item in selected_items)

        try:
            filename = generate_invoice(
                business_data,
                customer_data,
                selected_items,
                grand_total
            )

            messagebox.showinfo(
                "Success",
                f"Invoice PDF created successfully!\n\nSaved as: {filename}"
            )

        except Exception as e:
            messagebox.showerror(
                "PDF Error",
                str(e)
            )

    def test_pdf_button():
        print("PDF BUTTON IS WORKING!")
        messagebox.showinfo(
            "Test",
            "PDF button is connected successfully!"
        )

    pdf_button = ctk.CTkButton(
        main_frame,
        text="Generate PDF Invoice",
        command=create_pdf_invoice,
        width=250,
        height=45
    )
    pdf_button.pack(pady=20)

    def save_current_bill():
        if not selected_items:
            messagebox.showerror(
                "Error",
                "Please add products before saving."
            )
            return

        business_id = business_options[business_menu.get()]

        customers = get_customers(business_id)

        selected_customer = next(
            (c for c in customers if c[2] == customer_menu.get()),
            None
        )

        if selected_customer is None:
            messagebox.showerror(
                "Error",
                "Please select a valid customer."
            )
            return

        customer_id = selected_customer[0]

        subtotal_paise = sum(
            int(round(item["subtotal_paise"]))
            for item in selected_items
        )

        total_tax = sum(
            int(round(item["tax_paise"]))
            for item in selected_items
        )

        total_paise = sum(
            int(round(item["total_paise"]))
            for item in selected_items
        )

        cgst_paise = total_tax // 2
        sgst_paise = total_tax - cgst_paise

        invoice_number = "INV-" + datetime.now().strftime(
            "%Y%m%d%H%M%S"
        )

        invoice_date = datetime.now().strftime("%Y-%m-%d")

        try:
            # Check the latest stock before saving the invoice.
            products = get_products(business_id)

            for item in selected_items:
                product = next(
                    (p for p in products if p[0] == item["product_id"]),
                    None
                )

                if product is None:
                    raise Exception(
                        f"Product not found: {item['product_name']}"
                    )

                if product[5] < item["quantity"]:
                    raise Exception(
                        f"Not enough stock for {item['product_name']}. "
                        f"Available: {product[5]}, "
                        f"Required: {item['quantity']}"
                    )

            save_invoice(
                business_id,
                customer_id,
                invoice_number,
                invoice_date,
                "GST",
                subtotal_paise,
                cgst_paise,
                sgst_paise,
                0,
                total_paise,
                selected_items
            )

            messagebox.showinfo(
                "Success",
                f"Invoice {invoice_number} saved successfully!"
            )

        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Could not save invoice: {e}"
            )

    save_button = ctk.CTkButton(
        main_frame,
        text="Save Bill",
        command=save_current_bill,
        width=200,
        height=40,
        fg_color="#2D9263"
    )

    save_button.pack(pady=20)