import tkinter as tk
from tkinter import ttk, messagebox
import logging
from datetime import datetime
from src.database.models import UserRole

logger = logging.getLogger(__name__)


class UserManagementScreen(ttk.Frame):
    def __init__(self, parent, services):
        super().__init__(parent)
        self.parent = parent
        self.services = services
        self.selected_user = None

        # Verify admin access
        if not self.verify_admin_access():
            messagebox.showerror(
                "Access Denied",
                "You do not have permission to access user management."
            )
            return

        self.create_widgets()
        self.load_users()

    def verify_admin_access(self) -> bool:
        """Verify current user has admin access"""
        try:
            # TODO: Get actual user ID from session
            has_permission, _ = self.services['auth'].check_permission(1, UserRole.ADMIN)
            return has_permission
        except Exception as e:
            logger.error(f"Error verifying admin access: {str(e)}")
            return False

    def create_widgets(self):
        """Create and arrange widgets"""
        # Main heading
        heading_frame = ttk.Frame(self)
        heading_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(
            heading_frame,
            text="User Management",
            font=("Helvetica", 16, "bold")
        ).pack(side="left")

        ttk.Button(
            heading_frame,
            text="Add User",
            command=self.show_add_user_dialog
        ).pack(side="right")

        # Search frame
        search_frame = ttk.Frame(self)
        search_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(search_frame, text="Search:").pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.filter_users())
        search_entry = ttk.Entry(
            search_frame,
            textvariable=self.search_var,
            width=30
        )
        search_entry.pack(side="left", padx=5)

        ttk.Label(search_frame, text="Role:").pack(side="left", padx=(20, 5))
        self.role_var = tk.StringVar(value="All")
        role_combo = ttk.Combobox(
            search_frame,
            textvariable=self.role_var,
            values=["All"] + [role.value for role in UserRole],
            state="readonly",
            width=15
        )
        role_combo.pack(side="left", padx=5)
        role_combo.bind('<<ComboboxSelected>>', lambda e: self.filter_users())

        # Create users treeview
        columns = ("Username", "Email", "Role", "Last Login", "Status")
        self.users_tree = ttk.Treeview(
            self,
            columns=columns,
            show="headings",
            selectmode="browse"
        )

        # Configure columns
        self.users_tree.heading("Username", text="Username")
        self.users_tree.column("Username", width=150)
        self.users_tree.heading("Email", text="Email")
        self.users_tree.column("Email", width=200)
        self.users_tree.heading("Role", text="Role")
        self.users_tree.column("Role", width=100)
        self.users_tree.heading("Last Login", text="Last Login")
        self.users_tree.column("Last Login", width=150)
        self.users_tree.heading("Status", text="Status")
        self.users_tree.column("Status", width=100)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(
            self,
            orient="vertical",
            command=self.users_tree.yview
        )
        self.users_tree.configure(yscrollcommand=scrollbar.set)

        # Pack treeview and scrollbar
        self.users_tree.pack(side="left", fill="both", expand=True, padx=10, pady=5)
        scrollbar.pack(side="right", fill="y", pady=5)

        # Bind events
        self.users_tree.bind("<Button-3>", self.show_context_menu)
        self.users_tree.bind("<Double-1>", self.show_user_details)

        # Create context menu
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Edit User", command=self.show_edit_dialog)
        self.context_menu.add_command(label="Change Password", command=self.show_change_password_dialog)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Activate/Deactivate", command=self.toggle_user_status)
        self.context_menu.add_command(label="Reset Password", command=self.reset_user_password)

        # Pack main frame
        self.pack(fill="both", expand=True)

    def load_users(self):
        """Load users into treeview"""
        try:
            # Clear existing items
            for item in self.users_tree.get_children():
                self.users_tree.delete(item)

            # Get users
            users = self.services['user'].get_users()

            # Add users to treeview
            for user in users:
                self.users_tree.insert("", "end", values=(
                    user['username'],
                    user['email'],
                    user['role'],
                    user['last_login'] if user['last_login'] else "Never",
                    "Active" if user['is_active'] else "Inactive"
                ))

        except Exception as e:
            logger.error(f"Error loading users: {str(e)}")
            messagebox.showerror("Error", "Failed to load users")

    def filter_users(self):
        """Filter users based on search term and role"""
        try:
            search_term = self.search_var.get().lower()
            role_filter = self.role_var.get()

            # Show all items first
            for item in self.users_tree.get_children():
                self.users_tree.item(item, tags=())

            # Apply filters
            for item in self.users_tree.get_children():
                values = self.users_tree.item(item)['values']
                username = str(values[0]).lower()
                email = str(values[1]).lower()
                role = str(values[2])

                show_item = True

                # Apply search filter
                if search_term and search_term not in username and search_term not in email:
                    show_item = False

                # Apply role filter
                if role_filter != "All" and role_filter != role:
                    show_item = False

                # Hide or show item
                if show_item:
                    self.users_tree.item(item, tags=())
                else:
                    self.users_tree.detach(item)

        except Exception as e:
            logger.error(f"Error filtering users: {str(e)}")

    def show_context_menu(self, event):
        """Show context menu for selected user"""
        item = self.users_tree.identify_row(event.y)
        if item:
            self.users_tree.selection_set(item)
            self.selected_user = self.users_tree.item(item)['values']
            self.context_menu.post(event.x_root, event.y_root)

    def show_user_details(self, event=None):
        """Show details for selected user"""
        if not self.selected_user:
            return

        dialog = tk.Toplevel(self)
        dialog.title("User Details")
        dialog.geometry("400x300")
        dialog.grab_set()

        # Get full user details
        user = self.services['user'].get_user_details(self.selected_user[0])
        if user:
            # Create details view
            details_frame = ttk.Frame(dialog, padding="20")
            details_frame.pack(fill="both", expand=True)

            # Display user details
            details = [
                ("Username:", user['username']),
                ("Email:", user['email']),
                ("Role:", user['role']),
                ("Status:", "Active" if user['is_active'] else "Inactive"),
                ("Last Login:", user['last_login'] if user['last_login'] else "Never"),
                ("Created At:", user['created_at'])
            ]

            for i, (label, value) in enumerate(details):
                ttk.Label(
                    details_frame,
                    text=label,
                    font=("Helvetica", 10, "bold")
                ).grid(row=i, column=0, sticky="e", padx=5, pady=5)
                ttk.Label(
                    details_frame,
                    text=value
                ).grid(row=i, column=1, sticky="w", padx=5, pady=5)

            # Add close button
            ttk.Button(
                dialog,
                text="Close",
                command=dialog.destroy
            ).pack(pady=10)

    def show_add_user_dialog(self):
        """Show dialog to add new user"""
        dialog = tk.Toplevel(self)
        dialog.title("Add User")
        dialog.geometry("400x500")
        dialog.grab_set()

        # Create user form
        form_frame = ttk.Frame(dialog, padding="20")
        form_frame.pack(fill="both", expand=True)

        # Username field
        ttk.Label(form_frame, text="Username:").pack(anchor="w", pady=(0, 5))
        username_var = tk.StringVar()
        ttk.Entry(
            form_frame,
            textvariable=username_var,
            width=40
        ).pack(fill="x", pady=(0, 10))

        # Email field
        ttk.Label(form_frame, text="Email:").pack(anchor="w", pady=(0, 5))
        email_var = tk.StringVar()
        ttk.Entry(
            form_frame,
            textvariable=email_var,
            width=40
        ).pack(fill="x", pady=(0, 10))

        # Password field
        ttk.Label(form_frame, text="Password:").pack(anchor="w", pady=(0, 5))
        password_var = tk.StringVar()
        ttk.Entry(
            form_frame,
            textvariable=password_var,
            show="*",
            width=40
        ).pack(fill="x", pady=(0, 10))

        # Confirm password field
        ttk.Label(form_frame, text="Confirm Password:").pack(anchor="w", pady=(0, 5))
        confirm_password_var = tk.StringVar()
        ttk.Entry(
            form_frame,
            textvariable=confirm_password_var,
            show="*",
            width=40
        ).pack(fill="x", pady=(0, 10))

        # Role selection
        ttk.Label(form_frame, text="Role:").pack(anchor="w", pady=(0, 5))
        role_var = tk.StringVar(value=UserRole.STAFF.value)
        for role in UserRole:
            ttk.Radiobutton(
                form_frame,
                text=role.value.capitalize(),
                value=role.value,
                variable=role_var
            ).pack(anchor="w")

        def save_user():
            try:
                # Get form data
                username = username_var.get().strip()
                email = email_var.get().strip()
                password = password_var.get()
                confirm_password = confirm_password_var.get()
                role = UserRole(role_var.get())

                # Validate inputs
                if not all([username, email, password, confirm_password]):
                    raise ValueError("All fields are required")

                if password != confirm_password:
                    raise ValueError("Passwords do not match")

                # Create user
                self.services['user'].create_user(
                    username=username,
                    email=email,
                    password=password,
                    role=role
                )

                messagebox.showinfo("Success", "User created successfully!")
                dialog.destroy()

                # Refresh users list
                self.load_users()

            except ValueError as e:
                messagebox.showerror("Error", str(e))
            except Exception as e:
                logger.error(f"Error creating user: {str(e)}")
                messagebox.showerror("Error", "Failed to create user")

        # Add save button
        ttk.Button(
            form_frame,
            text="Save",
            command=save_user
        ).pack(pady=20)

    def show_edit_dialog(self):
        """Show dialog to edit selected user"""
        if not self.selected_user:
            return

        dialog = tk.Toplevel(self)
        dialog.title("Edit User")
        dialog.geometry("400x400")
        dialog.grab_set()

        # Get user details
        user = self.services['user'].get_user_details(self.selected_user[0])

        # Create edit form
        form_frame = ttk.Frame(dialog, padding="20")
        form_frame.pack(fill="both", expand=True)

        # Username field (read-only)
        ttk.Label(form_frame, text="Username:").pack(anchor="w", pady=(0, 5))
        username_var = tk.StringVar(value=user['username'])
        ttk.Entry(
            form_frame,
            textvariable=username_var,
            state="readonly",
            width=40
        ).pack(fill="x", pady=(0, 10))

        # Email field
        ttk.Label(form_frame, text="Email:").pack(anchor="w", pady=(0, 5))
        email_var = tk.StringVar(value=user['email'])
        ttk.Entry(
            form_frame,
            textvariable=email_var,
            width=40
        ).pack(fill="x", pady=(0, 10))

        # Role selection
        ttk.Label(form_frame, text="Role:").pack(anchor="w", pady=(0, 5))
        role_var = tk.StringVar(value=user['role'])
        for role in UserRole:
            ttk.Radiobutton(
                form_frame,
                text=role.value.capitalize(),
                value=role.value,
                variable=role_var
            ).pack(anchor="w")

        def save_changes():
            try:
                # Get form data
                email = email_var.get().strip()
                role = UserRole(role_var.get())

                # Validate inputs
                if not email:
                    raise ValueError("Email is required")

                # Update user
                self.services['user'].update_user(
                    user_id=user['id'],
                    update_data={
                        'email': email,
                        'role': role
                    },
                    audit_user_id=1  # TODO: Get actual user ID
                )

                messagebox.showinfo("Success", "User updated successfully!")
                dialog.destroy()

                # Refresh users list
                self.load_users()

            except ValueError as e:
                messagebox.showerror("Error", str(e))
            except Exception as e:
                logger.error(f"Error updating user: {str(e)}")
                messagebox.showerror("Error", "Failed to update user")

                # Add save button
            ttk.Button(
                form_frame,
                text="Save Changes",
                command=save_changes
            ).pack(pady=20)

            def show_change_password_dialog(self):
                """Show dialog to change user's password"""
                if not self.selected_user:
                    return

                dialog = tk.Toplevel(self)
                dialog.title("Change Password")
                dialog.geometry("400x300")
                dialog.grab_set()

                # Create password form
                form_frame = ttk.Frame(dialog, padding="20")
                form_frame.pack(fill="both", expand=True)

                ttk.Label(
                    form_frame,
                    text=f"Change Password for {self.selected_user[0]}",
                    font=("Helvetica", 12, "bold")
                ).pack(pady=(0, 20))

                # New password field
                ttk.Label(form_frame, text="New Password:").pack(anchor="w", pady=(0, 5))
                password_var = tk.StringVar()
                ttk.Entry(
                    form_frame,
                    textvariable=password_var,
                    show="*",
                    width=40
                ).pack(fill="x", pady=(0, 10))

                # Confirm password field
                ttk.Label(form_frame, text="Confirm Password:").pack(anchor="w", pady=(0, 5))
                confirm_password_var = tk.StringVar()
                ttk.Entry(
                    form_frame,
                    textvariable=confirm_password_var,
                    show="*",
                    width=40
                ).pack(fill="x", pady=(0, 10))

                def change_password():
                    try:
                        # Get passwords
                        password = password_var.get()
                        confirm_password = confirm_password_var.get()

                        # Validate inputs
                        if not password or not confirm_password:
                            raise ValueError("All fields are required")

                        if password != confirm_password:
                            raise ValueError("Passwords do not match")

                        # Update password
                        self.services['user'].update_password(
                            user_id=self.selected_user[0],
                            new_password=password,
                            audit_user_id=1  # TODO: Get actual user ID
                        )

                        messagebox.showinfo("Success", "Password changed successfully!")
                        dialog.destroy()

                    except ValueError as e:
                        messagebox.showerror("Error", str(e))
                    except Exception as e:
                        logger.error(f"Error changing password: {str(e)}")
                        messagebox.showerror("Error", "Failed to change password")

                # Add save button
                ttk.Button(
                    form_frame,
                    text="Change Password",
                    command=change_password
                ).pack(pady=20)

            def reset_user_password(self):
                """Reset user's password and send email"""
                if not self.selected_user:
                    return

                if messagebox.askyesno(
                        "Confirm Reset",
                        f"Are you sure you want to reset the password for {self.selected_user[0]}?\n"
                        "A reset link will be sent to their email address."
                ):
                    try:
                        # Initiate password reset
                        self.services['user'].initiate_password_reset(
                            email=self.selected_user[1]
                        )

                        messagebox.showinfo(
                            "Success",
                            "Password reset link has been sent to the user's email."
                        )

                    except Exception as e:
                        logger.error(f"Error resetting password: {str(e)}")
                        messagebox.showerror("Error", "Failed to reset password")

            def toggle_user_status(self):
                """Activate or deactivate selected user"""
                if not self.selected_user:
                    return

                current_status = self.selected_user[4]  # "Active" or "Inactive"
                new_status = "deactivate" if current_status == "Active" else "activate"

                if messagebox.askyesno(
                        "Confirm Status Change",
                        f"Are you sure you want to {new_status} user {self.selected_user[0]}?"
                ):
                    try:
                        if new_status == "deactivate":
                            self.services['user'].deactivate_user(
                                user_id=self.selected_user[0],
                                audit_user_id=1  # TODO: Get actual user ID
                            )
                        else:
                            self.services['user'].reactivate_user(
                                user_id=self.selected_user[0],
                                audit_user_id=1  # TODO: Get actual user ID
                            )

                        messagebox.showinfo(
                            "Success",
                            f"User {new_status}d successfully!"
                        )

                        # Refresh users list
                        self.load_users()

                    except Exception as e:
                        logger.error(f"Error changing user status: {str(e)}")
                        messagebox.showerror("Error", f"Failed to {new_status} user")

            def refresh(self):
                """Refresh the user list"""
                self.load_users()

            def cleanup(self):
                """Clean up resources"""
                pass