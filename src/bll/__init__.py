"""
Business Logic Layer (BLL) for the Brew and Bite Café Management System.
Implements business rules and service logic.
"""

from src.bll.user_service import UserService
from src.bll.expense_service import ExpenseService
from src.bll.inventory_service import InventoryService
from src.bll.sales_service import SalesService
from src.bll.reporting_service import ReportingService
from src.bll.auth_service import AuthService

__all__ = [
    'UserService',
    'ExpenseService',
    'InventoryService',
    'SalesService',
    'ReportingService',
    'AuthService'
]

# Version of the BLL
__version__ = '1.0.0'

# Define service factory functions
def create_auth_service(session):
    return AuthService(session)

def create_user_service(session):
    return UserService(session)

def create_expense_service(session):
    return ExpenseService(session)

def create_inventory_service(session):
    return InventoryService(session)

def create_sales_service(session):
    return SalesService(session)

def create_reporting_service(session):
    return ReportingService(session)

# Service factory that creates all services
def create_services(session):
    return {
        'auth': create_auth_service(session),
        'user': create_user_service(session),
        'expense': create_expense_service(session),
        'inventory': create_inventory_service(session),
        'sales': create_sales_service(session),
        'reporting': create_reporting_service(session)
    }