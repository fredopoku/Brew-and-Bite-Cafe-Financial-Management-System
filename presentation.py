import tkinter as tk
from tkinter import messagebox, simpledialog
from business_logic import register_user, authenticate_user, record_expense, add_inventory_item, record_sale, generate_expense_report, generate_inventory_report, generate_sales_report

# Function to display a message box with a title and message
def show_message(title, message):
    messagebox.showinfo(title, message)

# GUI function to handle user registration
def register_user_gui():
    def register():
        # Retrieve input data from user
        username = entry_username.get()
        password = entry_password.get()
        email = entry_email.get()
        # Call business logic to register the user
        register_user(username, password, email)
        # Notify the user of success and close the window
        show_message("Success", "User registered successfully!")
        register_window.destroy()

    # Create a new top-level window for user registration
    register_window = tk.Toplevel(root)
    register_window.title("Register User")

    # Create input fields for username, password, and email
    tk.Label(register_window, text="Username:").pack()
    entry_username = tk.Entry(register_window)
    entry_username.pack()

    tk.Label(register_window, text="Password:").pack()
    entry_password = tk.Entry(register_window, show="*")
    entry_password.pack()

    tk.Label(register_window, text="Email:").pack()
    entry_email = tk.Entry(register_window)
    entry_email.pack()

    # Button to trigger the registration process
    tk.Button(register_window, text="Register", command=register).pack()

# GUI function to handle recording an expense
def record_expense_gui():
    def record_expense():
        # Retrieve input data from the user
        user_id = int(entry_user_id.get())
        category_id = int(entry_category_id.get())
        date = entry_date.get()
        amount = float(entry_amount.get())
        description = entry_description.get()
        # Call business logic to record the expense
        record_expense(user_id, category_id, date, amount, description)
        # Notify the user of success and close the window
        show_message("Success", "Expense recorded successfully!")
        expense_window.destroy()

    # Create a new top-level window for recording expenses
    expense_window = tk.Toplevel(root)
    expense_window.title("Record Expense")

    # Create input fields for expense details
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

    # Button to trigger the expense recording process
    tk.Button(expense_window, text="Record", command=record_expense).pack()

# GUI function to handle adding an inventory item
def add_inventory_item_gui():
    def add_item():
        # Retrieve input data from the user
        item_name = entry_item_name.get()
        quantity = int(entry_quantity.get())
        cost = float(entry_cost.get())
        # Call business logic to add the inventory item
        add_inventory_item(item_name, quantity, cost)
        # Notify the user of success and close the window
        show_message("Success", "Inventory item added successfully!")
        inventory_window.destroy()

    # Create a new top-level window for adding inventory items
    inventory_window = tk.Toplevel(root)
    inventory_window.title("Add Inventory Item")

    # Create input fields for inventory item details
    tk.Label(inventory_window, text="Item Name:").pack()
    entry_item_name = tk.Entry(inventory_window)
    entry_item_name.pack()

    tk.Label(inventory_window, text="Quantity:").pack()
    entry_quantity = tk.Entry(inventory_window)
    entry_quantity.pack()

    tk.Label(inventory_window, text="Cost:").pack()
    entry_cost = tk.Entry(inventory_window)
    entry_cost.pack()

    # Button to trigger the inventory item addition process
    tk.Button(inventory_window, text="Add", command=add_item).pack()

# GUI function to handle recording a sale
def record_sale_gui():
    def record_sale():
        # Retrieve input data from the user
        user_id = int(entry_user_id.get())
        date = entry_date.get()
        amount = float(entry_amount.get())
        # Use eval to parse the input for items sold (dictionary format)
        items_sold = eval(entry_items_sold.get())  # Format: {item_id: quantity_sold}
        # Call business logic to record the sale
        record_sale(user_id, date, amount, items_sold)
        # Notify the user of success and close the window
        show_message("Success", "Sale recorded successfully!")
        sale_window.destroy()

    # Create a new top-level window for recording sales
    sale_window = tk.Toplevel(root)
    sale_window.title("Record Sale")

    # Create input fields for sale details
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

    # Button to trigger the sale recording process
    tk.Button(sale_window, text="Record", command=record_sale).pack()

# GUI function to display the expense report
def generate_expense_report_gui():
    # Retrieve the expense report from business logic
    report = generate_expense_report()
    # Create a new top-level window to display the report
    report_window = tk.Toplevel(root)
    report_window.title("Expense Report")
    text_widget = tk.Text(report_window)
    text_widget.pack()
    # Populate the text widget with the report data
    for expense in report:
        text_widget.insert(tk.END, f"Date: {expense['date']}, Amount: {expense['amount']}, Category: {expense['category']}, Description: {expense['description']}\n")

# GUI function to display the inventory report
def generate_inventory_report_gui():
    # Retrieve the inventory report from business logic
    report = generate_inventory_report()
    # Create a new top-level window to display the report
    report_window = tk.Toplevel(root)
    report_window.title("Inventory Report")
    text_widget = tk.Text(report_window)
    text_widget.pack()
    # Populate the text widget with the report data
    for item in report:
        text_widget.insert(tk.END, f"Item Name: {item['item_name']}, Quantity: {item['quantity']}, Cost: {item['cost']}\n")

# GUI function to display the sales report
def generate_sales_report_gui():
    # Retrieve the sales report from business logic
    report = generate_sales_report()
    # Create a new top-level window to display the report
    report_window = tk.Toplevel(root)
    report_window.title("Sales Report")
    text_widget = tk.Text(report_window)
    text_widget.pack()
    # Populate the text widget with the report data
    for sale in report:
        text_widget.insert(tk.END, f"Date: {sale['date']}, Amount: {sale['amount']}, Items Sold: {sale['items_sold']}\n")

# Main application window
root = tk.Tk()
root.title("Brew and Bite Café Management System")

# Buttons to access various functionalities
tk.Button(root, text="Register User", command=register_user_gui).pack()
tk.Button(root, text="Record Expense", command=record_expense_gui).pack()
tk.Button(root, text="Add Inventory Item", command=add_inventory_item_gui).pack()
tk.Button(root, text="Record Sale", command=record_sale_gui).pack()
tk.Button(root, text="Generate Expense Report", command=generate_expense_report_gui).pack()
tk.Button(root, text="Generate Inventory Report", command=generate_inventory_report_gui).pack()
tk.Button(root, text="Generate Sales Report", command=generate_sales_report_gui).pack()

# Run the main event loop for the application
root.mainloop()
