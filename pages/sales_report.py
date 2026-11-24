import customtkinter as ctk
from tkinter import messagebox
from database import (
    get_businesses,
    get_business_total_sales,
    get_business_total_invoices,
    get_business_average_invoice_value,
    get_business_best_selling_product
)


def show_sales_report(parent):

    # Main scrollable frame
    report_frame = ctk.CTkScrollableFrame(parent)
    report_frame.pack(
        fill="both",
        expand=True,
        padx=10,
        pady=10
    )

    # Page heading
    heading = ctk.CTkLabel(
        report_frame,
        text="Sales Report",
        font=("Arial", 26, "bold"),
        text_color=("#172B4D", "#FFFFFF")
    )
    heading.pack(anchor="w", padx=20, pady=(20, 5))

    # Subtitle
    subtitle = ctk.CTkLabel(
        report_frame,
        text="View and analyze your business sales performance",
        font=("Arial", 14),
        text_color="gray"
    )
    subtitle.pack(anchor="w", padx=20, pady=(0, 20))

# Business Selection
    from database import get_businesses

    businesses = get_businesses()

    business_names = {
        business[1]: business[0]
        for business in businesses
    }

    business_selector = ctk.CTkComboBox(
        report_frame,
        values=list(business_names.keys()),
        width=300
    )
    business_selector.pack(
        anchor="w",
        padx=20,
        pady=10
    )    

    def update_report(selected_business=None):

        business_name = business_selector.get()

        if business_name not in business_names:
            return

        business_id = business_names[business_name]

        total_sales = get_business_total_sales(business_id) / 100

        total_invoices = get_business_total_invoices(business_id)

        average_invoice = (
            get_business_average_invoice_value(business_id) / 100
        )

        best_product, quantity = get_business_best_selling_product(
            business_id
        )

        values = [
            f"₹{total_sales:,.2f}",
            str(total_invoices),
            f"₹{average_invoice:,.2f}",
            best_product if best_product else "No Sales"
        ]

        for i, value in enumerate(values):
            cards_frame.winfo_children()[i].winfo_children()[1].configure(
                text=value
            )   

# Sales Summary Cards
    cards_frame = ctk.CTkFrame(
        report_frame,
        fg_color="transparent"
    )
    cards_frame.pack(fill="x", padx=20, pady=15)

    card_titles = [
        "Total Sales",
        "Total Invoices",
        "Average Invoice",
        "Best Selling Product"
    ]

    for i, title in enumerate(card_titles):

        card = ctk.CTkFrame(
            cards_frame,
            corner_radius=12,
            height=120
        )
        card.grid(
            row=0,
            column=i,
            padx=8,
            pady=8,
            sticky="nsew"
        )

        ctk.CTkLabel(
            card,
            text=title,
            font=("Arial", 14, "bold")
        ).pack(pady=(20, 10))

        ctk.CTkLabel(
            card,
            text="Loading...",
            font=("Arial", 20, "bold")
        ).pack(pady=5)

        cards_frame.grid_columnconfigure(
            i,
            weight=1
        )    

        business_selector.configure(
        command=update_report
    )

    if businesses:
        business_selector.set(businesses[0][1])
        update_report()        