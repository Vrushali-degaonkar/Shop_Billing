import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

DB_NAME = "shop.db"


class ShopBillingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Shop Billing Management System")
        self.root.geometry("1050x680")
        self.root.minsize(900, 600)
        self.cart = []

        self.setup_database()
        self.build_ui()
        self.refresh_products()
        self.refresh_product_dropdown()
        self.refresh_sales()
        self.update_dashboard()

    def connect(self):
        return sqlite3.connect(DB_NAME)

    def setup_database(self):
        with self.connect() as con:
            cur = con.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    price REAL NOT NULL,
                    stock INTEGER NOT NULL
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS sales (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer TEXT NOT NULL,
                    total REAL NOT NULL,
                    sale_date TEXT NOT NULL
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS sale_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sale_id INTEGER NOT NULL,
                    product_name TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    price REAL NOT NULL,
                    subtotal REAL NOT NULL,
                    FOREIGN KEY (sale_id) REFERENCES sales(id)
                )
            """)
            con.commit()

    def build_ui(self):
        header = tk.Frame(self.root, bg="#17324d", height=70)
        header.pack(fill="x")
        tk.Label(header, text="SHOP BILLING MANAGEMENT SYSTEM",
                 bg="#17324d", fg="white", font=("Arial", 19, "bold")).pack(pady=18)

        self.tabs = ttk.Notebook(self.root)
        self.tabs.pack(fill="both", expand=True, padx=12, pady=12)

        self.dashboard_tab = ttk.Frame(self.tabs, padding=15)
        self.products_tab = ttk.Frame(self.tabs, padding=15)
        self.billing_tab = ttk.Frame(self.tabs, padding=15)
        self.sales_tab = ttk.Frame(self.tabs, padding=15)

        self.tabs.add(self.dashboard_tab, text="Dashboard")
        self.tabs.add(self.products_tab, text="Products")
        self.tabs.add(self.billing_tab, text="Billing")
        self.tabs.add(self.sales_tab, text="Sales History")

        self.build_dashboard()
        self.build_products()
        self.build_billing()
        self.build_sales()

    def build_dashboard(self):
        ttk.Label(self.dashboard_tab, text="Store Overview",
                  font=("Arial", 18, "bold")).pack(anchor="w", pady=(5, 20))
        cards = ttk.Frame(self.dashboard_tab)
        cards.pack(fill="x")
        self.products_count = tk.StringVar(value="0")
        self.stock_count = tk.StringVar(value="0")
        self.sales_total = tk.StringVar(value="₹0.00")

        for title, variable in [
            ("PRODUCT TYPES", self.products_count),
            ("TOTAL STOCK UNITS", self.stock_count),
            ("TOTAL SALES", self.sales_total)
        ]:
            card = ttk.LabelFrame(cards, text=title, padding=22)
            card.pack(side="left", fill="both", expand=True, padx=8)
            ttk.Label(card, textvariable=variable,
                      font=("Arial", 20, "bold")).pack(pady=8)

        ttk.Label(self.dashboard_tab,
                  text="Use the Products tab to manage inventory and the Billing tab to create customer bills.",
                  wraplength=800).pack(anchor="w", pady=30)

    def build_products(self):
        ttk.Label(self.products_tab, text="Product Management",
                  font=("Arial", 17, "bold")).pack(anchor="w", pady=(0, 12))

        form = ttk.LabelFrame(self.products_tab, text="Add a product", padding=12)
        form.pack(fill="x", pady=5)

        self.product_name = tk.StringVar()
        self.product_price = tk.StringVar()
        self.product_stock = tk.StringVar()

        ttk.Label(form, text="Product name").grid(row=0, column=0, sticky="w", padx=5)
        ttk.Entry(form, textvariable=self.product_name, width=25).grid(row=1, column=0, padx=5, pady=5)
        ttk.Label(form, text="Price (₹)").grid(row=0, column=1, sticky="w", padx=5)
        ttk.Entry(form, textvariable=self.product_price, width=15).grid(row=1, column=1, padx=5, pady=5)
        ttk.Label(form, text="Stock quantity").grid(row=0, column=2, sticky="w", padx=5)
        ttk.Entry(form, textvariable=self.product_stock, width=15).grid(row=1, column=2, padx=5, pady=5)
        ttk.Button(form, text="Add Product", command=self.add_product).grid(row=1, column=3, padx=12)

        columns = ("id", "name", "price", "stock")
        self.product_tree = ttk.Treeview(self.products_tab, columns=columns, show="headings", height=15)
        for col, heading, width in [
            ("id", "ID", 70), ("name", "Product Name", 400),
            ("price", "Price (₹)", 180), ("stock", "Stock", 150)
        ]:
            self.product_tree.heading(col, text=heading)
            self.product_tree.column(col, width=width, anchor="center")
        self.product_tree.pack(fill="both", expand=True, pady=12)

        ttk.Button(self.products_tab, text="Delete Selected Product",
                   command=self.delete_product).pack(anchor="e")

    def build_billing(self):
        ttk.Label(self.billing_tab, text="Create Customer Bill",
                  font=("Arial", 17, "bold")).pack(anchor="w", pady=(0, 10))

        top = ttk.Frame(self.billing_tab)
        top.pack(fill="x", pady=5)
        ttk.Label(top, text="Customer name:").pack(side="left")
        self.customer_name = tk.StringVar()
        ttk.Entry(top, textvariable=self.customer_name, width=30).pack(side="left", padx=8)

        add_frame = ttk.LabelFrame(self.billing_tab, text="Add item to bill", padding=10)
        add_frame.pack(fill="x", pady=8)
        self.selected_product = tk.StringVar()
        self.bill_quantity = tk.StringVar(value="1")
        ttk.Label(add_frame, text="Product").grid(row=0, column=0, padx=5)
        self.product_combo = ttk.Combobox(add_frame, textvariable=self.selected_product,
                                          state="readonly", width=35)
        self.product_combo.grid(row=0, column=1, padx=5)
        ttk.Label(add_frame, text="Quantity").grid(row=0, column=2, padx=5)
        ttk.Entry(add_frame, textvariable=self.bill_quantity, width=8).grid(row=0, column=3, padx=5)
        ttk.Button(add_frame, text="Add to Cart", command=self.add_to_cart).grid(row=0, column=4, padx=10)

        body = ttk.Frame(self.billing_tab)
        body.pack(fill="both", expand=True, pady=8)
        cart_frame = ttk.Frame(body)
        cart_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        ttk.Label(cart_frame, text="Shopping Cart", font=("Arial", 11, "bold")).pack(anchor="w")
        self.cart_tree = ttk.Treeview(cart_frame, columns=("name", "qty", "price", "subtotal"),
                                      show="headings", height=12)
        for col, heading, width in [
            ("name", "Product", 180), ("qty", "Qty", 55),
            ("price", "Price", 85), ("subtotal", "Subtotal", 100)
        ]:
            self.cart_tree.heading(col, text=heading)
            self.cart_tree.column(col, width=width, anchor="center")
        self.cart_tree.pack(fill="both", expand=True, pady=5)
        ttk.Button(cart_frame, text="Remove Selected Item",
                   command=self.remove_cart_item).pack(anchor="e")

        invoice_frame = ttk.Frame(body)
        invoice_frame.pack(side="right", fill="both", expand=True)
        ttk.Label(invoice_frame, text="Invoice Preview", font=("Arial", 11, "bold")).pack(anchor="w")
        self.invoice_text = tk.Text(invoice_frame, height=13, width=42, font=("Courier", 9))
        self.invoice_text.pack(fill="both", expand=True, pady=5)
        self.total_label = ttk.Label(self.billing_tab, text="Total: ₹0.00",
                                     font=("Arial", 14, "bold"))
        self.total_label.pack(anchor="e", pady=5)
        ttk.Button(self.billing_tab, text="Generate Bill & Save Sale",
                   command=self.checkout).pack(anchor="e", pady=5)

    def build_sales(self):
        ttk.Label(self.sales_tab, text="Previous Transactions",
                  font=("Arial", 17, "bold")).pack(anchor="w", pady=(0, 12))
        cols = ("id", "customer", "total", "date")
        self.sales_tree = ttk.Treeview(self.sales_tab, columns=cols, show="headings", height=20)
        for col, heading, width in [
            ("id", "Bill ID", 90), ("customer", "Customer", 250),
            ("total", "Total (₹)", 160), ("date", "Date & Time", 260)
        ]:
            self.sales_tree.heading(col, text=heading)
            self.sales_tree.column(col, width=width, anchor="center")
        self.sales_tree.pack(fill="both", expand=True)

    def add_product(self):
        name = self.product_name.get().strip()
        try:
            price = float(self.product_price.get())
            stock = int(self.product_stock.get())
            if not name or price <= 0 or stock < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid input", "Enter a name, a price above 0, and stock of 0 or more.")
            return

        with self.connect() as con:
            con.execute("INSERT INTO products(name, price, stock) VALUES (?, ?, ?)",
                        (name, price, stock))
        self.product_name.set("")
        self.product_price.set("")
        self.product_stock.set("")
        self.refresh_products()
        self.refresh_product_dropdown()
        self.update_dashboard()
        messagebox.showinfo("Success", "Product added successfully.")

    def delete_product(self):
        selected = self.product_tree.selection()
        if not selected:
            messagebox.showwarning("Select product", "Please select a product to delete.")
            return
        product_id = self.product_tree.item(selected[0])["values"][0]
        if messagebox.askyesno("Confirm", "Delete the selected product?"):
            with self.connect() as con:
                con.execute("DELETE FROM products WHERE id = ?", (product_id,))
            self.refresh_products()
            self.refresh_product_dropdown()
            self.update_dashboard()

    def refresh_products(self):
        for item in self.product_tree.get_children():
            self.product_tree.delete(item)
        with self.connect() as con:
            rows = con.execute("SELECT id, name, price, stock FROM products ORDER BY name").fetchall()
        for row in rows:
            self.product_tree.insert("", "end", values=(row[0], row[1], f"{row[2]:.2f}", row[3]))

    def refresh_product_dropdown(self):
        with self.connect() as con:
            rows = con.execute("SELECT name FROM products WHERE stock > 0 ORDER BY name").fetchall()
        self.product_combo["values"] = [r[0] for r in rows]
        if rows and self.selected_product.get() not in self.product_combo["values"]:
            self.selected_product.set(rows[0][0])
        elif not rows:
            self.selected_product.set("")

    def add_to_cart(self):
        name = self.selected_product.get()
        if not name:
            messagebox.showwarning("No products", "Add a product with available stock first.")
            return
        try:
            qty = int(self.bill_quantity.get())
            if qty <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid quantity", "Quantity must be a positive whole number.")
            return

        with self.connect() as con:
            row = con.execute("SELECT price, stock FROM products WHERE name = ?", (name,)).fetchone()
        if not row:
            messagebox.showerror("Error", "Product not found.")
            return

        existing_qty = sum(item["qty"] for item in self.cart if item["name"] == name)
        if existing_qty + qty > row[1]:
            messagebox.showerror("Insufficient stock", f"Only {row[1]} unit(s) are available.")
            return

        existing = next((item for item in self.cart if item["name"] == name), None)
        if existing:
            existing["qty"] += qty
        else:
            self.cart.append({"name": name, "price": row[0], "qty": qty})
        self.bill_quantity.set("1")
        self.refresh_cart()

    def refresh_cart(self):
        for item in self.cart_tree.get_children():
            self.cart_tree.delete(item)
        total = 0
        for item in self.cart:
            subtotal = item["price"] * item["qty"]
            total += subtotal
            self.cart_tree.insert("", "end", values=(
                item["name"], item["qty"], f'{item["price"]:.2f}', f"{subtotal:.2f}"
            ))
        self.total_label.config(text=f"Total: ₹{total:.2f}")
        self.show_invoice_preview(total)

    def show_invoice_preview(self, total):
        self.invoice_text.delete("1.0", "end")
        self.invoice_text.insert("end", "          SHOP INVOICE\n")
        self.invoice_text.insert("end", "-" * 38 + "\n")
        self.invoice_text.insert("end", f"Customer: {self.customer_name.get().strip() or 'Walk-in'}\n")
        self.invoice_text.insert("end", f"Date: {datetime.now():%d-%m-%Y %H:%M}\n")
        self.invoice_text.insert("end", "-" * 38 + "\n")
        for item in self.cart:
            subtotal = item["price"] * item["qty"]
            self.invoice_text.insert("end", f'{item["name"][:15]:15} {item["qty"]:>3} x {item["price"]:>7.2f}\n')
            self.invoice_text.insert("end", f'{"":15} Subtotal: {subtotal:>10.2f}\n')
        self.invoice_text.insert("end", "-" * 38 + "\n")
        self.invoice_text.insert("end", f"TOTAL: Rs. {total:.2f}\n")
        self.invoice_text.insert("end", "Thank you for shopping!\n")

    def remove_cart_item(self):
        selected = self.cart_tree.selection()
        if not selected:
            messagebox.showwarning("Select item", "Select an item to remove.")
            return
        name = self.cart_tree.item(selected[0])["values"][0]
        self.cart = [item for item in self.cart if item["name"] != name]
        self.refresh_cart()

    def checkout(self):
        customer = self.customer_name.get().strip() or "Walk-in"
        if not self.cart:
            messagebox.showwarning("Empty cart", "Add at least one product before generating a bill.")
            return

        total = sum(item["price"] * item["qty"] for item in self.cart)
        sale_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            with self.connect() as con:
                cur = con.cursor()
                # Recheck stock and save the sale in one database transaction.
                for item in self.cart:
                    row = cur.execute("SELECT stock FROM products WHERE name = ?",
                                      (item["name"],)).fetchone()
                    if not row or row[0] < item["qty"]:
                        raise ValueError(f'Not enough stock for {item["name"]}.')
                cur.execute("INSERT INTO sales(customer, total, sale_date) VALUES (?, ?, ?)",
                            (customer, total, sale_date))
                sale_id = cur.lastrowid
                for item in self.cart:
                    subtotal = item["price"] * item["qty"]
                    cur.execute("""INSERT INTO sale_items
                        (sale_id, product_name, quantity, price, subtotal)
                        VALUES (?, ?, ?, ?, ?)""",
                        (sale_id, item["name"], item["qty"], item["price"], subtotal))
                    cur.execute("UPDATE products SET stock = stock - ? WHERE name = ?",
                                (item["qty"], item["name"]))
        except ValueError as exc:
            messagebox.showerror("Checkout failed", str(exc))
            self.refresh_products()
            self.refresh_product_dropdown()
            return

        self.cart.clear()
        self.customer_name.set("")
        self.refresh_cart()
        self.refresh_products()
        self.refresh_product_dropdown()
        self.refresh_sales()
        self.update_dashboard()
        messagebox.showinfo("Bill generated", f"Bill #{sale_id} saved successfully.\nTotal: ₹{total:.2f}")

    def refresh_sales(self):
        for item in self.sales_tree.get_children():
            self.sales_tree.delete(item)
        with self.connect() as con:
            rows = con.execute(
                "SELECT id, customer, total, sale_date FROM sales ORDER BY id DESC"
            ).fetchall()
        for row in rows:
            self.sales_tree.insert("", "end",
                                   values=(row[0], row[1], f"{row[2]:.2f}", row[3]))

    def update_dashboard(self):
        with self.connect() as con:
            product_types, stock_units = con.execute(
                "SELECT COUNT(*), COALESCE(SUM(stock), 0) FROM products"
            ).fetchone()
            total_sales = con.execute("SELECT COALESCE(SUM(total), 0) FROM sales").fetchone()[0]
        self.products_count.set(str(product_types))
        self.stock_count.set(str(stock_units))
        self.sales_total.set(f"₹{total_sales:.2f}")


if __name__ == "__main__":
    root = tk.Tk()
    app = ShopBillingApp(root)
    root.mainloop()
