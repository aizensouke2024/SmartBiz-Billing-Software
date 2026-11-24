
from datetime import datetime, timedelta
from pathlib import Path
import sys

import customtkinter as ctk

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from database import (
    get_business_low_stock_products,
    get_business_total_customers,
    get_business_total_invoices,
    get_business_total_products,
    get_business_total_sales,
    get_recent_business_invoices,
    get_business_daily_sales,
    get_business_monthly_sales,
    get_business_last_month_sales,
    get_business_average_invoice_value,
    get_business_best_selling_product,
    get_business_month_comparison,
    get_business_last_7_days_sales,
)


def show_business_dashboard(business_id, business_name, parent):

    # Clear previous page
    for widget in parent.winfo_children():
        widget.destroy()

    # Main scrollable dashboard
    dashboard = ctk.CTkScrollableFrame(
        parent,
        orientation="vertical"
    )
    dashboard.pack(
        fill="both",
        expand=True,
        padx=5,
        pady=5
    )

    # Header
    header = ctk.CTkFrame(
        dashboard,
        fg_color="transparent"
    )
    header.pack(fill="x", padx=20, pady=(10, 5))

    ctk.CTkLabel(
        header,
        text=f"{business_name} Dashboard",
        font=("Arial", 26, "bold"),
        anchor="w"
    ).pack(side="left", padx=10)

    ctk.CTkLabel(
        header,
        text=f"Last Updated: {datetime.now().strftime('%d-%m-%Y %I:%M %p')}",
        font=("Arial", 11),
        text_color="gray"
    ).pack(side="left", padx=10)

    def go_back():
        from pages.business import show_business_page
        show_business_page(parent)

    ctk.CTkButton(
        header,
        text="Back to Businesses",
        width=160,
        command=go_back
    ).pack(side="right", padx=5)

    ctk.CTkButton(
        header,
        text="Refresh",
        width=100,
        command=lambda: show_business_dashboard(
            business_id, business_name, parent
        )
    ).pack(side="right", padx=5)

    # Summary Cards
    cards = ctk.CTkFrame(
        dashboard,
        fg_color="transparent"
    )
    cards.pack(fill="x", padx=10, pady=20)

    summary = [
        ("Total Sales", f"₹{get_business_total_sales(business_id) / 100:,.2f}", "#2563EB"),
        ("Invoices", str(get_business_total_invoices(business_id)), "#16A34A"),
        ("Customers", str(get_business_total_customers(business_id)), "#D97706"),
        ("Products", str(get_business_total_products(business_id)), "#7C3AED"),
    ]

    for title, value, accent_color in summary:

        card = ctk.CTkFrame(
            cards,
            fg_color="#FFFFFF",
            corner_radius=15,
            border_width=1,
            border_color="#E5E7EB"
        )
        card.pack(
            side="left",
            fill="both",
            expand=True,
            padx=8,
            pady=8
        )

        ctk.CTkLabel(
            card,
            text=title,
            font=("Arial", 14, "bold"),
            text_color=accent_color
        ).pack(pady=(18, 8))

        ctk.CTkLabel(
            card,
            text=value,
            font=("Arial", 26, "bold"),
            text_color="#172B4D"
        ).pack(pady=(5, 18))

    # Sales Performance Section
    performance_frame = ctk.CTkFrame(
        dashboard,
        corner_radius=15
    )
    performance_frame.pack(fill="x", padx=20, pady=15)

    ctk.CTkLabel(
        performance_frame,
        text="Sales Performance",
        font=("Arial", 20, "bold")
    ).pack(anchor="w", padx=15, pady=(15, 5))

    performance_cards = ctk.CTkFrame(
        performance_frame,
        fg_color="transparent"
    )
    performance_cards.pack(fill="x", padx=10, pady=10)

    monthly_sales_data = get_business_monthly_sales(business_id)

    current_month = datetime.now().strftime("%Y-%m")

    monthly_sales = next(
        (amount for month, amount in monthly_sales_data
         if month == current_month),
        0
    ) / 100

    last_month_sales = get_business_last_month_sales(business_id) / 100
    average_invoice = get_business_average_invoice_value(business_id) / 100

    if last_month_sales > 0:
        growth = (
            (monthly_sales - last_month_sales)
            / last_month_sales
        ) * 100

        if growth > 0:
            growth_text = f"↑ +{growth:.1f}%"
            growth_color = "#16A34A"
        elif growth < 0:
            growth_text = f"↓ {growth:.1f}%"
            growth_color = "#DC2626"
        else:
            growth_text = "— 0.0%"
            growth_color = "#6B7280"
    elif monthly_sales > 0:
        growth_text = "NEW"
        growth_color = "#16A34A"
    else:
        growth_text = "— N/A"
        growth_color = "#6B7280"

    best_product, best_quantity = get_business_best_selling_product(
        business_id
    )

    performance_data = [
        ("This Month's Sales", f"₹{monthly_sales:,.2f}", "#2563EB"),
        ("Sales Growth", growth_text, growth_color),
        ("Average Invoice", f"₹{average_invoice:,.2f}", "#D97706"),
        (
            "Best-Selling Product",
            f"{best_product} ({best_quantity})" if best_product else "No sales yet",
            "#7C3AED"
        ),
    ]

    for title, value, accent_color in performance_data:

        card = ctk.CTkFrame(
            performance_cards,
            corner_radius=12,
            border_width=1,
            border_color="#E5E7EB"
        )
        card.pack(
            side="left",
            fill="both",
            expand=True,
            padx=6,
            pady=6
        )

        ctk.CTkLabel(
            card,
            text=title,
            font=("Arial", 13, "bold"),
            text_color=accent_color
        ).pack(pady=(15, 8))

        ctk.CTkLabel(
            card,
            text=value,
            font=("Arial", 18, "bold"),
            wraplength=180
        ).pack(pady=(5, 15))

    # Chart Theme
    current_mode = ctk.get_appearance_mode()

    if current_mode == "Dark":
        chart_bg = "#2B2B2B"
        text_color = "#FFFFFF"
        grid_color = "#555555"
        line_color = "#60A5FA"
    else:
        chart_bg = "#FFFFFF"
        text_color = "#172B4D"
        grid_color = "#D1D5DB"
        line_color = "#2563EB"

    # 7-Day Sales Chart
    chart_frame = ctk.CTkFrame(
        dashboard,
        corner_radius=15
    )
    chart_frame.pack(fill="x", padx=20, pady=15)

    ctk.CTkLabel(
        chart_frame,
        text="Sales - Last 7 Days",
        font=("Arial", 18, "bold")
    ).pack(anchor="w", padx=15, pady=(12, 5))

    sales_data = get_business_daily_sales(business_id)

    today = datetime.now().date()

    dates = [
        today - timedelta(days=i)
        for i in range(6, -1, -1)
    ]

    sales_dict = {}

    for date_value, amount in sales_data:
        if hasattr(date_value, "strftime"):
            date_key = date_value.strftime("%Y-%m-%d")
        else:
            date_key = str(date_value)[:10]

        sales_dict[date_key] = amount / 100

    sales_values = [
        sales_dict.get(date.strftime("%Y-%m-%d"), 0)
        for date in dates
    ]

    date_labels = [
        date.strftime("%d %b")
        for date in dates
    ]

    figure = Figure(
    figsize=(12, 5),
    dpi=100,
    facecolor=chart_bg
)

    ax = figure.add_subplot(111)
    ax.set_facecolor(chart_bg)

    ax.plot(
        date_labels,
        sales_values,
        marker="o",
        linewidth=2,
        color=line_color,
        markerfacecolor=line_color
    )

    ax.set_ylabel("Sales (₹)", color=text_color)
    ax.tick_params(colors=text_color)

    for spine in ax.spines.values():
        spine.set_color(grid_color)

    ax.grid(
        True,
        linestyle="--",
        alpha=0.3,
        color=grid_color
    )

    ax.set_ylim(bottom=0)
    figure.tight_layout()

    canvas = FigureCanvasTkAgg(
        figure,
        master=chart_frame
    )

    canvas.draw()

    chart_widget = canvas.get_tk_widget()
    chart_widget.configure(height=350)

    chart_widget.pack(
        fill="x",
        expand=True,
        padx=15,
        pady=15
    )

    # Monthly Sales Comparison Chart
    comparison_frame = ctk.CTkFrame(
        dashboard,
        corner_radius=15
    )
    comparison_frame.pack(
        fill="x",
        padx=20,
        pady=15
    )

    ctk.CTkLabel(
        comparison_frame,
        text="Monthly Sales Comparison",
        font=("Arial", 18, "bold")
    ).pack(anchor="w", padx=15, pady=(12, 5))

    monthly_data = get_business_month_comparison(business_id)

    monthly_dict = {
        month: amount / 100
        for month, amount in monthly_data
    }

    previous_month = today.replace(day=1) - timedelta(days=1)

    month_keys = [
        previous_month.strftime("%Y-%m"),
        today.strftime("%Y-%m")
    ]

    month_labels = [
        previous_month.strftime("%b %Y"),
        today.strftime("%b %Y")
    ]

    monthly_values = [
        monthly_dict.get(month, 0)
        for month in month_keys
    ]

    figure_comparison = Figure(
        figsize=(12, 5),
        dpi=100,
        facecolor=chart_bg
    )

    ax_comparison = figure_comparison.add_subplot(111)
    ax_comparison.set_facecolor(chart_bg)

    ax_comparison.bar(
        month_labels,
        monthly_values,
        color=["#60A5FA", "#2563EB"],
        width=0.5
    )

    ax_comparison.set_ylabel(
        "Sales (₹)",
        color=text_color
    )

    ax_comparison.tick_params(colors=text_color)

    for spine in ax_comparison.spines.values():
        spine.set_color(grid_color)

    ax_comparison.grid(
        True,
        axis="y",
        linestyle="--",
        alpha=0.3,
        color=grid_color
    )

    ax_comparison.set_axisbelow(True)
    ax_comparison.set_ylim(bottom=0)

    figure_comparison.tight_layout()

    comparison_canvas = FigureCanvasTkAgg(
        figure_comparison,
        master=comparison_frame
    )

    comparison_canvas.draw()

    comparison_widget = comparison_canvas.get_tk_widget()
    comparison_widget.configure(
        width=800,
        height=320
    )

    comparison_widget.pack(
        fill="x",
        expand=True,
        padx=15,
        pady=15
    )


    # Recent Invoices
    recent_frame = ctk.CTkFrame(dashboard)
    recent_frame.pack(
        fill="x",
        padx=20,
        pady=(10, 5)
    )

    ctk.CTkLabel(
        recent_frame,
        text="Recent Invoices",
        font=("Arial", 18, "bold"),
        anchor="w"
    ).pack(fill="x", padx=12, pady=(10, 5))

    recent_invoices = get_recent_business_invoices(business_id)

    if not recent_invoices:
        ctk.CTkLabel(
            recent_frame,
            text="No invoices found."
        ).pack(pady=12)

    else:
        for invoice in recent_invoices:
            invoice_number, invoice_date, customer_name, total_paise = invoice

            ctk.CTkLabel(
                recent_frame,
                text=(
                    f"{invoice_number}  |  {invoice_date or '-'}  |  "
                    f"{customer_name or 'Walk-in Customer'}  |  "
                    f"₹{total_paise / 100:,.2f}"
                ),
                anchor="w"
            ).pack(fill="x", padx=12, pady=4)

    # Low Stock Products
    low_stock_frame = ctk.CTkFrame(dashboard)
    low_stock_frame.pack(
        fill="x",
        padx=20,
        pady=(10, 20)
    )

    ctk.CTkLabel(
        low_stock_frame,
        text="Low Stock Products (5 or fewer)",
        font=("Arial", 18, "bold"),
        anchor="w"
    ).pack(fill="x", padx=12, pady=(10, 5))

    low_stock_products = get_business_low_stock_products(business_id)

    if not low_stock_products:
        ctk.CTkLabel(
            low_stock_frame,
            text="No low-stock products."
        ).pack(pady=12)

    else:
        for product_name, stock in low_stock_products:

            if stock == 0:
                stock_status = "OUT OF STOCK"
                status_color = "red"

            elif stock <= 2:
                stock_status = "CRITICAL"
                status_color = "red"

            else:
                stock_status = "LOW STOCK"
                status_color = "orange"

            ctk.CTkLabel(
                low_stock_frame,
                text=f"{product_name}  |  Stock: {stock}  |  {stock_status}",
                anchor="w",
                text_color=status_color
            ).pack(fill="x", padx=12, pady=4)
