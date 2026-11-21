# Shop Billing Management System

A beginner-friendly desktop Point of Sale (POS) application built with Python, Tkinter and SQLite.

## Features
- Dashboard showing product count, total stock and total sales
- Add and delete products
- Create customer bills with a shopping cart
- Automatic subtotal and total calculations
- Stock validation and automatic stock deduction after checkout
- Persistent sales history stored in SQLite

## Requirements
- Python 3.9 or newer
- Tkinter (usually included with Python)
- SQLite (included with Python)

No third-party Python packages are required.

## Run the project
1. Download or clone this repository.
2. Open a terminal in the project folder.
3. Run:

   ```bash
   python app.py
   ```

4. Add products from the **Products** tab.
5. Open **Billing**, enter a customer name, add products and quantities, then click **Generate Bill & Save Sale**.
6. Review completed transactions in **Sales History**.

The application automatically creates `shop.db` in the working directory on first run. Keep this file to retain your local products and sales.

## Project structure
```text
shop-billing-management-system/
├── app.py
├── README.md
└── .gitignore
```

## Notes
This is a learning/portfolio project. It is designed as a local, single-computer application and does not include tax configuration, barcode scanning, user authentication, or printing integration.
