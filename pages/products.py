import importlib

try:
    ctk = importlib.import_module("customtkinter")
except ModuleNotFoundError:
    import tkinter as tk
    from tkinter import ttk

    class StringVar(tk.StringVar):
        def __init__(self, value=""):
            super().__init__(value=value)

    class CTkLabel(tk.Label):
        def __init__(self, master=None, text="", font=None, anchor="center", **kwargs):
            if "text_color" in kwargs:
                kwargs.pop("text_color")
            super().__init__(master, text=text, font=font, anchor=anchor, **kwargs)

    class CTkEntry(tk.Entry):
        def __init__(self, master=None, width=300, placeholder_text="", **kwargs):
            super().__init__(master, width=width, **kwargs)
            self._placeholder = placeholder_text
            if placeholder_text:
                self.insert(0, placeholder_text)
                self.bind("<FocusIn>", self._clear_placeholder)
                self.bind("<FocusOut>", self._restore_placeholder)

        def _clear_placeholder(self, event=None):
            if self.get() == self._placeholder:
                self.delete(0, tk.END)

        def _restore_placeholder(self, event=None):
            if not self.get():
                self.delete(0, tk.END)
                self.insert(0, self._placeholder)

    class CTkButton(tk.Button):
        def __init__(self, master=None, text="", width=None, command=None, **kwargs):
            if "text_color" in kwargs:
                kwargs.pop("text_color")
            super().__init__(master, text=text, width=width, command=command, **kwargs)

    class CTkOptionMenu(tk.Frame):
        def __init__(self, master=None, values=None, variable=None, command=None, **kwargs):
            super().__init__(master, **kwargs)
            self._variable = variable
            self._command = command
            self._combo = ttk.Combobox(
                self,
                values=values or [],
                textvariable=self._variable,
                state="readonly"
            )
            self._combo.pack(fill="x")
            self._combo.bind("<<ComboboxSelected>>", self._on_select)

        def _on_select(self, event=None):
            if self._command is not None:
                self._command(self._variable.get())

    class CTkScrollableFrame(tk.Frame):
        def __init__(self, master=None, width=None, height=None, **kwargs):
            super().__init__(master, width=width, height=height, **kwargs)

    class _CompatCTk:
        StringVar = StringVar
        CTkLabel = CTkLabel
        CTkEntry = CTkEntry
        CTkButton = CTkButton
        CTkOptionMenu = CTkOptionMenu
        CTkScrollableFrame = CTkScrollableFrame

    ctk = _CompatCTk()

from database import (
    add_product,
    get_products,
    get_businesses,
    move_product_to_trash,
    update_product_details
)
from tkinter import messagebox


def show_products_page(parent):
    for widget in parent.winfo_children():
        widget.destroy()

    heading = ctk.CTkLabel(
        parent,
        text="Product Management",
        font=("Arial", 26, "bold")
    )
    heading.pack(pady=15)

    businesses = get_businesses()

    if not businesses:
        ctk.CTkLabel(
            parent,
            text="Please register a business first.",
            font=("Arial", 16)
        ).pack(pady=30)
        return

    business_names = {business[1]: business[0] for business in businesses}
    selected_business = ctk.StringVar(value=businesses[0][1])

    ctk.CTkLabel(
        parent,
        text="Select Business",
        font=("Arial", 14)
    ).pack(pady=5)

    ctk.CTkOptionMenu(
        parent,
        values=list(business_names.keys()),
        variable=selected_business,
        command=lambda choice: display_products()
    ).pack(pady=5)

    fields = [
        "Product Name",
        "Product Code",
        "Price (₹)",
        "Stock Quantity",
        "GST Rate (%)"
    ]

    entries = {}
    for field in fields:
        entry = ctk.CTkEntry(parent, width=300, placeholder_text=field)
        entry.pack(pady=4)
        entries[field] = entry

    message = ctk.CTkLabel(parent, text="")
    message.pack(pady=5)

    product_list = ctk.CTkScrollableFrame(parent, width=650, height=180)
    product_list.pack(fill="both", expand=True, pady=10)

    def display_products():
        for widget in product_list.winfo_children():
            widget.destroy()

        business_id = business_names[selected_business.get()]
        products = get_products(business_id)

        if not products:
            ctk.CTkLabel(
                product_list,
                text="No products added yet."
            ).pack(pady=10)
            return

        for product in products:
            price = product[4] / 100
            product_row = ctk.CTkScrollableFrame(
                product_list,
                width=600,
                height=65
            )
            product_row.pack(fill="x", padx=5, pady=3)

            ctk.CTkLabel(
                product_row,
                text=(
                    f"{product[2]} | "
                    f"Code: {product[3]} | "
                    f"Price: ₹{price:.2f} | "
                    f"Stock: {product[5]} | "
                    f"GST: {product[6]}%"
                ),
                anchor="w"
            ).pack(side="left", padx=5, pady=8)

            ctk.CTkButton(
                product_row,
                text="Edit",
                width=70,
                command=lambda p=product: edit_product_window(p)
            ).pack(side="right", padx=5, pady=5)

            ctk.CTkButton(
                product_row,
                text="Delete",
                width=80,
                fg_color="#D9534F",
                hover_color="#B52B27",
                command=lambda p=product: confirm_delete(p[0], business_id)
            ).pack(side="right", padx=5, pady=5)

    def edit_product_window(product):

        edit_window = ctk.CTkToplevel(parent)
        edit_window.title("Edit Product")
        edit_window.geometry("400x400")

        ctk.CTkLabel(
            edit_window,
            text="Edit Product Details",
            font=("Arial", 20, "bold")
        ).pack(pady=15)

        fields = [
            ("Product Name", product[2]),
            ("Product Code", product[3]),
            ("Price (₹)", str(product[4] / 100)),
            ("GST Rate (%)", str(product[6]))
        ]

        edit_entries = {}

        for field, value in fields:
            entry = ctk.CTkEntry(
                edit_window,
                width=280,
                placeholder_text=field
            )
            entry.pack(pady=7)
            entry.insert(0, value)
            edit_entries[field] = entry

        def save_changes():

            name = edit_entries["Product Name"].get().strip()
            code = edit_entries["Product Code"].get().strip()

            try:
                price = float(edit_entries["Price (₹)"].get())
                gst = float(edit_entries["GST Rate (%)"].get())

                if not name or price < 0 or gst < 0:
                    raise ValueError

            except ValueError:
                messagebox.showerror(
                    "Invalid Input",
                    "Enter a valid name, price and GST rate."
                )
                return

            business_id = business_names[selected_business.get()]

            try:
                update_product_details(
                    product[0],
                    business_id,
                    name,
                    code,
                    round(price * 100),
                    gst
                )

                messagebox.showinfo(
                    "Success",
                    "Product updated successfully!"
                )

                edit_window.destroy()
                display_products()

            except Exception as e:
                messagebox.showerror("Error", str(e))

        ctk.CTkButton(
            edit_window,
            text="Save Changes",
            command=save_changes
        ).pack(pady=15)

    def confirm_delete(product_id, business_id):
        confirm = messagebox.askyesno(
            "Move to Trash",
            "Move this product to Trash Bin?"
        )

        if not confirm:
            return

        try:
            move_product_to_trash(product_id, business_id)

            messagebox.showinfo(
                "Success",
                "Product moved to Trash Bin!"
            )

            display_products()

        except Exception as e:
            messagebox.showerror("Error", str(e))