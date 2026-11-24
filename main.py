import customtkinter as ctk
from database import (
    connect_db,
    create_tables,
    get_total_sales,
    get_total_invoices,
    get_total_customers,
    get_total_products,
    get_monthly_sales
)
from pages.business import show_business_page
from pages.products import show_products_page
from pages.customers import show_customers_page
from pages.billing import show_billing_page
from pages.sales_history import show_sales_history_page
from pages.invoice_history import show_invoice_history_page
from matplotlib.figure import Figure  # type: ignore[import-not-found]
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  # type: ignore[import-not-found]
from matplotlib.ticker import FuncFormatter  # type: ignore[import-not-found]
from pages.inventory import show_inventory_page
from pages.reports import show_reports_page
from pages.sales_report import show_sales_report
from pages.settings import show_settings_page

# Appearance settings
create_tables()
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class SmartBizApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("AIZEN WORLD")
        self.geometry("1100x700")
        self.minsize(900, 600)

        self.configure(fg_color=("#F4F6FA", "#111827"))

        # Main layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Create sidebar
        self.create_sidebar()

        # Create dashboard
        self.create_dashboard()

    def create_sidebar(self):

        sidebar = ctk.CTkFrame(
            self,
            width=220,
            corner_radius=0,
            fg_color=("#172B4D", "#0B1220")
        )
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)

        title = ctk.CTkLabel(
            sidebar,
            text="SmartBiz",
            font=("Arial", 26, "bold"),
            text_color="white"
        )
        title.pack(pady=30)

        buttons = [
    "Dashboard",
    "Business",
    "New Bill",
    "Products",
    "Customers",
    "Inventory",
    "Sales History",
    "Invoice History",
    "Reports",
    "Sales Report",
    "Settings"
]

        for name in buttons:

            button = ctk.CTkButton(
                sidebar,
                text=name,
                height=42,
                anchor="w",
                fg_color="transparent",
                hover_color="#29466D",
                text_color="white",
                command=lambda n=name: self.show_page(n)
            )

            button.pack(fill="x", padx=15, pady=5)

    def create_dashboard(self):

        self.content = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        self.content.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=25,
            pady=25
        )

        self.show_page("Dashboard")

    def show_page(self, page_name):

        for widget in self.content.winfo_children():
            widget.destroy()

        if page_name == "Business":
            show_business_page(self.content)
            return

        if page_name == "Products":
            show_products_page(self.content)
            return

        if page_name == "Customers":
            show_customers_page(self.content)
            return

        if page_name == "New Bill":
           show_billing_page(self.content)
           return

        if page_name == "Invoice History":
           show_invoice_history_page(self.content)
           return

        if page_name == "Sales History":
           show_sales_history_page(self.content)
           return

        if page_name == "Inventory":
            show_inventory_page(self.content)
            return

        if page_name == "Reports":
            show_reports_page(self.content)
            return

        if page_name == "Sales Report":
           show_sales_report(self.content)
           return

        if page_name == "Settings":
            show_settings_page(self.content)
            return

        heading = ctk.CTkLabel(
            self.content,
            text=page_name,
            font=("Arial", 28, "bold"),
            text_color=("#172B4D", "#F8FAFC")
        )
        heading.pack(anchor="w", pady=(10, 5))


        if page_name == "Dashboard":

            # Detect application theme
            is_dark = ctk.get_appearance_mode() == "Dark"

            bg_color = "#111827" if is_dark else "#F4F6FA"
            card_color = "#1F2937" if is_dark else "#FFFFFF"
            text_color = "#F8FAFC" if is_dark else "#172B4D"
            muted_color = "#CBD5E1" if is_dark else "#64748B"
            grid_color = "#475569" if is_dark else "#CBD5E1"
            bar_color = "#60A5FA" if is_dark else "#2563EB"

            # Welcome
            welcome = ctk.CTkLabel(
                self.content,
                text="Welcome to SmartBiz Billing Software!",
                font=("Arial", 16),
                text_color=text_color
            )
            welcome.pack(anchor="w", pady=10)

            # Summary cards
            cards_frame = ctk.CTkFrame(
                self.content,
                fg_color="transparent"
            )
            cards_frame.pack(fill="x", pady=25)

            total_sales = get_total_sales() / 100
            total_invoices = get_total_invoices()
            total_customers = get_total_customers()

            cards = [
                ("Total Sales", f"₹{total_sales:,.2f}"),
                ("Total Invoices", str(total_invoices)),
                ("Total Customers", str(total_customers)),
                ("Total Products", str(get_total_products()))
            ]

            for title, value in cards:

                card = ctk.CTkFrame(
                    cards_frame,
                    fg_color=card_color,
                    corner_radius=12
                )

                card.pack(
                    side="left",
                    expand=True,
                    fill="both",
                    padx=7
                )

                ctk.CTkLabel(
                    card,
                    text=title,
                    font=("Arial", 13),
                    text_color=muted_color
                ).pack(pady=(20, 8))

                ctk.CTkLabel(
                    card,
                    text=value,
                    font=("Arial", 23, "bold"),
                    text_color=text_color
                ).pack(pady=(0, 20))

            # Monthly Sales Overview
            chart_title = ctk.CTkLabel(
                self.content,
                text="Monthly Sales Overview",
                font=("Arial", 20, "bold"),
                text_color=text_color
            )
            chart_title.pack(anchor="w", pady=(20, 10))

            monthly_data = get_monthly_sales()

            months = [row[0] for row in monthly_data]
            sales = [row[1] / 100 for row in monthly_data]

            figure = Figure(
                figsize=(8, 3.8),
                dpi=100,
                facecolor=bg_color
            )

            ax = figure.add_subplot(111)
            ax.set_facecolor(card_color)

            if months:

                positions = list(range(len(months)))

                bars = ax.bar(
                    positions,
                    sales,
                    width=0.45,
                    color=bar_color
                )

                ax.set_xticks(positions)
                ax.set_xticklabels(months)

                for bar, amount in zip(bars, sales):
                    ax.annotate(
                        f"₹{amount:,.0f}",
                        (bar.get_x() + bar.get_width() / 2,
                         bar.get_height()),
                        ha="center",
                        va="bottom",
                        fontsize=10,
                        fontweight="bold",
                        color=text_color,
                        xytext=(0, 6),
                        textcoords="offset points"
                    )

                max_sales = max(sales)
                ax.set_ylim(
                    0,
                    max_sales * 1.25 if max_sales > 0 else 1
                )

                ax.yaxis.set_major_formatter(
                    FuncFormatter(
                        lambda value, position: f"₹{value:,.0f}"
                    )
                )

            else:

                ax.text(
                    0.5, 0.5,
                    "No sales data available yet",
                    ha="center",
                    va="center",
                    color=text_color,
                    transform=ax.transAxes
                )

            ax.set_ylabel("Sales", color=text_color)
            ax.set_xlabel("Month", color=text_color)

            ax.set_title(
                "Monthly Sales Performance",
                fontsize=14,
                fontweight="bold",
                color=text_color,
                pad=20
            )

            ax.tick_params(
                axis="both",
                colors=muted_color
            )

            ax.grid(
                axis="y",
                linestyle="--",
                color=grid_color,
                alpha=0.35
            )

            ax.set_axisbelow(True)

            for spine in ax.spines.values():
                spine.set_color(grid_color)

            figure.tight_layout()

            canvas = FigureCanvasTkAgg(
                figure,
                master=self.content
            )

            canvas.draw()

            canvas_widget = canvas.get_tk_widget()

            canvas_widget.configure(
                bg=bg_color,
                highlightthickness=0
            )

            canvas_widget.pack(
                fill="x",
                pady=10
            )

# Start application
if __name__ == "__main__":
    create_tables()

    app = SmartBizApp()
    app.mainloop()

def get_invoice_items(invoice_id):
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            product_name,
            quantity,
            unit_price_paise,
            gst_rate,
            subtotal_paise,
            tax_paise,
            total_paise
        FROM invoice_items
        WHERE invoice_id = ?
    """, (invoice_id,))

    items = cursor.fetchall()
    connection.close()

    return items
