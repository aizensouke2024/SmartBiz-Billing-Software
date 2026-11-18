
import customtkinter as ctk
from database import get_businesses, get_invoices


def show_sales_history_page(parent):

    main_frame = ctk.CTkScrollableFrame(parent)
    main_frame.pack(fill="both", expand=True, padx=10, pady=10)

    title = ctk.CTkLabel(
        main_frame,
        text="Sales History",
        font=("Arial", 26, "bold")
    )
    title.pack(pady=20)

    subtitle = ctk.CTkLabel(
        main_frame,
        text="View all your saved invoices",
        font=("Arial", 15)
    )
    subtitle.pack(pady=5)

    businesses = get_businesses()

    if not businesses:
        ctk.CTkLabel(
            main_frame,
            text="No businesses registered."
        ).pack(pady=20)
        return

    business_options = {
        business[1]: business[0]
        for business in businesses
    }

    business_menu = ctk.CTkOptionMenu(
        main_frame,
        values=list(business_options.keys())
    )
    business_menu.pack(pady=15)

    records_frame = ctk.CTkFrame(main_frame)
    records_frame.pack(fill="x", padx=10, pady=15)

    def load_invoices(selected_business):

        for widget in records_frame.winfo_children():
            widget.destroy()

        business_id = business_options[selected_business]
        invoices = get_invoices(business_id)

        if not invoices:
            ctk.CTkLabel(
                records_frame,
                text="No invoices found."
            ).pack(pady=20)
            return

        headers = [
            "Invoice No.",
            "Date",
            "Customer",
            "Subtotal",
            "Total"
        ]

        for col, heading in enumerate(headers):
            ctk.CTkLabel(
                records_frame,
                text=heading,
                font=("Arial", 13, "bold")
            ).grid(row=0, column=col, padx=10, pady=10)

        for row, invoice in enumerate(invoices, start=1):

            values = [
                invoice[1],
                invoice[2],
                invoice[3],
                f"₹{invoice[4] / 100:.2f}",
                f"₹{invoice[5] / 100:.2f}"
            ]

            for col, value in enumerate(values):
                ctk.CTkLabel(
                    records_frame,
                    text=str(value)
                ).grid(
                    row=row,
                    column=col,
                    padx=10,
                    pady=10
                )

    business_menu.configure(command=load_invoices)

    load_invoices(business_menu.get())
