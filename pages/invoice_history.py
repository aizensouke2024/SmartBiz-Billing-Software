
import customtkinter as ctk
from tkinter import messagebox

from invoice_pdf import generate_invoice

from database import (
    get_invoices,
    get_businesses,
    get_invoice_items,
    get_invoice_details,
    get_business_details,
    get_customers,
    move_invoice_to_trash
)


def show_invoice_details(invoice_id, parent):

    print("Opening invoice details:", invoice_id)

    try:
        items = get_invoice_items(invoice_id)

        details_window = ctk.CTkToplevel(parent.winfo_toplevel())
        details_window.title(f"Invoice Details #{invoice_id}")
        details_window.geometry("750x600")

        details_window.transient(parent.winfo_toplevel())
        details_window.lift()
        details_window.focus_force()

        title = ctk.CTkLabel(
            details_window,
            text=f"Invoice Details #{invoice_id}",
            font=("Arial", 24, "bold")
        )
        title.pack(pady=20)

        if not items:
            ctk.CTkLabel(
                details_window,
                text="No product details found for this invoice.",
                font=("Arial", 14)
            ).pack(pady=20)

            return

        details_frame = ctk.CTkScrollableFrame(
            details_window,
            width=680,
            height=400
        )
        details_frame.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=10
        )

        for item in items:

            product_text = (
                f"Product: {item['product_name']}\n"
                f"Quantity: {item['quantity']}\n"
                f"Unit Price: ₹{item['unit_price_paise'] / 100:.2f}\n"
                f"GST: {item['gst_rate']}%\n"
                f"Tax: ₹{item['tax_paise'] / 100:.2f}\n"
                f"Total: ₹{item['total_paise'] / 100:.2f}"
            )

            product_card = ctk.CTkLabel(
                details_frame,
                text=product_text,
                justify="left",
                anchor="w",
                font=("Arial", 13),
                fg_color=("#EEF5FC", "#263445"),
                corner_radius=10
            )

            product_card.pack(
                fill="x",
                padx=10,
                pady=8
            )

        pdf_button = ctk.CTkButton(
            details_window,
            text="Generate PDF",
            command=lambda: regenerate_invoice_pdf(invoice_id),
            width=220,
            height=40
        )
        pdf_button.pack(pady=15)

    except Exception as e:
        messagebox.showerror(
            "Invoice Details Error",
            str(e),
            parent=parent.winfo_toplevel()
        )


def regenerate_invoice_pdf(invoice_id):

    try:
        invoice = get_invoice_details(invoice_id)

        if invoice is None:
            messagebox.showerror(
                "Error",
                "Invoice details not found."
            )
            return

        business_id = invoice[0]
        customer_id = invoice[1]
        grand_total = invoice[2]

        business = get_business_details(business_id)

        customers = get_customers(business_id)

        customer = next(
            (c for c in customers if c[0] == customer_id),
            None
        )

        if business is None or customer is None:
            messagebox.showerror(
                "Error",
                "Business or customer details not found."
            )
            return

        items = get_invoice_items(invoice_id)

        if not items:
            messagebox.showerror(
                "Error",
                "No products found in this invoice."
            )
            return

        filename = generate_invoice(
            business,
            customer,
            items,
            grand_total
        )

        messagebox.showinfo(
            "Success",
            f"Invoice PDF generated successfully!\n\nSaved as: {filename}"
        )

    except Exception as e:
        messagebox.showerror(
            "PDF Error",
            str(e)
        )


def show_invoice_history_page(parent):

    for widget in parent.winfo_children():
        widget.destroy()

    title = ctk.CTkLabel(
        parent,
        text="Invoice History",
        font=("Arial", 28, "bold")
    )
    title.pack(pady=20)

    subtitle = ctk.CTkLabel(
        parent,
        text="View all your previously created invoices",
        font=("Arial", 14)
    )
    subtitle.pack(pady=5)

    businesses = get_businesses()

    business_options = {
        business[1]: business[0]
        for business in businesses
    }

    if not business_options:
        ctk.CTkLabel(
            parent,
            text="No businesses found.",
            font=("Arial", 16)
        ).pack(pady=20)
        return

    business_menu = ctk.CTkOptionMenu(
        parent,
        values=list(business_options.keys()),
        width=250
    )
    business_menu.pack(pady=15)

    invoice_frame = ctk.CTkScrollableFrame(
        parent,
        width=800,
        height=450
    )
    invoice_frame.pack(
        fill="both",
        expand=True,
        padx=20,
        pady=20
    )

    
    def load_invoices(selected_business=None):

        for widget in invoice_frame.winfo_children():
            widget.destroy()

        if selected_business is None:
            selected_business = business_menu.get()

        business_id = business_options.get(selected_business)

        if business_id is None:
            return

        invoices = get_invoices(business_id)

        if not invoices:
            ctk.CTkLabel(
                invoice_frame,
                text="No invoices found for this business.",
                font=("Arial", 16)
            ).pack(pady=20)
            return

        for invoice in invoices:

            invoice_card = ctk.CTkFrame(
                invoice_frame,
                corner_radius=10
            )
            invoice_card.pack(
                fill="x",
                padx=10,
                pady=8
            )

            ctk.CTkLabel(
                invoice_card,
                text=f"Invoice: {invoice[1]}",
                font=("Arial", 17, "bold")
            ).pack(anchor="w", padx=15, pady=5)

            ctk.CTkLabel(
                invoice_card,
                text=f"Date: {invoice[2]}    Customer: {invoice[3]}"
            ).pack(anchor="w", padx=15, pady=5)

            ctk.CTkLabel(
                invoice_card,
                text=f"Total: ₹{invoice[5] / 100:.2f}",
                font=("Arial", 15, "bold")
            ).pack(anchor="w", padx=15, pady=5)

            
            buttons_frame = ctk.CTkFrame(invoice_card)
            buttons_frame.pack(anchor="e", padx=15, pady=10)

            ctk.CTkButton(
                buttons_frame,
                text="View Details",
                command=lambda inv_id=invoice[0]: show_invoice_details(
                    inv_id,
                    parent
                )
            ).pack(side="left", padx=5)

            ctk.CTkButton(
                buttons_frame,
                text="Move to Trash",
                fg_color="#B83232",
                hover_color="#8F2020",
                command=lambda inv_id=invoice[0], bid=business_id:
                    delete_invoice(inv_id, bid)
            ).pack(side="left", padx=5)


    def delete_invoice(invoice_id, business_id):

        confirm = messagebox.askyesno(
            "Move Invoice to Trash",
            "Move this invoice to the Recycle Bin?\n\n"
            "You can restore it later from Settings."
        )

        if not confirm:
            return

        try:
            move_invoice_to_trash(invoice_id, business_id)

            messagebox.showinfo(
                "Success",
                "Invoice moved to Recycle Bin!"
            )

            load_invoices()

        except Exception as e:
            messagebox.showerror(
                "Error",
                str(e)
            )

    business_menu.configure(command=load_invoices)

    load_invoices()
