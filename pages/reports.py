import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import customtkinter as ctk
import csv
from tkinter import filedialog, messagebox

from database import (
    get_businesses,
    get_business_total_sales,
    get_business_total_invoices,
    get_business_total_customers,
    get_business_total_products,
    get_business_monthly_sales,
)


def show_reports_page(parent):

    for widget in parent.winfo_children():
        widget.destroy()

    ctk.CTkLabel(
        parent,
        text="Reports",
        font=("Arial", 28, "bold")
    ).pack(pady=15)

    # Company Selection
    businesses = get_businesses()

    business_names = {
        business[1]: business[0]
        for business in businesses
    }

    business_selector = ctk.CTkComboBox(
        parent,
        values=list(business_names.keys()),
        width=300
    )
    business_selector.pack(pady=10)

    if businesses:
        business_selector.set(businesses[0][1])
    else:
        business_selector.set("No businesses available")

    content = ctk.CTkFrame(parent)
    content.pack(fill="both", expand=True)

    def refresh_report(*args):
        for widget in content.winfo_children():
            widget.destroy()

        selected_name = business_selector.get()
        business_id = business_names.get(selected_name)

        if business_id is None:
            ctk.CTkLabel(
                content,
                text="No businesses available.",
                font=("Arial", 16)
            ).pack(pady=30)
            return

        # Summary cards
        summary = ctk.CTkFrame(
            content,
            fg_color="transparent"
        )
        summary.pack(fill="x", padx=20, pady=10)

        cards = [
            ("Total Sales", f"₹{get_business_total_sales(business_id) / 100:,.2f}"),
            ("Invoices", str(get_business_total_invoices(business_id))),
            ("Customers", str(get_business_total_customers(business_id))),
            ("Products", str(get_business_total_products(business_id)))
        ]

        for title, value in cards:
            card = ctk.CTkFrame(summary, corner_radius=12)
            card.pack(side="left", fill="both", expand=True, padx=5, pady=10)

            ctk.CTkLabel(
                card,
                text=title,
                font=("Arial", 14)
            ).pack(pady=5)

            ctk.CTkLabel(
                card,
                text=value,
                font=("Arial", 22, "bold")
            ).pack(pady=5)

        # Monthly Sales
        ctk.CTkLabel(
            content,
            text="Monthly Sales Report",
            font=("Arial", 20, "bold")
        ).pack(pady=15)

        monthly_data = get_business_monthly_sales(business_id)

        table = ctk.CTkScrollableFrame(
            content,
            height=200
        )
        table.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=10
        )

        monthly_heading = ctk.CTkLabel(
            table,
            text="Month                         Sales",
            font=("Arial", 16, "bold")
        )
        monthly_heading.pack(
            anchor="w",
            padx=10,
            pady=5
        )

        if monthly_data:
            for month, amount in monthly_data:
                ctk.CTkLabel(
                    table,
                    text=f"{month:<30}₹{amount / 100:,.2f}",
                    font=("Arial", 14)
                ).pack(anchor="w", padx=10, pady=2)
        else:
            ctk.CTkLabel(
                table,
                text="No sales data available.",
                font=("Arial", 14)
            ).pack(pady=20)

        # Export CSV
        def export_report():
            if not monthly_data:
                messagebox.showinfo(
                    "No Data",
                    "There is no sales data to export."
                )
                return

            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV Files", "*.csv")],
                title="Save Sales Report"
            )

            if not file_path:
                return

            try:
                with open(
                    file_path,
                    "w",
                    newline="",
                    encoding="utf-8"
                ) as file:
                    writer = csv.writer(file)
                    writer.writerow(["Month", "Sales (₹)"])

                    for month, amount in monthly_data:
                        writer.writerow([
                            month,
                            round(amount / 100, 2)
                        ])

                messagebox.showinfo(
                    "Success",
                    "Report exported successfully!"
                )

            except Exception as e:
                messagebox.showerror("Export Error", str(e))

        ctk.CTkButton(
            content,
            text="Export Sales Report (CSV)",
            command=export_report
        ).pack(pady=15)

    business_selector.configure(command=refresh_report)
    refresh_report()