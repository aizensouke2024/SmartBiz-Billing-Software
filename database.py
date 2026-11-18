
import sqlite3
import os

# Get project folder location
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Database folder location
DB_DIR = os.path.join(BASE_DIR, "database")

# Automatically create database folder if missing
os.makedirs(DB_DIR, exist_ok=True)

# Database file location
DB_PATH = os.path.join(DB_DIR, "smartbiz.db")


# Connect to database
def connect_db():
    connection = sqlite3.connect(DB_PATH)
    return connection


# Create all database tables
def create_tables():
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS businesses (
            business_id INTEGER PRIMARY KEY AUTOINCREMENT,
            business_name TEXT NOT NULL,
            owner_name TEXT,
            phone TEXT,
            email TEXT,
            address TEXT,
            gstin TEXT
        )
    """)

    # Products table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            business_id INTEGER,
            product_name TEXT NOT NULL,
            product_code TEXT,
            price_paise INTEGER NOT NULL,
            stock INTEGER DEFAULT 0,
            gst_rate REAL DEFAULT 0
        )
    """)

    # Customers table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
            business_id INTEGER,
            customer_name TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            address TEXT,
            gstin TEXT
        )
    """)

    # Invoices table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS invoices (
            invoice_id INTEGER PRIMARY KEY AUTOINCREMENT,
            business_id INTEGER,
            customer_id INTEGER,
            invoice_number TEXT NOT NULL,
            invoice_date TEXT,
            bill_type TEXT,
            subtotal_paise INTEGER DEFAULT 0,
            discount_paise INTEGER DEFAULT 0,
            cgst_paise INTEGER DEFAULT 0,
            sgst_paise INTEGER DEFAULT 0,
            igst_paise INTEGER DEFAULT 0,
            total_paise INTEGER DEFAULT 0
        )
    """)

    # Invoice items table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS invoice_items (
            item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_id INTEGER,
            product_id INTEGER,
            product_name TEXT NOT NULL,
            quantity INTEGER DEFAULT 1,
            unit_price_paise INTEGER DEFAULT 0,
            gst_rate REAL DEFAULT 0,
            subtotal_paise INTEGER DEFAULT 0,
            tax_paise INTEGER DEFAULT 0,
            total_paise INTEGER DEFAULT 0
        )
    """)

        # Add Trash Bin support to existing tables
    tables = [
        "businesses",
        "products",
        "customers",
        "invoices"
    ]

    for table in tables:
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [column[1] for column in cursor.fetchall()]

        if "deleted_at" not in columns:
            cursor.execute(
                f"ALTER TABLE {table} ADD COLUMN deleted_at TEXT DEFAULT NULL"
            )


    connection.commit()
    connection.close()

# Add a new business
def add_business(name, owner, phone, email, address, gstin):
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO businesses
        (business_name, owner_name, phone, email, address, gstin)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (name, owner, phone, email, address, gstin))

    connection.commit()
    connection.close()


# Get all businesses
def get_businesses():
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM businesses")
    businesses = cursor.fetchall()

    connection.close()
    return businesses


# Get complete details of one business
def get_business_details(business_id):
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT business_name, owner_name, phone,
               email, address, gstin
        FROM businesses
        WHERE business_id = ?
    """, (business_id,))

    business = cursor.fetchone()

    connection.close()
    return business


# Add a new product
def add_product(business_id, name, code, price, stock, gst):
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO products
        (business_id, product_name, product_code,
         price_paise, stock, gst_rate)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (business_id, name, code, price, stock, gst))

    connection.commit()
    connection.close()


# Get products for a business
def get_products(business_id):
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT * FROM products
        WHERE business_id = ?
    """, (business_id,))

    products = cursor.fetchall()

    connection.close()
    return products


# Add a new customer
def add_customer(business_id, name, phone, email, address, gstin):
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO customers
        (business_id, customer_name, phone, email, address, gstin)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (business_id, name, phone, email, address, gstin))

    connection.commit()
    connection.close()


# Get customers for a business
def get_customers(business_id):
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT * FROM customers
        WHERE business_id = ?
    """, (business_id,))

    customers = cursor.fetchall()

    connection.close()
    return customers



def save_invoice(
    business_id,
    customer_id,
    invoice_number,
    invoice_date,
    bill_type,
    subtotal_paise,
    cgst_paise,
    sgst_paise,
    igst_paise,
    total_paise,
    items
):
    connection = connect_db()
    cursor = connection.cursor()

    try:
        # Create invoice
        cursor.execute("""
            INSERT INTO invoices (
                business_id, customer_id, invoice_number,
                invoice_date, bill_type, subtotal_paise,
                cgst_paise, sgst_paise, igst_paise, total_paise
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            business_id, customer_id, invoice_number,
            invoice_date, bill_type, subtotal_paise,
            cgst_paise, sgst_paise, igst_paise, total_paise
        ))

        invoice_id = cursor.lastrowid

        # Save invoice items and reduce stock
        for item in items:

            quantity = item["quantity"]
            product_id = item["product_id"]

            # Save invoice item
            cursor.execute("""
                INSERT INTO invoice_items (
                    invoice_id, product_id, product_name,
                    quantity, unit_price_paise, gst_rate,
                    subtotal_paise, tax_paise, total_paise
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                invoice_id,
                product_id,
                item["product_name"],
                quantity,
                item["unit_price_paise"],
                item["gst_rate"],
                item["subtotal_paise"],
                item["tax_paise"],
                item["total_paise"]
            ))

            # Reduce product stock
            cursor.execute("""
                UPDATE products
                SET stock = stock - ?
                WHERE product_id = ?
                AND business_id = ?
                AND stock >= ?
            """, (
                quantity,
                product_id,
                business_id,
                quantity
            ))

            if cursor.rowcount == 0:
                raise Exception(
                    f"Not enough stock for {item['product_name']} "
                    "or product does not belong to this company."
                )

        connection.commit()
        return invoice_id

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def get_invoices(business_id):
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            invoices.invoice_id,
            invoices.invoice_number,
            invoices.invoice_date,
            customers.customer_name,
            invoices.subtotal_paise,
            invoices.total_paise
        FROM invoices
        JOIN customers
            ON invoices.customer_id = customers.customer_id
        WHERE invoices.business_id = ?
        ORDER BY invoices.invoice_id DESC
    """, (business_id,))

    invoices = cursor.fetchall()
    connection.close()

    return invoices



if __name__ == "__main__":
    create_tables()
    print("AIZEN WORLD database created successfully!")


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

    rows = cursor.fetchall()
    connection.close()

    items = []

    for row in rows:
        items.append({
            "product_name": row[0],
            "quantity": row[1],
            "unit_price_paise": row[2],
            "gst_rate": row[3],
            "subtotal_paise": row[4],
            "tax_paise": row[5],
            "total_paise": row[6]
        })

    return items

    
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

def get_invoice_details(invoice_id):
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT business_id, customer_id, total_paise
        FROM invoices
        WHERE invoice_id = ?
    """, (invoice_id,))

    invoice = cursor.fetchone()
    connection.close()

    return invoice


def get_total_sales():
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT COALESCE(SUM(total_paise), 0)
        FROM invoices
    """)

    result = cursor.fetchone()[0]
    connection.close()

    return result


def get_total_invoices():
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("SELECT COUNT(*) FROM invoices")

    result = cursor.fetchone()[0]
    connection.close()

    return result


def get_total_customers():
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("SELECT COUNT(*) FROM customers")

    result = cursor.fetchone()[0]
    connection.close()

    return result


def get_total_products():
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("SELECT COUNT(*) FROM products")

    result = cursor.fetchone()[0]
    connection.close()

    return result


def get_monthly_sales():
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            strftime('%Y-%m', invoice_date) AS month,
            SUM(total_paise)
        FROM invoices
        WHERE invoice_date IS NOT NULL
        GROUP BY month
        ORDER BY month
    """)

    result = cursor.fetchall()
    connection.close()

    return result

def get_inventory_products(business_id):
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            product_id,
            product_name,
            product_code,
            price_paise,
            stock
        FROM products
        WHERE business_id = ?
        ORDER BY product_name ASC
    """, (business_id,))

    products = cursor.fetchall()
    connection.close()

    return products

def add_product_stock(business_id, product_id, quantity):
    connection = connect_db()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            UPDATE products
            SET stock = stock + ?
            WHERE product_id = ?
            AND business_id = ?
        """, (quantity, product_id, business_id))

        if cursor.rowcount == 0:
            raise Exception("Product not found.")

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def update_product_stock(product_id, business_id, stock):
    connection = connect_db()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            UPDATE products
            SET stock = ?
            WHERE product_id = ?
            AND business_id = ?
        """, (stock, product_id, business_id))

        if cursor.rowcount == 0:
            raise Exception("Product not found.")

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def delete_product(product_id, business_id):
    connection = connect_db()
    cursor = connection.cursor()

    try:
        # Preserve old invoice records
        cursor.execute("""
            UPDATE invoice_items
            SET product_id = NULL
            WHERE product_id = ?
        """, (product_id,))

        cursor.execute("""
            DELETE FROM products
            WHERE product_id = ?
            AND business_id = ?
        """, (product_id, business_id))

        if cursor.rowcount == 0:
            raise Exception("Product not found.")

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def update_product_details(
    product_id,
    business_id,
    name,
    code,
    price,
    gst
):
    connection = connect_db()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            UPDATE products
            SET product_name = ?,
                product_code = ?,
                price_paise = ?,
                gst_rate = ?
            WHERE product_id = ?
            AND business_id = ?
        """, (
            name,
            code,
            price,
            gst,
            product_id,
            business_id
        ))

        if cursor.rowcount == 0:
            raise Exception("Product not found.")

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def move_product_to_trash(product_id, business_id):
    connection = connect_db()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            UPDATE products
            SET deleted_at = CURRENT_TIMESTAMP
            WHERE product_id = ?
            AND business_id = ?
            AND deleted_at IS NULL
        """, (product_id, business_id))

        if cursor.rowcount == 0:
            raise Exception("Product not found.")

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def get_deleted_products():
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT product_id, business_id, product_name,
               product_code, price_paise, stock, gst_rate,
               deleted_at
        FROM products
        WHERE deleted_at IS NOT NULL
        ORDER BY deleted_at DESC
    """)

    products = cursor.fetchall()
    connection.close()
    return products


def restore_product(product_id):
    connection = connect_db()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            UPDATE products
            SET deleted_at = NULL
            WHERE product_id = ?
        """, (product_id,))

        connection.commit()

    finally:
        connection.close()