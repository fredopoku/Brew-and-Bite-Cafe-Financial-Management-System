from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()


class UserRole(enum.Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    STAFF = "staff"


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(256), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.STAFF)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    reset_token = Column(String(256))
    reset_token_expiry = Column(DateTime)

    # Relationships
    expenses = relationship('Expense', back_populates='user')
    sales = relationship('Sale', back_populates='user')
    inventory_transactions = relationship('InventoryTransaction', back_populates='user')
    audit_logs = relationship('AuditLog', back_populates='user')


class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    type = Column(String(20), nullable=False)  # 'expense' or 'income'
    description = Column(Text)

    # Relationships
    expenses = relationship('Expense', back_populates='category')


class Expense(Base):
    __tablename__ = 'expenses'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)
    amount = Column(Float, nullable=False)
    description = Column(Text)
    date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship('User', back_populates='expenses')
    category = relationship('Category', back_populates='expenses')


class InventoryItem(Base):
    __tablename__ = 'inventory'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    quantity = Column(Integer, default=0)
    unit_cost = Column(Float, nullable=False)
    reorder_level = Column(Integer, default=10)
    last_restocked = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    sale_items = relationship('SaleItem', back_populates='inventory_item')
    inventory_transactions = relationship('InventoryTransaction', back_populates='inventory_item')


class InventoryTransaction(Base):
    __tablename__ = 'inventory_transactions'

    id = Column(Integer, primary_key=True)
    inventory_item_id = Column(Integer, ForeignKey('inventory.id'), nullable=False)
    transaction_type = Column(String(20), nullable=False)  # 'restock', 'sale', 'adjustment'
    quantity = Column(Integer, nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    notes = Column(Text)

    # Relationships
    inventory_item = relationship('InventoryItem', back_populates='inventory_transactions')
    user = relationship('User', back_populates='inventory_transactions')


class Sale(Base):
    __tablename__ = 'sales'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    date = Column(DateTime, nullable=False)
    total_amount = Column(Float, nullable=False)
    payment_method = Column(String(50))
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship('User', back_populates='sales')
    sale_items = relationship('SaleItem', back_populates='sale')


class SaleItem(Base):
    __tablename__ = 'sale_items'

    id = Column(Integer, primary_key=True)
    sale_id = Column(Integer, ForeignKey('sales.id'), nullable=False)
    inventory_item_id = Column(Integer, ForeignKey('inventory.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)

    # Relationships
    sale = relationship('Sale', back_populates='sale_items')
    inventory_item = relationship('InventoryItem', back_populates='sale_items')


class AuditLog(Base):
    __tablename__ = 'audit_logs'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    action = Column(String(50), nullable=False)
    table_name = Column(String(50), nullable=False)
    record_id = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)
    details = Column(Text)

    # Relationships
    user = relationship('User', back_populates='audit_logs')