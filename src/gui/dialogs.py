import tkinter as tk
from tkinter import ttk, messagebox
import logging
from datetime import datetime
import webbrowser

logger = logging.getLogger(__name__)


class AboutDialog:
    def __init__(self, parent):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("About")
        self.dialog.geometry("400x500")
        self.dialog.resizable(False, False)
        self.dialog.grab_set()

        self.create_widgets()

        # Center dialog on parent
        self.dialog.transient(parent)
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - self.dialog.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.dialog.winfo_height()) // 2
        self.dialog.geometry(f"+{x}+{y}")

    def create_widgets(self):
        """Create dialog widgets"""
        # Logo/App name
        ttk.Label(
            self.dialog,
            text="Brew and Bite Café",
            font=("Helvetica", 20, "bold")
        ).pack(pady=20)

        ttk.Label(
            self.dialog,
            text="Management System",
            font=("Helvetica", 12)
        ).pack()

        # Version info
        info_frame = ttk.Frame(self.dialog, padding=20)
        info_frame.pack(fill="x")

        info = [
            ("Version:", "1.0.0"),
            ("Release Date:", "January 2024"),
            ("License:", "Proprietary"),
            ("Database:", "SQLite 3"),
            ("Python Version:", "3.11")
        ]

        for label, value in info:
            ttk.Label(
                info_frame,
                text=label,
                font=("Helvetica", 10, "bold")
            ).pack(anchor="w", pady=2)
            ttk.Label(
                info_frame,
                text=value
            ).pack(anchor="w", pady=(0, 5))

        # Credits
        ttk.Label(
            self.dialog,
            text="Developed by:",
            font=("Helvetica", 10, "bold")
        ).pack(pady=(20, 5))

        ttk.Label(
            self.dialog,
            text="Frederick Opoku Afriyie"
        ).pack()

        # Links
        link_frame = ttk.Frame(self.dialog)
        link_frame.pack(pady=20)

        ttk.Button(
            link_frame,
            text="Documentation",
            command=lambda: webbrowser.open("https://docs.brewandbite.com")
        ).pack(side="left", padx=5)

        ttk.Button(
            link_frame,
            text="Support",
            command=lambda: webbrowser.open("https://support.brewandbite.com")
        ).pack(side="left", padx=5)

        # Close button
        ttk.Button(
            self.dialog,
            text="Close",
            command=self.dialog.destroy
        ).pack(pady=20)


class UserManualDialog:
    def __init__(self, parent):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("User Manual")
        self.dialog.geometry("800x600")
        self.dialog.grab_set()

        self.create_widgets()

        # Center dialog
        self.dialog.transient(parent)
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - self.dialog.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.dialog.winfo_height()) // 2
        self.dialog.geometry(f"+{x}+{y}")

    def create_widgets(self):
        """Create dialog widgets"""
        # Create notebook for different sections
        notebook = ttk.Notebook(self.dialog)
        notebook.pack(fill="both", expand=True, padx=10, pady=5)

        # Overview tab
        overview_tab = ttk.Frame(notebook)
        notebook.add(overview_tab, text="Overview")

        ttk.Label(
            overview_tab,
            text="Brew and Bite Café Management System",
            font=("Helvetica", 16, "bold")
        ).pack(pady=20)

        overview_text = """
        Welcome to the Brew and Bite Café Management System!

        This application helps you manage your café operations effectively by providing:
        • Sales tracking and management
        • Inventory control
        • Expense management
        • Financial reporting
        • User management

        Each module is designed to be intuitive and easy to use while providing
        powerful features for managing your business.
        """

        ttk.Label(
            overview_tab,
            text=overview_text,
            wraplength=700,
            justify="left"
        ).pack(padx=20, pady=10)

        # Create tabs for each main feature
        self.create_sales_tab(notebook)
        self.create_inventory_tab(notebook)
        self.create_expenses_tab(notebook)
        self.create_reports_tab(notebook)
        self.create_settings_tab(notebook)

        # Close button
        ttk.Button(
            self.dialog,
            text="Close",
            command=self.dialog.destroy
        ).pack(pady=10)

    def create_sales_tab(self, notebook):
        """Create sales documentation tab"""
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="Sales")

        content = ttk.Frame(tab, padding=20)
        content.pack(fill="both", expand=True)

        # Add sales documentation
        sections = [
            ("Recording Sales", """
            To record a new sale:
            1. Click the "New Sale" button
            2. Select items from inventory
            3. Specify quantities
            4. Choose payment method
            5. Complete the sale

            The system will automatically update inventory and generate a receipt.
            """),

            ("Managing Sales History", """
            View and manage past sales:
            • Filter by date range
            • Search by transaction ID
            • Export sales reports
            • Void transactions (requires manager approval)
            """),

            ("Reports & Analytics", """
            The sales module provides:
            • Daily sales summaries
            • Best-selling items
            • Payment method breakdown
            • Staff performance metrics
            """)
        ]

        for title, text in sections:
            ttk.Label(
                content,
                text=title,
                font=("Helvetica", 12, "bold")
            ).pack(anchor="w", pady=(10, 5))

            ttk.Label(
                content,
                text=text,
                wraplength=700,
                justify="left"
            ).pack(anchor="w", padx=20, pady=(0, 10))

    def create_inventory_tab(self, notebook):
        """Create inventory documentation tab"""
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="Inventory")

        content = ttk.Frame(tab, padding=20)
        content.pack(fill="both", expand=True)

        sections = [
            ("Managing Stock", """
            Keep track of your inventory:
            1. Add new items with details
            2. Update quantities
            3. Set reorder levels
            4. Track stock movements

            The system will alert you when items are running low.
            """),

            ("Stock Adjustments", """
            Adjust inventory levels:
            • Record new stock arrivals
            • Handle damaged/expired items
            • Transfer stock
            • Conduct stock takes
            """),

            ("Reports", """
            Monitor your inventory:
            • Current stock levels
            • Stock movement history
            • Low stock alerts
            • Valuation reports
            """)
        ]

        for title, text in sections:
            ttk.Label(
                content,
                text=title,
                font=("Helvetica", 12, "bold")
            ).pack(anchor="w", pady=(10, 5))

            ttk.Label(
                content,
                text=text,
                wraplength=700,
                justify="left"
            ).pack(anchor="w", padx=20, pady=(0, 10))

    def create_expenses_tab(self, notebook):
        """Create expenses documentation tab"""
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="Expenses")

        content = ttk.Frame(tab, padding=20)
        content.pack(fill="both", expand=True)

        sections = [
            ("Recording Expenses", """
            Track all business expenses:
            1. Select expense category
            2. Enter amount and details
            3. Attach receipts (optional)
            4. Save the record

            Expenses are categorized for better tracking.
            """),

            ("Categories", """
            Manage expense categories:
            • Create custom categories
            • Set budgets
            • Track spending by category
            • Generate category reports
            """),

            ("Analysis", """
            Analyze your expenses:
            • Monthly summaries
            • Category breakdown
            • Budget vs. Actual
            • Trend analysis
            """)
        ]

        for title, text in sections:
            ttk.Label(
                content,
                text=title,
                font=("Helvetica", 12, "bold")
            ).pack(anchor="w", pady=(10, 5))

            ttk.Label(
                content,
                text=text,
                wraplength=700,
                justify="left"
            ).pack(anchor="w", padx=20, pady=(0, 10))

    def create_reports_tab(self, notebook):
        """Create reports documentation tab"""
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="Reports")

        content = ttk.Frame(tab, padding=20)
        content.pack(fill="both", expand=True)

        sections = [
            ("Available Reports", """
            The system provides various reports:
            • Daily Sales Summary
            • Inventory Status
            • Expense Analysis
            • Profit & Loss
            • Staff Performance
            """),

            ("Generating Reports", """
            To generate a report:
            1. Select report type
            2. Choose date range
            3. Apply any filters
            4. Generate report
            5. Export if needed
            """),

            ("Customization", """
            Customize your reports:
            • Select specific metrics
            • Choose display format
            • Save report templates
            • Schedule automated reports
            """)
        ]

        for title, text in sections:
            ttk.Label(
                content,
                text=title,
                font=("Helvetica", 12, "bold")
            ).pack(anchor="w", pady=(10, 5))

            ttk.Label(
                content,
                text=text,
                wraplength=700,
                justify="left"
            ).pack(anchor="w", padx=20, pady=(0, 10))

    def create_settings_tab(self, notebook):
        """Create settings documentation tab"""
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="Settings")

        content = ttk.Frame(tab, padding=20)
        content.pack(fill="both", expand=True)

        sections = [
            ("User Management", """
            Manage system users:
            • Add/remove users
            • Set permissions
            • Reset passwords
            • View user activity
            """),

            ("System Settings", """
            Configure the system:
            • Email settings
            • Backup options
            • Display preferences
            • Regional settings
            """),

            ("Data Management", """
            Manage your data:
            • Create backups
            • Restore from backup
            • Export data
            • Clear old records
            """)
        ]

        for title, text in sections:
            ttk.Label(
                content,
                text=title,
                font=("Helvetica", 12, "bold")
            ).pack(anchor="w", pady=(10, 5))

            ttk.Label(
                content,
                text=text,
                wraplength=700,
                justify="left"
            ).pack(anchor="w", padx=20, pady=(0, 10))


class ChangePasswordDialog:
    def __init__(self, parent, auth_service, user_id):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Change Password")
        self.dialog.geometry("400x300")
        self.dialog.grab_set()

        self.auth_service = auth_service
        self.user_id = user_id

        self.create_widgets()

        # Center dialog
        self.dialog.transient(parent)
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - self.dialog.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.dialog.winfo_height()) // 2
        self.dialog.geometry(f"+{x}+{y}")

    def create_widgets(self):
        """Create dialog widgets"""
        form_frame = ttk.Frame(self.dialog, padding=20)
        form_frame.pack(fill="both", expand=True)

        # Current password
        ttk.Label(
            form_frame,
            text="Current Password:"
        ).pack(anchor="w", pady=(0, 5))

        self.current_password_var = tk.StringVar()
        ttk.Entry(
            form_frame,
            textvariable=self.current_password_var,
            show="*",
            width=30
        ).pack(fill="x", pady=(0, 10))

        # New password
        ttk.Label(
            form_frame,
            text="New Password:"
        ).pack(anchor="w", pady=(0, 5))

        self.new_password_var = tk.StringVar()
        ttk.Entry(
            form_frame,
            textvariable=self.new_password_var,
            show="*",
            width=30
        ).pack(fill="x", pady=(0, 10))

        # Confirm new password
        ttk.Label(
            form_frame,
            text="Confirm New Password:"
        ).pack(anchor="w", pady=(0, 5))

        self.confirm_password_var = tk.StringVar()
        ttk.Entry(
            form_frame,
            textvariable=self.confirm_password_var,
            show="*",
            width=30
        ).pack(fill="x", pady=(0, 10))

        # Password requirements
        ttk.Label(
            form_frame,
            text="Password must contain:",
            font=("Helvetica", 9, "bold")
        ).pack(anchor="w", pady=(10, 5))

        requirements_text = """
                • At least 8 characters
                • One uppercase letter
                • One lowercase letter
                • One number
                • One special character
                """

        ttk.Label(
            form_frame,
            text=requirements_text,
            font=("Helvetica", 9),
            justify="left"
        ).pack(anchor="w", padx=20)

        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.pack(pady=20)

        ttk.Button(
            button_frame,
            text="Change Password",
            command=self.change_password
        ).pack(side="left", padx=5)

        ttk.Button(
            button_frame,
            text="Cancel",
            command=self.dialog.destroy
        ).pack(side="left", padx=5)

    def change_password(self):
        """Handle password change"""
        try:
            current_password = self.current_password_var.get()
            new_password = self.new_password_var.get()
            confirm_password = self.confirm_password_var.get()

            # Validate inputs
            if not all([current_password, new_password, confirm_password]):
                raise ValueError("All fields are required")

            if new_password != confirm_password:
                raise ValueError("New passwords do not match")

            # Attempt to change password
            success = self.auth_service.change_password(
                user_id=self.user_id,
                current_password=current_password,
                new_password=new_password
            )

            if success:
                messagebox.showinfo(
                    "Success",
                    "Password changed successfully!"
                )
                self.dialog.destroy()
            else:
                messagebox.showerror(
                    "Error",
                    "Failed to change password. Please check your current password."
                )

        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            logger.error(f"Error changing password: {str(e)}")
            messagebox.showerror("Error", "Failed to change password")

    class BackupDialog:
        def __init__(self, parent, settings_service):
            self.dialog = tk.Toplevel(parent)
            self.dialog.title("Database Backup")
            self.dialog.geometry("500x400")
            self.dialog.grab_set()

            self.settings_service = settings_service

            self.create_widgets()

            # Center dialog
            self.dialog.transient(parent)
            self.dialog.update_idletasks()
            x = parent.winfo_x() + (parent.winfo_width() - self.dialog.winfo_width()) // 2
            y = parent.winfo_y() + (parent.winfo_height() - self.dialog.winfo_height()) // 2
            self.dialog.geometry(f"+{x}+{y}")

        def create_widgets(self):
            """Create dialog widgets"""
            content_frame = ttk.Frame(self.dialog, padding=20)
            content_frame.pack(fill="both", expand=True)

            # Heading
            ttk.Label(
                content_frame,
                text="Database Backup",
                font=("Helvetica", 14, "bold")
            ).pack(pady=(0, 20))

            # Backup location
            location_frame = ttk.Frame(content_frame)
            location_frame.pack(fill="x", pady=5)

            ttk.Label(
                location_frame,
                text="Backup Location:"
            ).pack(side="left")

            self.location_var = tk.StringVar()
            ttk.Entry(
                location_frame,
                textvariable=self.location_var,
                width=40
            ).pack(side="left", padx=5)

            ttk.Button(
                location_frame,
                text="Browse",
                command=self.browse_location
            ).pack(side="left")

            # Backup options
            options_frame = ttk.LabelFrame(content_frame, text="Backup Options")
            options_frame.pack(fill="x", pady=20)

            # Compress backup
            self.compress_var = tk.BooleanVar(value=True)
            ttk.Checkbutton(
                options_frame,
                text="Compress backup file",
                variable=self.compress_var
            ).pack(anchor="w", padx=10, pady=5)

            # Include attachments
            self.attachments_var = tk.BooleanVar(value=True)
            ttk.Checkbutton(
                options_frame,
                text="Include attachments and media files",
                variable=self.attachments_var
            ).pack(anchor="w", padx=10, pady=5)

            # Schedule frame
            schedule_frame = ttk.LabelFrame(content_frame, text="Backup Schedule")
            schedule_frame.pack(fill="x", pady=20)

            # Enable scheduling
            self.schedule_var = tk.BooleanVar(value=False)
            ttk.Checkbutton(
                schedule_frame,
                text="Enable automatic backups",
                variable=self.schedule_var,
                command=self.toggle_schedule_options
            ).pack(anchor="w", padx=10, pady=5)

            # Schedule options
            self.schedule_options = ttk.Frame(schedule_frame)
            self.schedule_options.pack(fill="x", padx=10, pady=5)

            ttk.Label(
                self.schedule_options,
                text="Frequency:"
            ).pack(side="left")

            self.frequency_var = tk.StringVar(value="daily")
            ttk.Combobox(
                self.schedule_options,
                textvariable=self.frequency_var,
                values=["daily", "weekly", "monthly"],
                state="readonly",
                width=15
            ).pack(side="left", padx=5)

            # Initially disable schedule options
            self.toggle_schedule_options()

            # Buttons
            button_frame = ttk.Frame(content_frame)
            button_frame.pack(pady=20)

            ttk.Button(
                button_frame,
                text="Start Backup",
                command=self.start_backup
            ).pack(side="left", padx=5)

            ttk.Button(
                button_frame,
                text="Cancel",
                command=self.dialog.destroy
            ).pack(side="left", padx=5)

        def browse_location(self):
            """Browse for backup location"""
            directory = tk.filedialog.askdirectory(
                title="Select Backup Location"
            )
            if directory:
                self.location_var.set(directory)

        def toggle_schedule_options(self):
            """Enable/disable schedule options"""
            for child in self.schedule_options.winfo_children():
                child.configure(state="normal" if self.schedule_var.get() else "disabled")

        def start_backup(self):
            """Start the backup process"""
            try:
                location = self.location_var.get()
                if not location:
                    raise ValueError("Please select a backup location")

                options = {
                    'location': location,
                    'compress': self.compress_var.get(),
                    'include_attachments': self.attachments_var.get(),
                    'schedule': {
                        'enabled': self.schedule_var.get(),
                        'frequency': self.frequency_var.get() if self.schedule_var.get() else None
                    }
                }

                # Create backup
                backup_file = self.settings_service.create_backup(options)

                messagebox.showinfo(
                    "Success",
                    f"Backup created successfully!\nLocation: {backup_file}"
                )
                self.dialog.destroy()

            except ValueError as e:
                messagebox.showerror("Error", str(e))
            except Exception as e:
                logger.error(f"Error creating backup: {str(e)}")
                messagebox.showerror("Error", "Failed to create backup")

    # Update dialog boxes registry
    dialogs = {
        'about': AboutDialog,
        'user_manual': UserManualDialog,
        'change_password': ChangePasswordDialog,
        'backup': BackupDialog
    }