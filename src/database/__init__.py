"""
Database configuration and models for the Brew and Bite Café Management System.
"""

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from src.config import DATABASE_URL
from src.database.models import (
    Base,
    User,
    Category,
    Expense,
    InventoryItem,
    InventoryTransaction,
    Sale,
    SaleItem,
    AuditLog,
    UserRole
)
from src.database.database import (
    initialize_database,
    get_session,
    backup_database,
    session_scope
)

# Create engine and session factory
engine = create_engine(DATABASE_URL, echo=False)
Session = sessionmaker(bind=engine)

__all__ = [
    'Base',
    'User',
    'Category',
    'Expense',
    'InventoryItem',
    'InventoryTransaction',
    'Sale',
    'SaleItem',
    'AuditLog',
    'UserRole',
    'initialize_database',
    'get_session',
    'backup_database',
    'session_scope',
    'engine',
    'Session'
]


def models():
    return None