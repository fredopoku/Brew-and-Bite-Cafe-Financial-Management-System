from hashlib import sha256  # Import the SHA-256 hashing function from the hashlib module
from datetime import datetime  # Import the datetime module for handling dates and times
from database import session, User, Category, Expense, Inventory, Sale, SaleItem  # Import database session and models

def hash_password(password):
        # Hashes the input password using SHA-256 and returns the hexadecimal digest
        return sha256(password.encode()).hexdigest()

def register_user(username, password, email):
        # Registers a new user in the database by creating a User object
        password_hash = hash_password(password)  # Hash the password for secure storage
        new_user = User(username=username, password_hash=password_hash, email=email)  # Create a new User object
        session.add(new_user)  # Add the new user to the database session
        session.commit()  # Commit the transaction to save changes

def authenticate_user(username, password):
        # Authenticates a user by verifying their username and hashed password
        password_hash = hash_password(password)  # Hash the password to compare with stored hash
        user = session.query(User).filter_by(username=username, password_hash=password_hash).first()  # Query user from database
        return user  # Return the user object if found, or None if not authenticated

def record_expense(user_id, category_id, date, amount, description):
        # Records an expense in the database by creating an Expense object
        expense = Expense(
            user_id=user_id,  # ID of the user recording the expense
            category_id=category_id,  # ID of the category of the expense
            date=date,  # Date of the expense
            amount=amount,  # Amount spent
            description=description  # Description of the expense
        )
        session.add(expense)  # Add the expense to the database session
        session.commit()  # Commit the transaction to save changes

def add_inventory_item(item_name, quantity, cost):
        # Adds a new inventory item to the database
        item = Inventory(
            item_name=item_name,  # Name of the inventory item
            quantity=quantity,  # Quantity of the item in stock
            cost=cost  # Cost of the item
        )
        session.add(item)  # Add the inventory item to the database session
        session.commit()  # Commit the transaction to save changes

def record_sale(user_id, date, amount, items_sold):
        # Records a sale transaction and its associated sold items in the database
        sale = Sale(
            user_id=user_id,  # ID of the user recording the sale
            date=date,  # Date of the sale
            amount=amount  # Total amount of the sale
        )
        session.add(sale)  # Add the sale to the database session
        session.commit()  # Commit the sale to generate the sale ID

        for item_id, quantity_sold in items_sold.items():
            # Iterate through each sold item and record its details
            sale_item = SaleItem(
                sale_id=sale.sale_id,  # ID of the associated sale
                item_id=item_id,  # ID of the sold item
                quantity_sold=quantity_sold  # Quantity of the item sold
            )
            session.add(sale_item)  # Add the sale item to the database session

        session.commit()  # Commit the transaction to save changes

def generate_expense_report():
        # Generates a report of all expenses from the database
        expenses = session.query(Expense).all()  # Query all expenses
        report = []  # Initialize an empty list to hold the report
        for expense in expenses:
            # Add details of each expense to the report
            report.append({
                'date': expense.date,  # Date of the expense
                'amount': expense.amount,  # Amount spent
                'category': expense.category.category_name,  # Name of the expense category
                'description': expense.description  # Description of the expense
            })
        return report  # Return the generated expense report

def generate_inventory_report():
        # Generates a report of all inventory items from the database
        inventory = session.query(Inventory).all()  # Query all inventory items
        report = []  # Initialize an empty list to hold the report
        for item in inventory:
            # Add details of each inventory item to the report
            report.append({
                'item_name': item.item_name,  # Name of the inventory item
                'quantity': item.quantity,  # Quantity of the item in stock
                'cost': item.cost  # Cost of the item
            })
        return report  # Return the generated inventory report

def generate_sales_report():
        # Generates a report of all sales transactions from the database
        sales = session.query(Sale).all()  # Query all sales
        report = []  # Initialize an empty list to hold the report
        for sale in sales:
            # Query all items sold in the current sale
            items_sold = session.query(SaleItem).filter_by(sale_id=sale.sale_id).all()
            # Create a list of sold items with their names and quantities
            items_sold_list = [{'item_name': item.inventory_item.item_name, 'quantity_sold': item.quantity_sold} for item in items_sold]
            # Add details of the sale and associated items to the report
            report.append({
                'date': sale.date,  # Date of the sale
                'amount': sale.amount,  # Total amount of the sale
                'items_sold': items_sold_list  # List of sold items with details
            })
        return report  # Return the generated sales report
