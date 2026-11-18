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
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import FuncFormatter
from pages.inventory import show_inventory_page

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

        self.configure(fg_color="#F4F6FA")

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
            fg_color="#172B4D"
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

        heading = ctk.CTkLabel(
            self.content,
            text=page_name,
            font=("Arial", 28, "bold"),
            text_color="#172B4D"
        )
        heading.pack(anchor="w", pady=(10, 5))

        if page_name == "Dashboard":

            welcome = ctk.CTkLabel(
                self.content,
                text="Welcome to SmartBiz Billing Software!",
                font=("Arial", 16),
                text_color="#64748B"
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
                    fg_color="white",
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
                    text_color="#64748B"
                ).pack(pady=(20, 8))

                ctk.CTkLabel(
                    card,
                    text=value,
                    font=("Arial", 23, "bold"),
                    text_color="#172B4D"
                ).pack(pady=(0, 20))

            chart_title = ctk.CTkLabel(
                self.content,
                text="Monthly Sales Overview",
                font=("Arial", 20, "bold"),
                text_color="#172B4D"
            )
            chart_title.pack(anchor="w", pady=(20, 10))

            monthly_data = get_monthly_sales()

            print("Monthly Sales Data:", monthly_data)

            months = [row[0] for row in monthly_data]
            sales = [row[1] / 100 for row in monthly_data]

            figure = Figure(
                figsize=(8, 3.8),
                dpi=100,
                facecolor="#F4F6FA"
            )

            ax = figure.add_subplot(111)
            ax.set_facecolor("white")

            if months:
                positions = list(range(len(months)))

                bars = ax.bar(
                    positions,
                    sales,
                    width=0.45,
                    color="#2563EB"
                )

                ax.set_xticks(positions)
                ax.set_xticklabels(months)

                for bar, amount in zip(bars, sales):
                    ax.annotate(
                        f"₹{amount:,.0f}",
                        (bar.get_x() + bar.get_width() / 2, bar.get_height()),
                        ha="center",
                        va="bottom",
                        fontsize=10,
                        fontweight="bold",
                        xytext=(0, 6),
                        textcoords="offset points"
                    )

                    ax.set_ylim(0, max(sales) * 1.25)

                ax.yaxis.set_major_formatter(
                    FuncFormatter(lambda value, position: f"₹{value:,.0f}")
                )
            else:
                ax.text(
                    0.5, 0.5,
                    "No sales data available yet",
                    ha="center",
                    va="center",
                    transform=ax.transAxes
                )

            ax.set_ylabel("Sales")
            ax.set_xlabel("Month")
            ax.set_title(
                "Monthly Sales Performance",
                fontsize=14,
                fontweight="bold",
                pad=20
            )

            ax.grid(
                axis="y",
                linestyle="--",
                alpha=0.25
            )

            ax.set_axisbelow(True)

            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)

            figure.tight_layout()

            canvas = FigureCanvasTkAgg(
                figure,
                master=self.content
            )
            canvas.draw()
            ax.bar(months, sales, color="#2563EB")

            ax.set_ylabel("Sales (₹)")
            ax.set_xlabel("Month")
            ax.set_title("Monthly Sales Performance")

            figure.tight_layout()

            canvas = FigureCanvasTkAgg(
                figure,
                master=self.content
            )

            canvas.draw()

            canvas.get_tk_widget().pack(
                fill="x",
                pady=10
            )

        else:
            message = ctk.CTkLabel(
                self.content,
                text=f"{page_name} section will be developed soon.",
                font=("Arial", 16),
                text_color="#64748B"
            )
            message.pack(anchor="w", pady=20)


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
