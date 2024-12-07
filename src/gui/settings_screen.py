import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import logging
from datetime import datetime
from src.database.models import UserRole
from src.config import APP_NAME, APP_VERSION

logger = logging.getLogger(__name__)

class SettingsScreen(ttk.Frame):
    def __init__(self, parent, services):
        super().__init__(parent)
        self.parent = parent
        self.services = services

        # Verify admin access
        if not self.verify_admin_access():
            messagebox.showerror(
                "Access Denied",
                "You do not have permission to access settings."
            )
            return

        self.create_widgets()
        self.load_settings()

    def verify_admin_access(self) -> bool:
        """Verify current user has admin access"""
        try:
            has_permission, _ = self.services['auth'].check_permission(1, UserRole.ADMIN)
            return has_permission
        except Exception as e:
            logger.error(f"Error verifying admin access: {str(e)}")
            return False

    def create_widgets(self):
        """Create and arrange widgets"""
        # Create notebook for different settings sections
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=5)

        # Create settings tabs
        self.create_general_tab()
        self.create_backup_tab()
        self.create_audit_tab()
        self.create_email_tab()

        # Pack main frame
        self.pack(fill="both", expand=True)

    def create_general_tab(self):
        """Create general settings tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="General")

        # App info section
        info_frame = ttk.LabelFrame(tab, text="Application Information")
        info_frame.pack(fill="x", padx=10, pady=5)

        info = [
            ("Application Name:", APP_NAME),
            ("Version:", APP_VERSION),
            ("Last Database Backup:", self.get_last_backup_date())
        ]

        for i, (label, value) in enumerate(info):
            ttk.Label(
                info_frame,
                text=label,
                font=("Helvetica", 10, "bold")
            ).grid(row=i, column=0, padx=5, pady=5, sticky="e")
            ttk.Label(
                info_frame,
                text=value
            ).grid(row=i, column=1, padx=5, pady=5, sticky="w")

        # Session settings
        session_frame = ttk.LabelFrame(tab, text="Session Settings")
        session_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(session_frame, text="Session Timeout (minutes):").pack(side="left", padx=5)
        self.timeout_var = tk.StringVar(value="30")
        ttk.Entry(
            session_frame,
            textvariable=self.timeout_var,
            width=10
        ).pack(side="left", padx=5)

        ttk.Button(
            session_frame,
            text="Apply",
            command=self.update_session_timeout
        ).pack(side="left", padx=5)

        # Display settings
        display_frame = ttk.LabelFrame(tab, text="Display Settings")
        display_frame.pack(fill="x", padx=10, pady=5)

        # Theme selection
        ttk.Label(display_frame, text="Theme:").pack(side="left", padx=5)
        self.theme_var = tk.StringVar(value="Default")
        ttk.Combobox(
            display_frame,
            textvariable=self.theme_var,
            values=["Default", "Light", "Dark"],
            state="readonly",
            width=15
        ).pack(side="left", padx=5)

        ttk.Button(
            display_frame,
            text="Apply",
            command=self.update_theme
        ).pack(side="left", padx=5)

    def create_backup_tab(self):
        """Create backup & restore tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Backup & Restore")

        # Backup section
        backup_frame = ttk.LabelFrame(tab, text="Database Backup")
        backup_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(
            backup_frame,
            text="Create a backup of the database and settings"
        ).pack(pady=5)

        backup_buttons = ttk.Frame(backup_frame)
        backup_buttons.pack(pady=10)

        ttk.Button(
            backup_buttons,
            text="Create Manual Backup",
            command=self.create_backup
        ).pack(side="left", padx=5)

        ttk.Button(
            backup_buttons,
            text="Schedule Automatic Backup",
            command=self.schedule_backup
        ).pack(side="left", padx=5)

        # Auto-backup settings
        auto_frame = ttk.Frame(backup_frame)
        auto_frame.pack(fill="x", pady=10)

        ttk.Label(auto_frame, text="Auto-backup frequency:").pack(side="left", padx=5)
        self.backup_freq_var = tk.StringVar(value="daily")
        ttk.Combobox(
            auto_frame,
            textvariable=self.backup_freq_var,
            values=["daily", "weekly", "monthly"],
            state="readonly",
            width=15
        ).pack(side="left", padx=5)

        # Restore section
        restore_frame = ttk.LabelFrame(tab, text="Database Restore")
        restore_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(
            restore_frame,
            text="Restore database from a backup file\n"
            "Warning: This will replace the current database",
            justify="center"
        ).pack(pady=5)

        ttk.Button(
            restore_frame,
            text="Restore from Backup",
            command=self.restore_database
        ).pack(pady=10)

        # Backup history
        history_frame = ttk.LabelFrame(tab, text="Backup History")
        history_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Create backup history treeview
        columns = ("Date", "Size", "Type", "Status")
        self.backup_tree = ttk.Treeview(
            history_frame,
            columns=columns,
            show="headings"
        )

        for col in columns:
            self.backup_tree.heading(col, text=col)
            self.backup_tree.column(col, width=100)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(
            history_frame,
            orient="vertical",
            command=self.backup_tree.yview
        )
        self.backup_tree.configure(yscrollcommand=scrollbar.set)

        self.backup_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def create_audit_tab(self):
        """Create audit log tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Audit Log")

        # Controls frame
        controls_frame = ttk.Frame(tab)
        controls_frame.pack(fill="x", padx=10, pady=5)

        # Date range
        ttk.Label(controls_frame, text="Date Range:").pack(side="left")
        self.audit_start_var = tk.StringVar(
            value=datetime.now().strftime("%Y-%m-%d")
        )
        ttk.Entry(
            controls_frame,
            textvariable=self.audit_start_var,
            width=10
        ).pack(side="left", padx=5)

        ttk.Label(controls_frame, text="to").pack(side="left")
        self.audit_end_var = tk.StringVar(
            value=datetime.now().strftime("%Y-%m-%d")
        )
        ttk.Entry(
            controls_frame,
            textvariable=self.audit_end_var,
            width=10
        ).pack(side="left", padx=5)

        # Action filter
        ttk.Label(controls_frame, text="Action:").pack(side="left", padx=(20, 5))
        self.action_var = tk.StringVar(value="All")
        ttk.Combobox(
            controls_frame,
            textvariable=self.action_var,
            values=["All", "CREATE", "UPDATE", "DELETE", "LOGIN", "LOGOUT"],
            state="readonly",
            width=15
        ).pack(side="left", padx=5)

        # Search button
        ttk.Button(
            controls_frame,
            text="Search",
            command=self.load_audit_logs
        ).pack(side="left", padx=5)

        # Export button
        ttk.Button(
            controls_frame,
            text="Export",
            command=self.export_audit_logs
        ).pack(side="right", padx=5)

        # Create audit log treeview
        columns = ("Timestamp", "User", "Action", "Details")
        self.audit_tree = ttk.Treeview(
            tab,
            columns=columns,
            show="headings"
        )

        self.audit_tree.heading("Timestamp", text="Timestamp")
        self.audit_tree.column("Timestamp", width=150)
        self.audit_tree.heading("User", text="User")
        self.audit_tree.column("User", width=100)
        self.audit_tree.heading("Action", text="Action")
        self.audit_tree.column("Action", width=100)
        self.audit_tree.heading("Details", text="Details")
        self.audit_tree.column("Details", width=400)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(
            tab,
            orient="vertical",
            command=self.audit_tree.yview
        )
        self.audit_tree.configure(yscrollcommand=scrollbar.set)

        # Pack treeview and scrollbar
        self.audit_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def create_email_tab(self):
        """Create email settings tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Email Settings")

        # Email server settings
        server_frame = ttk.LabelFrame(tab, text="Email Server Settings")
        server_frame.pack(fill="x", padx=10, pady=5)

        # SMTP Server
        ttk.Label(server_frame, text="SMTP Server:").pack(anchor="w", pady=(10, 0))
        self.smtp_server_var = tk.StringVar()
        ttk.Entry(
            server_frame,
            textvariable=self.smtp_server_var,
            width=40
        ).pack(fill="x", padx=5, pady=5)

        # Port
        ttk.Label(server_frame, text="Port:").pack(anchor="w")
        self.smtp_port_var = tk.StringVar()
        ttk.Entry(
            server_frame,
            textvariable=self.smtp_port_var,
            width=10
        ).pack(anchor="w", padx=5, pady=5)

        # Sender email
        ttk.Label(server_frame, text="Sender Email:").pack(anchor="w")
        self.sender_email_var = tk.StringVar()
        ttk.Entry(
            server_frame,
            textvariable=self.sender_email_var,
            width=40
        ).pack(fill="x", padx=5, pady=5)

        # Password
        ttk.Label(server_frame, text="Password:").pack(anchor="w")
        self.email_password_var = tk.StringVar()
        ttk.Entry(
            server_frame,
            textvariable=self.email_password_var,
            show="*",
            width=40
        ).pack(fill="x", padx=5, pady=5)

        # SSL/TLS
        self.use_tls_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            server_frame,
            text="Use SSL/TLS",
            variable=self.use_tls_var
        ).pack(anchor="w", padx=5, pady=5)

        # Test and save buttons
        button_frame = ttk.Frame(server_frame)
        button_frame.pack(pady=10)

        ttk.Button(
            button_frame,
            text="Test Connection",
            command=self.test_email_connection
        ).pack(side="left", padx=5)

        ttk.Button(
            button_frame,
            text="Save Settings",
            command=self.save_email_settings
        ).pack(side="left", padx=5)

        # Email templates
        template_frame = ttk.LabelFrame(tab, text="Email Templates")
        template_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Template selection
        ttk.Label(template_frame, text="Select Template:").pack(anchor="w", pady=(10, 0))
        self.template_var = tk.StringVar()
        templates = [
            "Password Reset",
            "New User Welcome",
            "Account Deactivation",
            "Low Stock Alert"
        ]
        template_combo = ttk.Combobox(
            template_frame,
            textvariable=self.template_var,
            values=templates,
            state="readonly",
            width=30
        )
        template_combo.pack(anchor="w", padx=5, pady=5)
        template_combo.bind('<<ComboboxSelected>>', self.load_template)

        # Template content
        ttk.Label(template_frame, text="Subject:").pack(anchor="w")
        self.subject_var = tk.StringVar()
        ttk.Entry(
            template_frame,
            textvariable=self.subject_var,
            width=60
        ).pack(fill="x", padx=5, pady=5)

        ttk.Label(template_frame, text="Content:").pack(anchor="w")
        self.content_text = tk.Text(template_frame, height=10)
        self.content_text.pack(fill="both", expand=True, padx=5, pady=5)

        # Template buttons
        template_buttons = ttk.Frame(template_frame)
        template_buttons.pack(pady=10)

        ttk.Button(
            template_buttons,
            text="Save Template",
            command=self.save_template
        ).pack(side="left", padx=5)

        ttk.Button(
            template_buttons,
            text="Reset to Default",
            command=self.reset_template
        ).pack(side="left", padx=5)

    def load_settings(self):
        """Load current settings"""
        try:
            # Load general settings
            settings = self.services['settings'].get_settings()

            # Set session timeout
            self.timeout_var.set(str(settings.get('session_timeout', 30)))

            # Set theme
            self.theme_var.set(settings.get('theme', 'Default'))

            # Set backup frequency
            self.backup_freq_var.set(settings.get('backup_frequency', 'daily'))

            # Load email settings
            self.smtp_server_var.set(settings.get('smtp_server', ''))
            self.smtp_port_var.set(str(settings.get('smtp_port', 587)))
            self.sender_email_var.set(settings.get('sender_email', ''))
            self.email_password_var.set(settings.get('email_password', ''))
            self.use_tls_var.set(settings.get('use_tls', True))

            # Load backup history
            self.load_backup_history()

            # Load audit logs
            self.load_audit_logs()

        except Exception as e:
            logger.error(f"Error loading settings: {str(e)}")
            messagebox.showerror("Error", "Failed to load settings")

    def get_last_backup_date(self) -> str:
        """Get the date of the last backup"""
        try:
            last_backup = self.services['settings'].get_last_backup_date()
            return last_backup.strftime("%Y-%m-%d %H:%M:%S") if last_backup else "Never"
        except Exception as e:
            logger.error(f"Error getting last backup date: {str(e)}")
            return "Unknown"

    def update_session_timeout(self):
        """Update session timeout setting"""
        try:
            timeout = int(self.timeout_var.get())
            if timeout < 1:
                raise ValueError("Timeout must be at least 1 minute")

            self.services['settings'].update_setting(
                'session_timeout',
                timeout,
                audit_user_id=1  # TODO: Get actual user ID
            )

            messagebox.showinfo("Success", "Session timeout updated successfully!")

        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            logger.error(f"Error updating session timeout: {str(e)}")
            messagebox.showerror("Error", "Failed to update session timeout")

    def update_theme(self):
        """Update application theme"""
        try:
            theme = self.theme_var.get()
            self.services['settings'].update_setting(
                'theme',
                theme,
                audit_user_id=1  # TODO: Get actual user ID
            )

            # Apply theme changes
            self.apply_theme(theme)

            messagebox.showinfo("Success", "Theme updated successfully!")

        except Exception as e:
            logger.error(f"Error updating theme: {str(e)}")
            messagebox.showerror("Error", "Failed to update theme")

    def apply_theme(self, theme: str):
        """Apply selected theme to application"""
        # TODO: Implement theme application
        pass

    def create_backup(self):
        """Create manual database backup"""
        try:
            # Get backup directory from user
            backup_dir = filedialog.askdirectory(
                title="Select Backup Directory"
            )

            if backup_dir:
                backup_file = self.services['settings'].create_backup(backup_dir)
                messagebox.showinfo(
                    "Success",
                    f"Backup created successfully!\nLocation: {backup_file}"
                )

                # Refresh backup history
                self.load_backup_history()

        except Exception as e:
            logger.error(f"Error creating backup: {str(e)}")
            messagebox.showerror("Error", "Failed to create backup")

    def schedule_backup(self):
        """Schedule automatic database backup"""
        try:
            frequency = self.backup_freq_var.get()
            self.services['settings'].schedule_backup(
                frequency,
                audit_user_id=1  # TODO: Get actual user ID
            )

            messagebox.showinfo(
                "Success",
                f"Automatic backup scheduled ({frequency})"
            )

        except Exception as e:
            logger.error(f"Error scheduling backup: {str(e)}")
            messagebox.showerror("Error", "Failed to schedule backup")

    def restore_database(self):
        """Restore database from backup"""
        try:
            if messagebox.askyesno(
                "Confirm Restore",
                "This will replace the current database with the selected backup.\n"
                "Are you sure you want to continue?"
            ):
                # Get backup file from user
                backup_file = filedialog.askopenfilename(
                    title="Select Backup File",
                    filetypes=[("Database Backup", "*.bak")]
                )

                if backup_file:
                    self.services['settings'].restore_backup(
                        backup_file,
                        audit_user_id=1  # TODO: Get actual user ID
                    )

                    messagebox.showinfo(
                        "Success",
                        "Database restored successfully!\n"
                        "The application will now restart."
                    )

                    # Restart application
                    self.restart_application()

        except Exception as e:
            logger.error(f"Error restoring database: {str(e)}")
            messagebox.showerror("Error", "Failed to restore database")

    def load_backup_history(self):
        """Load backup history into treeview"""
        try:
            # Clear existing items
            for item in self.backup_tree.get_children():
                self.backup_tree.delete(item)

            # Get backup history
            history = self.services['settings'].get_backup_history()

            # Add backups to treeview
            for backup in history:
                self.backup_tree.insert("", "end", values=(
                    backup['date'],
                    backup['size'],
                    backup['type'],
                    backup['status']
                ))

        except Exception as e:
            logger.error(f"Error loading backup history: {str(e)}")
            messagebox.showerror("Error", "Failed to load backup history")

    def load_audit_logs(self):
        """Load audit logs into treeview"""
        try:
            # Clear existing items
            for item in self.audit_tree.get_children():
                self.audit_tree.delete(item)

            # Get audit logs
            logs = self.services['settings'].get_audit_logs(
                start_date=self.audit_start_var.get(),
                end_date=self.audit_end_var.get(),
                action=self.action_var.get() if self.action_var.get() != "All" else None
            )

            # Add logs to treeview
            for log in logs:
                self.audit_tree.insert("", 0, values=(
                    log['timestamp'],
                    log['username'],
                    log['action'],
                    log['details']
                ))

        except Exception as e:
            logger.error(f"Error loading audit logs: {str(e)}")
            messagebox.showerror("Error", "Failed to load audit logs")

    def export_audit_logs(self):
        """Export audit logs to CSV"""
        try:
            # Get file location from user
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV Files", "*.csv")],
                initialfile="audit_logs.csv"
            )

            if filename:
                self.services['settings'].export_audit_logs(
                    filename,
                    start_date=self.audit_start_var.get(),
                    end_date=self.audit_end_var.get(),
                    action=self.action_var.get() if self.action_var.get() != "All" else None
                )

                messagebox.showinfo(
                    "Success",
                    "Audit logs exported successfully!"
                )

        except Exception as e:
            logger.error(f"Error exporting audit logs: {str(e)}")
            messagebox.showerror("Error", "Failed to export audit logs")

    def test_email_connection(self):
        """Test SMTP connection with current settings"""
        try:
            settings = {
                'smtp_server': self.smtp_server_var.get(),
                'smtp_port': int(self.smtp_port_var.get()),
                'sender_email': self.sender_email_var.get(),
                'email_password': self.email_password_var.get(),
                'use_tls': self.use_tls_var.get()
            }

            self.services['settings'].test_email_connection(settings)
            messagebox.showinfo("Success", "Email connection test successful!")

        except Exception as e:
            logger.error(f"Error testing email connection: {str(e)}")
            messagebox.showerror("Error", f"Connection test failed: {str(e)}")

    def save_email_settings(self):
        """Save email settings"""
        try:
            settings = {
                'smtp_server': self.smtp_server_var.get(),
                'smtp_port': int(self.smtp_port_var.get()),
                'sender_email': self.sender_email_var.get(),
                'email_password': self.email_password_var.get(),
                'use_tls': self.use_tls_var.get()
            }

            self.services['settings'].update_email_settings(
                settings,
                audit_user_id=1  # TODO: Get actual user ID
            )

            messagebox.showinfo("Success", "Email settings saved successfully!")

        except Exception as e:
            logger.error(f"Error saving email settings: {str(e)}")
            messagebox.showerror("Error", "Failed to save email settings")

    def load_template(self, event=None):
        """Load selected email template"""
        try:
            template = self.services['settings'].get_email_template(
                self.template_var.get()
            )

            self.subject_var.set(template['subject'])
            self.content_text.delete(1.0, tk.END)
            self.content_text.insert(1.0, template['content'])

        except Exception as e:
            logger.error(f"Error loading template: {str(e)}")
            messagebox.showerror("Error", "Failed to load template")

    def save_template(self):
        """Save current email template"""
        try:
            template = {
                'name': self.template_var.get(),
                'subject': self.subject_var.get(),
                'content': self.content_text.get(1.0, tk.END).strip()
            }

            self.services['settings'].save_email_template(
                template,
                audit_user_id=1  # TODO: Get actual user ID
            )

            messagebox.showinfo("Success", "Template saved successfully!")

        except Exception as e:
            logger.error(f"Error saving template: {str(e)}")
            messagebox.showerror("Error", "Failed to save template")

    def reset_template(self):
        """Reset selected template to default"""
        try:
            if messagebox.askyesno(
                "Confirm Reset",
                "Are you sure you want to reset this template to default?"
            ):
                self.services['settings'].reset_email_template(
                    self.template_var.get(),
                    audit_user_id=1  # TODO: Get actual user ID
                )

                # Reload template
                self.load_template()

                messagebox.showinfo("Success", "Template reset successfully!")

        except Exception as e:
            logger.error(f"Error resetting template: {str(e)}")
            messagebox.showerror("Error", "Failed to reset template")

    def restart_application(self):
        """Restart the application"""
        # TODO: Implement application restart
        pass

    def cleanup(self):
        """Clean up resources"""
        pass