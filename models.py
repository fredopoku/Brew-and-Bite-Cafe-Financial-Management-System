from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.ext.declarative import declarative_base

# Fix: Use the correct import path for declarative_base
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    password_hash = Column(String)
    email = Column(String)

class Expense(Base):
    __tablename__ = 'expenses'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    category_id = Column(Integer, ForeignKey('categories.id'))
    date = Column(Date)
    amount = Column(Float)
    description = Column(String)

    user = relationship('User', back_populates='expenses')
    category = relationship('Category', back_populates='expenses')

class Inventory(Base):
    __tablename__ = 'inventory'

    id = Column(Integer, primary_key=True)
    item_name = Column(String)
    quantity = Column(Integer)
    cost = Column(Float)

class Sale(Base):
    __tablename__ = 'sales'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    date = Column(Date)
    amount = Column(Float)

    user = relationship('User', back_populates='sales')

class SaleItem(Base):
    __tablename__ = 'sale_items'

    id = Column(Integer, primary_key=True)
    sale_id = Column(Integer, ForeignKey('sales.id'))
    item_id = Column(Integer, ForeignKey('inventory.id'))
    quantity_sold = Column(Integer)

    sale = relationship('Sale', back_populates='sale_items')
    item = relationship('Inventory')

class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    category_name = Column(String)

User.expenses = relationship('Expense', back_populates='user')
User.sales = relationship('Sale', back_populates='user')
Sale.sale_items = relationship('SaleItem', back_populates='sale')
Inventory.sale_items = relationship('SaleItem', back_populates='item')
Category.expenses = relationship('Expense', back_populates='category')
