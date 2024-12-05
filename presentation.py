import tkinter as tk
from tkinter import messagebox, simpledialog
from business_logic import (
    register_user, authenticate_user, record_expense,
    add_inventory_item, record_sale, generate_expense_report,
    generate_inventory_report, generate_sales_report
)
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models import User, Expense, Inventory, Sale, SaleItem, Category  # Import your ORM models

# Set up the database connection
engine = create_engine('sqlite:///brew_and_bite.db')
Session = sessionmaker(bind=engine)
session = Session()


# Function to display a message box with a title and message
def show_message(title, message):
    messagebox.showinfo(title, message)


# Utility function to validate that a string is a valid float
def validate_float(value, field_name):
    try:
        return float(value)
    except ValueError:
        show_message("Error", f"Invalid value for {field_name}. Please enter a valid number.")
        return None


# GUI function to handle user registration
def register_user_gui():
    def register():
        username = entry_username.get()
        password = entry_password.get()
        email = entry_email.get()

        if not username or not password or not email:
            show_message("Error", "All fields must be filled.")
            return

        # Check if email already exists
        existing_user = session.query(User).filter(User.email == email).first()
        if existing_user:
            show_message("Error", "Email is already registered. Please use a different email.")
            return

        # Insert user into the database
        new_user = User(username=username, password_hash=password, email=email)
        session.add(new_user)
        try:
            session.commit()
            show_message("Success", "User registered successfully!")
            register_window.destroy()
        except Exception as e:
            session.rollback()
            show_message("Error", f"An error occurred while registering the user: {str(e)}")

    register_window = tk.Toplevel(root)
    register_window.title("Register User")

    tk.Label(register_window, text="Username:").pack()
    entry_username = tk.Entry(register_window)
    entry_username.pack()

    tk.Label(register_window, text="Password:").pack()
    entry_password = tk.Entry(register_window, show="*")
    entry_password.pack()

    tk.Label(register_window, text="Email:").pack()
    entry_email = tk.Entry(register_window)
    entry_email.pack()

    tk.Button(register_window, text="Register", command=register).pack()


# GUI function to handle recording an expense
def record_expense_gui():
    def record_expense():
        user_id = entry_user_id.get()
        category_id = entry_category_id.get()
        date = entry_date.get()
        amount = validate_float(entry_amount.get(), "Amount")
        description = entry_description.get()

        if not user_id or not category_id or not date or not description:
            show_message("Error", "All fields must be filled.")
            return
        if amount is None:
            return

        # Insert expense into the database
        new_expense = Expense(user_id=int(user_id), category_id=int(category_id), date=date, amount=amount, description=description)
        session.add(new_expense)
        try:
            session.commit()
            show_message("Success", "Expense recorded successfully!")
            expense_window.destroy()
        except Exception as e:
            session.rollback()
            show_message("Error", f"An error occurred while recording the expense: {str(e)}")

    expense_window = tk.Toplevel(root)
    expense_window.title("Record Expense")

    tk.Label(expense_window, text="User ID:").pack()
    entry_user_id = tk.Entry(expense_window)
    entry_user_id.pack()

    tk.Label(expense_window, text="Category ID:").pack()
    entry_category_id = tk.Entry(expense_window)
    entry_category_id.pack()

    tk.Label(expense_window, text="Date (YYYY-MM-DD):").pack()
    entry_date = tk.Entry(expense_window)
    entry_date.pack()

    tk.Label(expense_window, text="Amount:").pack()
    entry_amount = tk.Entry(expense_window)
    entry_amount.pack()

    tk.Label(expense_window, text="Description:").pack()
    entry_description = tk.Entry(expense_window)
    entry_description.pack()

    tk.Button(expense_window, text="Record", command=record_expense).pack()


# GUI function to handle adding an inventory item
def add_inventory_item_gui():
    def add_item():
        item_name = entry_item_name.get()
        quantity = entry_quantity.get()
        cost = validate_float(entry_cost.get(), "Cost")

        if not item_name or not quantity or cost is None:
            show_message("Error", "All fields must be filled and Cost must be a valid number.")
            return

        # Insert inventory item into the database
        new_item = Inventory(item_name=item_name, quantity=int(quantity), cost=cost)
        session.add(new_item)
        try:
            session.commit()
            show_message("Success", "Inventory item added successfully!")
            inventory_window.destroy()
        except Exception as e:
            session.rollback()
            show_message("Error", f"An error occurred while adding the inventory item: {str(e)}")

    inventory_window = tk.Toplevel(root)
    inventory_window.title("Add Inventory Item")

    tk.Label(inventory_window, text="Item Name:").pack()
    entry_item_name = tk.Entry(inventory_window)
    entry_item_name.pack()

    tk.Label(inventory_window, text="Quantity:").pack()
    entry_quantity = tk.Entry(inventory_window)
    entry_quantity.pack()

    tk.Label(inventory_window, text="Cost:").pack()
    entry_cost = tk.Entry(inventory_window)
    entry_cost.pack()

    tk.Button(inventory_window, text="Add", command=add_item).pack()


# GUI function to handle recording a sale
def record_sale_gui():
    def record_sale():
        user_id = entry_user_id.get()
        date = entry_date.get()
        amount = validate_float(entry_amount.get(), "Amount")
        items_sold = entry_items_sold.get()

        if not user_id or not date or not items_sold or amount is None:
            show_message("Error", "All fields must be filled and Amount must be a valid number.")
            return

        # Convert string to dictionary
        items_sold_dict = eval(items_sold)  # Format: {item_id: quantity_sold}

        # Insert sale into the database
        new_sale = Sale(user_id=int(user_id), date=date, amount=amount)
        session.add(new_sale)
        try:
            session.commit()

            # Record the sale items
            for item_id, quantity_sold in items_sold_dict.items():
                new_sale_item = SaleItem(sale_id=new_sale.sale_id, item_id=item_id, quantity_sold=quantity_sold)
                session.add(new_sale_item)
            session.commit()

            show_message("Success", "Sale recorded successfully!")
            sale_window.destroy()
        except Exception as e:
            session.rollback()
            show_message("Error", f"An error occurred while recording the sale: {str(e)}")

    sale_window = tk.Toplevel(root)
    sale_window.title("Record Sale")

    tk.Label(sale_window, text="User ID:").pack()
    entry_user_id = tk.Entry(sale_window)
    entry_user_id.pack()

    tk.Label(sale_window, text="Date (YYYY-MM-DD):").pack()
    entry_date = tk.Entry(sale_window)
    entry_date.pack()

    tk.Label(sale_window, text="Amount:").pack()
    entry_amount = tk.Entry(sale_window)
    entry_amount.pack()

    tk.Label(sale_window, text="Items Sold (e.g., {1: 2, 2: 3}):").pack()
    entry_items_sold = tk.Entry(sale_window)
    entry_items_sold.pack()

    tk.Button(sale_window, text="Record", command=record_sale).pack()


# GUI function to display the expense report
def generate_expense_report_gui():
    report = generate_expense_report(session)
    report_window = tk.Toplevel(root)
    report_window.title("Expense Report")
    text_widget = tk.Text(report_window)
    text_widget.pack()
    for expense in report:
        text_widget.insert(tk.END,
                           f"Date: {expense.date}, Amount: {expense.amount}, Category: {expense.category.category_name}, Description: {expense.description}\n")


# GUI function to display the inventory report
def generate_inventory_report_gui():
    report = generate_inventory_report(session)
    report_window = tk.Toplevel(root)
    report_window.title("Inventory Report")
    text_widget = tk.Text(report_window)
    text_widget.pack()
    for item in report:
        text_widget.insert(tk.END,
                           f"Item Name: {item.item_name}, Quantity: {item.quantity}, Cost: {item.cost}\n")


# GUI function to display the sales report
def generate_sales_report_gui():
    report = generate_sales_report(session)
    report_window = tk.Toplevel(root)
    report_window.title("Sales Report")
    text_widget = tk.Text(report_window)
    text_widget.pack()
    for sale in report:
        text_widget.insert(tk.END,
                           f"Date: {sale.date}, Amount: {sale.amount}, Items Sold: {sale.items_sold}\n")


# Main application window
root = tk.Tk()
root.title("Brew and Bite Café Management System")

# Button to open user registration
register_button = tk.Button(root, text="Register User", command=register_user_gui)
register_button.pack()

# Button to record an expense
expense_button = tk.Button(root, text="Record Expense", command=record_expense_gui)
expense_button.pack()

# Button to add an inventory item
inventory_button = tk.Button(root, text="Add Inventory Item", command=add_inventory_item_gui)
inventory_button.pack()

# Button to record a sale
sale_button = tk.Button(root, text="Record Sale", command=record_sale_gui)
sale_button.pack()

# Button to generate an expense report
expense_report_button = tk.Button(root, text="Generate Expense Report", command=generate_expense_report_gui)
expense_report_button.pack()

# Button to generate an inventory report
inventory_report_button = tk.Button(root, text="Generate Inventory Report", command=generate_inventory_report_gui)
inventory_report_button.pack()

# Button to generate a sales report
sales_report_button = tk.Button(root, text="Generate Sales Report", command=generate_sales_report_gui)
sales_report_button.pack()

# Start the application
root.mainloop()
