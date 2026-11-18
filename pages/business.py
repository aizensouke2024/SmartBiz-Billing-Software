import importlib
import tkinter as tk

try:
    ctk = importlib.import_module("customtkinter")
except ModuleNotFoundError:
    # Keep the page usable when the optional customtkinter package is absent.
    class _TkLabel(tk.Label):
        def __init__(self, master=None, **kwargs):
            if "text_color" in kwargs:
                kwargs["fg"] = kwargs.pop("text_color")
            super().__init__(master, **kwargs)

        def configure(self, **kwargs):
            if "text_color" in kwargs:
                kwargs["fg"] = kwargs.pop("text_color")
            super().configure(**kwargs)

    class _TkEntry(tk.Entry):
        def __init__(self, master=None, **kwargs):
            kwargs.pop("height", None)
            kwargs.pop("placeholder_text", None)
            if kwargs.get("width", 0) > 100:
                kwargs["width"] = 40
            super().__init__(master, **kwargs)

    class _TkButton(tk.Button):
        def __init__(self, master=None, **kwargs):
            if kwargs.get("width", 0) > 50:
                kwargs["width"] = 20
            if kwargs.get("height", 0) > 10:
                kwargs["height"] = 2
            super().__init__(master, **kwargs)

    class ctk:
        CTkLabel = _TkLabel
        CTkEntry = _TkEntry
        CTkButton = _TkButton

from database import add_business


def show_business_page(parent):

    # Clear previous page
    for widget in parent.winfo_children():
        widget.destroy()

    # Page heading
    heading = ctk.CTkLabel(
        parent,
        text="Business Registration",
        font=("Arial", 26, "bold")
    )
    heading.pack(pady=20)

    # Input fields
    fields = [
        "Business Name",
        "Owner Name",
        "Phone Number",
        "Email",
        "Business Address",
        "GSTIN"
    ]

    entries = {}

    for field in fields:
        label = ctk.CTkLabel(
            parent,
            text=field,
            font=("Arial", 14)
        )
        label.pack(pady=(8, 2))

        entry = ctk.CTkEntry(
            parent,
            width=350,
            height=35,
            placeholder_text="Enter " + field
        )
        entry.pack(pady=3)

        entries[field] = entry

    # Save business function
    def save_business():

        name = entries["Business Name"].get().strip()

        if not name:
            message.configure(
                text="Please enter the business name.",
                text_color="red"
            )
            return

        add_business(
            name,
            entries["Owner Name"].get(),
            entries["Phone Number"].get(),
            entries["Email"].get(),
            entries["Business Address"].get(),
            entries["GSTIN"].get()
        )

        message.configure(
            text="Business saved successfully!",
            text_color="green"
        )

        for entry in entries.values():
            entry.delete(0, "end")

    # Save button
    save_button = ctk.CTkButton(
        parent,
        text="Save Business",
        width=180,
        height=40,
        command=save_business
    )
    save_button.pack(pady=20)

    # Message
    message = ctk.CTkLabel(
        parent,
        text="",
        font=("Arial", 14)
    )
    message.pack(pady=5)