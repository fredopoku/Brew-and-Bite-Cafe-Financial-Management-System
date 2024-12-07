"""
Graphical User Interface (GUI) package for the Brew and Bite Café Management System.
Implements all GUI screens and dialogs using tkinter.
"""

from src.gui.login_window import LoginWindow
from src.gui.main_window import MainWindow
from src.gui.sales_screen import SalesScreen
from src.gui.inventory_screen import InventoryScreen
from src.gui.expense_screen import ExpenseScreen
from src.gui.reports_screen import ReportsScreen
from src.gui.user_management_screen import UserManagementScreen
from src.gui.settings_screen import SettingsScreen

__all__ = [
    'LoginWindow',
    'MainWindow',
    'SalesScreen',
    'InventoryScreen',
    'ExpenseScreen',
    'ReportsScreen',
    'UserManagementScreen',
    'SettingsScreen'
]

# GUI Version
__version__ = '1.0.0'