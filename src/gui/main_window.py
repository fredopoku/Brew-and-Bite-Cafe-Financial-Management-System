from typing import Dict, Optional
import tkinter as tk
from tkinter import ttk, messagebox
import logging
from datetime import datetime, timedelta

# Local imports
from src.services.auth_service import AuthService
from src.services.user_service import UserService
from src.services.sales_service import SalesService
from src.services.expense_service import ExpenseService
from src.services.inventory_service import InventoryService
from src.services.reporting_service import ReportingService
from src.gui.dialogs import ChangePasswordDialog, UserManualDialog
from src.database.models import UserRole

logger = logging.getLogger(__name__)


class MainWindow:
    def __init__(self, user_data: Dict, auth_service: AuthService):
        self.user_data = user_data
        self.auth_service = auth_service
        self.last_activity = datetime.now()

        # Initialize main window
        self.root = tk.Tk()
        self.setup_window()
        self.create_services()
        self.create_widgets()
        self.setup_activity_tracking()

        # Load initial view
        self.load_dashboard()

    def setup_window(self):
        """Configure the main window"""
        self.root.title("Brew and Bite Café Management System")
        self.root.geometry("1024x768")
        self.root.minsize(800, 600)

        # Configure grid weights
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

    def create_services(self):
        """Initialize required services"""
        try:
            session = self.auth_service.session
            self.services = {
                'auth': self.auth_service,
                'user': UserService(session),
                'sales': SalesService(session),
                'expense': ExpenseService(session),
                'inventory': InventoryService(session),
                'reporting': ReportingService(session)
            }
        except Exception as e:
            logger.error(f"Error creating services: {str(e)}")
            messagebox.showerror("Error", "Failed to initialize services")
            self.root.destroy()

    def create_widgets(self):
        """Create and arrange main window widgets"""
        # Create menu bar
        self.create_menu()

        # Create sidebar
        self.create_sidebar()

        # Create main content area
        self.create_main_content()

        # Create status bar
        self.create_status_bar()

    def create_menu(self):
        """Create menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Change Password", command=self.show_change_password)
        file_menu.add_separator()
        file_menu.add_command(label="Logout", command=self.logout)
        file_menu.add_command(label="Exit", command=self.quit_app)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="User Manual", command=self.show_manual)
        help_menu.add_command(label="About", command=self.show_about)

    def create_sidebar(self):
        """Create navigation sidebar"""
        sidebar = ttk.Frame(self.root, relief="solid", borderwidth=1)
        sidebar.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # User info
        ttk.Label(
            sidebar,
            text=f"Welcome, {self.user_data['username']}",
            font=("Helvetica", 12, "bold")
        ).pack(pady=10)

        ttk.Label(
            sidebar,
            text=f"Role: {self.user_data['role']}",
            font=("Helvetica", 10)
        ).pack(pady=5)

        ttk.Separator(sidebar).pack(fill="x", pady=10)

        # Navigation buttons
        nav_buttons = [
            ("Dashboard", self.load_dashboard),
            ("Sales", self.load_sales),
            ("Inventory", self.load_inventory),
            ("Expenses", self.load_expenses),
            ("Reports", self.load_reports)
        ]

        for text, command in nav_buttons:
            ttk.Button(
                sidebar,
                text=text,
                command=command,
                width=20
            ).pack(pady=5)

        # Add user management for admin users
        if self.user_data['role'] == UserRole.ADMIN:
            ttk.Button(
                sidebar,
                text="User Management",
                command=self.load_user_management,
                width=20
            ).pack(pady=5)

    def create_main_content(self):
        """Create main content area"""
        self.main_content = ttk.Frame(self.root)
        self.main_content.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

    def create_status_bar(self):
        """Create status bar"""
        status_bar = ttk.Frame(self.root)
        status_bar.grid(row=1, column=0, columnspan=2, sticky="ew")

        # Add status info
        ttk.Label(
            status_bar,
            text=f"Version 1.0.0"
        ).pack(side="left", padx=10)

        # Add time display
        self.time_label = ttk.Label(status_bar)
        self.time_label.pack(side="right", padx=10)
        self.update_time()

    def load_dashboard(self):
        """Load dashboard view"""
        try:
            # Clear main content
            for widget in self.main_content.winfo_children():
                widget.destroy()

            # Get current date
            today = datetime.now().strftime('%Y-%m-%d')

            # Get required data
            sales_summary = self.services['sales'].get_daily_sales_summary(today)
            expense_summary = self.services['expense'].get_expense_summary(today, today)
            inventory_status = self.services['inventory'].get_inventory_status()

            # Create statistics frame
            stats_frame = ttk.Frame(self.main_content)
            stats_frame.pack(fill="x", padx=20, pady=10)

            for i in range(3):
                stats_frame.grid_columnconfigure(i, weight=1)

            # Create statistic cards
            self.create_stat_card(
                stats_frame,
                "Today's Sales",
                f"${sales_summary['summary']['total_sales']:,.2f}",
                f"Transactions: {sales_summary['summary']['transaction_count']}",
                0
            )

            self.create_stat_card(
                stats_frame,
                "Today's Expenses",
                f"${expense_summary['summary']['total_amount']:,.2f}",
                f"Items: {expense_summary['summary']['total_transactions']}",
                1
            )

            self.create_stat_card(
                stats_frame,
                "Inventory Value",
                f"${inventory_status['total_value']:,.2f}",
                f"Items: {inventory_status['total_items']}",
                2
            )

            # Create recent activities section
            self.create_activities_section()

        except Exception as e:
            logger.error(f"Error loading dashboard: {str(e)}")
            messagebox.showerror("Error", "Failed to load dashboard data")

    def create_stat_card(self, parent, title: str, value: str, subtitle: str, column: int):
        """Create a statistics card widget"""
        card = ttk.Frame(parent, relief="solid", borderwidth=1)
        card.grid(row=0, column=column, padx=10, pady=5, sticky="nsew")

        ttk.Label(
            card,
            text=title,
            font=("Helvetica", 12)
        ).pack(padx=10, pady=5)

        ttk.Label(
            card,
            text=value,
            font=("Helvetica", 16, "bold")
        ).pack(padx=10)

        ttk.Label(
            card,
            text=subtitle,
            font=("Helvetica", 10)
        ).pack(padx=10, pady=5)

    def create_activities_section(self):
        """Create recent activities section"""
        activities_frame = ttk.LabelFrame(self.main_content, text="Recent Activities")
        activities_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Create activity table
        columns = ("Time", "Type", "Amount", "Details")
        tree = ttk.Treeview(activities_frame, columns=columns, show="headings")

        # Configure columns
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(activities_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        # Pack table and scrollbar
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Load activities
        activities = self.services['reporting'].get_recent_activities()
        for activity in activities:
            tree.insert("", "end", values=(
                activity['timestamp'].strftime("%H:%M:%S"),
                activity['type'],
                f"${activity['amount']:,.2f}",
                activity['details']
            ))

    def setup_activity_tracking(self):
        """Setup auto-logout timer"""
        self.last_activity = datetime.now()
        self.root.bind_all("<Key>", self.reset_activity_timer)
        self.root.bind_all("<Button>", self.reset_activity_timer)
        self.root.bind_all("<MouseWheel>", self.reset_activity_timer)
        self.check_activity()

    def reset_activity_timer(self, event=None):
        """Reset the activity timer"""
        self.last_activity = datetime.now()

    def check_activity(self):
        """Check for user inactivity"""
        inactive_time = datetime.now() - self.last_activity
        if inactive_time.seconds > 1800:  # 30 minutes
            self.logout()
        else:
            self.root.after(60000, self.check_activity)  # Check every minute

    def update_time(self):
        """Update time display in status bar"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.config(text=current_time)
        self.root.after(1000, self.update_time)

    def show_change_password(self):
        """Show change password dialog"""
        ChangePasswordDialog(self.root, self.services['auth'], self.user_data['id'])

    def show_manual(self):
        """Show user manual"""
        UserManualDialog(self.root)

    def show_about(self):
        """Show about dialog"""
        messagebox.showinfo(
            "About",
            "Brew and Bite Café Management System\n"
            "Version 1.0.0\n\n"
            "© 2024 All rights reserved"
        )

    def logout(self):
        """Handle user logout"""
        try:
            self.auth_service.logout(self.user_data['id'])
            self.root.destroy()
            from src.gui.login_window import LoginWindow
            login = LoginWindow()
            login.run()
        except Exception as e:
            logger.error(f"Logout error: {str(e)}")
            messagebox.showerror("Error", "Failed to logout properly")

    def quit_app(self):
        """Quit application"""
        if messagebox.askyesno("Quit", "Are you sure you want to quit?"):
            try:
                self.auth_service.logout(self.user_data['id'])
            except:
                pass
            self.root.quit()

    def run(self):
        """Start the main window"""
        self.root.mainloop()