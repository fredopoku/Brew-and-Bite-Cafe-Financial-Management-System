from sqlalchemy import create_engine, Column, Integer, String, Float, Date, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# Base class for all ORM models
Base = declarative_base()

# User model representing the users table
class User(Base):
    __tablename__ = 'users'  # Define the table name
    user_id = Column(Integer, primary_key=True, autoincrement=True)  # Primary key with auto-increment
    username = Column(String(50), unique=True, nullable=False)  # Unique username field
    password_hash = Column(String(255), nullable=False)  # Password hash field
    email = Column(String(100), unique=True, nullable=False)  # Unique email field

# Category model representing the categories table
class Category(Base):
    __tablename__ = 'categories'  # Define the table name
    category_id = Column(Integer, primary_key=True, autoincrement=True)  # Primary key with auto-increment
    category_name = Column(String(50), nullable=False)  # Category name field

# Expense model representing the expenses table
class Expense(Base):
    __tablename__ = 'expenses'  # Define the table name
    expense_id = Column(Integer, primary_key=True, autoincrement=True)  # Primary key with auto-increment
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)  # Foreign key to users table
    category_id = Column(Integer, ForeignKey('categories.category_id'), nullable=False)  # Foreign key to categories table
    date = Column(Date, nullable=False)  # Date of the expense
    amount = Column(Float, nullable=False)  # Expense amount
    description = Column(Text, nullable=True)  # Optional description field
    user = relationship("User", backref="expenses")  # Establish relationship with User
    category = relationship("Category", backref="expenses")  # Establish relationship with Category

# Inventory model representing the inventory table
class Inventory(Base):
    __tablename__ = 'inventory'  # Define the table name
    item_id = Column(Integer, primary_key=True, autoincrement=True)  # Primary key with auto-increment
    item_name = Column(String(100), nullable=False)  # Inventory item name
    quantity = Column(Integer, nullable=False)  # Quantity of the item
    cost = Column(Float, nullable=False)  # Cost of the item

# Sale model representing the sales table
class Sale(Base):
    __tablename__ = 'sales'  # Define the table name
    sale_id = Column(Integer, primary_key=True, autoincrement=True)  # Primary key with auto-increment
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)  # Foreign key to users table
    date = Column(Date, nullable=False)  # Date of the sale
    amount = Column(Float, nullable=False)  # Total amount of the sale
    user = relationship("User", backref="sales")  # Establish relationship with User

# SaleItem model representing the sale_items table
class SaleItem(Base):
    __tablename__ = 'sale_items'  # Define the table name
    sale_item_id = Column(Integer, primary_key=True, autoincrement=True)  # Primary key with auto-increment
    sale_id = Column(Integer, ForeignKey('sales.sale_id'), nullable=False)  # Foreign key to sales table
    item_id = Column(Integer, ForeignKey('inventory.item_id'), nullable=False)  # Foreign key to inventory table
    quantity_sold = Column(Integer, nullable=False)  # Quantity of the item sold
    sale = relationship("Sale", backref="sale_items")  # Establish relationship with Sale
    inventory_item = relationship("Inventory", backref="sale_items")  # Establish relationship with Inventory

# Create a SQLite database connection
engine = create_engine('sqlite:///brew_and_bite.db')

# Create all tables defined in the Base class
Base.metadata.create_all(engine)

# Configure a sessionmaker bound to the engine
Session = sessionmaker(bind=engine)

# Create a session instance for interacting with the database
session = Session()
