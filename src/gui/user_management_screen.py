import tkinter as tk
from tkinter import ttk, messagebox
import logging
from src.database.models import UserRole

try:
    from src.gui.styles import (CREAM, CARD_BG, ESPRESSO, MEDIUM_BROWN, DARK_BROWN,
                                 LIGHT_BROWN, BORDER, TEXT_DARK, TEXT_MID, TEXT_LIGHT,
                                 SUCCESS, WARNING, DANGER, FONT_H2, FONT_H3,
                                 FONT_BODY, FONT_SMALL)
    _HAS_STYLES = True
except ImportError:
    _HAS_STYLES = False

logger = logging.getLogger(__name__)


class UserManagementScreen(ttk.Frame):
    def __init__(self, parent, services, user_data=None):
        super().__init__(parent)
        self.parent = parent
        self.services = services
        self.user_data = user_data or {}
        self.selected_user = None

        if not self._verify_admin_access():
            messagebox.showerror(
                "Access Denied",
                "You do not have permission to access user management."
            )
            return

        self._create_widgets()
        self._load_users()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _verify_admin_access(self) -> bool:
        return self.user_data.get('role') == UserRole.ADMIN.value

    def _audit_id(self) -> int:
        return self.user_data.get('id', 1)

    def _get_selected_id(self):
        if not self.selected_user:
            messagebox.showwarning("No Selection", "Please select a user first.")
            return None
        return int(self.selected_user[0])

    # ------------------------------------------------------------------
    # Widget creation
    # ------------------------------------------------------------------
    def _create_widgets(self):
        bg = CREAM if _HAS_STYLES else "#f0f0f0"

        # Header
        hdr = tk.Frame(self, bg=bg, pady=12)
        hdr.pack(fill="x", padx=20)
        tk.Label(hdr, text="User Management",
                 font=FONT_H2 if _HAS_STYLES else ("Helvetica", 16, "bold"),
                 bg=bg, fg=ESPRESSO if _HAS_STYLES else "black").pack(side="left")
        ttk.Button(hdr, text="Refresh",
                   style="Secondary.TButton" if _HAS_STYLES else "TButton",
                   command=self._load_users).pack(side="right", padx=(0, 6))
        ttk.Button(hdr, text="+ Add User",
                   style="Primary.TButton" if _HAS_STYLES else "TButton",
                   command=self._show_add_dialog).pack(side="right")

        # Search bar
        search_bar = tk.Frame(self, bg=bg)
        search_bar.pack(fill="x", padx=20, pady=(0, 8))
        tk.Label(search_bar, text="Search:", bg=bg,
                 font=FONT_SMALL if _HAS_STYLES else ("Helvetica", 10)).pack(side="left")
        self._search_var = tk.StringVar()
        self._search_var.trace_add('write', lambda *_: self._filter())
        ttk.Entry(search_bar, textvariable=self._search_var, width=28).pack(side="left", padx=5)
        tk.Label(search_bar, text="Role:", bg=bg,
                 font=FONT_SMALL if _HAS_STYLES else ("Helvetica", 10)).pack(side="left", padx=(16, 4))
        self._role_var = tk.StringVar(value="All")
        role_combo = ttk.Combobox(
            search_bar, textvariable=self._role_var,
            values=["All"] + [r.value for r in UserRole],
            state="readonly", width=14
        )
        role_combo.pack(side="left")
        role_combo.bind("<<ComboboxSelected>>", lambda _: self._filter())

        # Treeview with hidden ID column (col 0)
        tree_frame = tk.Frame(self, bg=bg)
        tree_frame.pack(fill="both", expand=True, padx=20, pady=(0, 8))

        cols = ("ID", "Username", "Email", "Role", "Last Login", "Status")
        self._tree = ttk.Treeview(
            tree_frame, columns=cols, show="headings", selectmode="browse"
        )
        self._tree.heading("ID", text="ID")
        self._tree.column("ID", width=0, minwidth=0, stretch=False)
        for col, w in [("Username", 150), ("Email", 230), ("Role", 100),
                       ("Last Login", 160), ("Status", 80)]:
            self._tree.heading(col, text=col)
            self._tree.column(col, width=w)

        sb = ttk.Scrollbar(tree_frame, orient="vertical", command=self._tree.yview)
        self._tree.configure(yscrollcommand=sb.set)
        self._tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        self._tree.bind("<<TreeviewSelect>>", self._on_select)
        self._tree.bind("<Double-1>", lambda e: self._show_edit_dialog())

        # Action buttons
        btn_row = tk.Frame(self, bg=bg)
        btn_row.pack(fill="x", padx=20, pady=(0, 14))
        ttk.Button(btn_row, text="Edit User",
                   style="Secondary.TButton" if _HAS_STYLES else "TButton",
                   command=self._show_edit_dialog).pack(side="left", padx=(0, 6))
        ttk.Button(btn_row, text="Reset Password",
                   style="Secondary.TButton" if _HAS_STYLES else "TButton",
                   command=self._show_reset_password_dialog).pack(side="left", padx=(0, 6))
        ttk.Button(btn_row, text="Toggle Active/Inactive",
                   style="Secondary.TButton" if _HAS_STYLES else "TButton",
                   command=self._toggle_status).pack(side="left")

        self.pack(fill="both", expand=True)

    # ------------------------------------------------------------------
    # Data loading
    # ------------------------------------------------------------------
    def _on_select(self, event=None):
        sel = self._tree.selection()
        if sel:
            self.selected_user = self._tree.item(sel[0])['values']

    def _load_users(self):
        for row in self._tree.get_children():
            self._tree.delete(row)
        try:
            users = self.services['user'].get_all_users()
            for u in users:
                last = u['last_login'] if u['last_login'] else "Never"
                self._tree.insert("", "end", values=(
                    u['id'], u['username'], u['email'], u['role'],
                    last, "Active" if u['is_active'] else "Inactive"
                ))
        except Exception as e:
            logger.error(f"Error loading users: {e}")
            messagebox.showerror("Error", "Failed to load users")

    def _filter(self):
        term = self._search_var.get().lower()
        role_f = self._role_var.get()
        for row in self._tree.get_children():
            self._tree.delete(row)
        try:
            users = self.services['user'].get_all_users()
            for u in users:
                if term and term not in u['username'].lower() and term not in u['email'].lower():
                    continue
                if role_f != "All" and role_f != u['role']:
                    continue
                last = u['last_login'] if u['last_login'] else "Never"
                self._tree.insert("", "end", values=(
                    u['id'], u['username'], u['email'], u['role'],
                    last, "Active" if u['is_active'] else "Inactive"
                ))
        except Exception as e:
            logger.error(f"Filter error: {e}")

    # ------------------------------------------------------------------
    # Dialogs
    # ------------------------------------------------------------------
    def _dialog_header(self, dlg, title_text):
        bg_h = MEDIUM_BROWN if _HAS_STYLES else "#8B5E3C"
        hdr = tk.Frame(dlg, bg=bg_h, pady=10)
        hdr.pack(fill="x")
        tk.Label(hdr, text=title_text,
                 font=FONT_H3 if _HAS_STYLES else ("Helvetica", 12, "bold"),
                 bg=bg_h, fg="white").pack()

    def _show_add_dialog(self):
        bg = CREAM if _HAS_STYLES else "#f0f0f0"
        dlg = tk.Toplevel(self)
        dlg.title("Add User")
        dlg.geometry("400x420")
        dlg.resizable(False, False)
        dlg.configure(bg=bg)
        dlg.grab_set()

        self._dialog_header(dlg, "Create New User")

        body = tk.Frame(dlg, bg=bg, padx=24, pady=16)
        body.pack(fill="both", expand=True)

        def lbl(text):
            tk.Label(body, text=text, bg=bg,
                     font=FONT_SMALL if _HAS_STYLES else ("Helvetica", 10)).pack(anchor="w", pady=(8, 2))

        lbl("Username")
        username_entry = ttk.Entry(body)
        username_entry.pack(fill="x", ipady=3)

        lbl("Email")
        email_entry = ttk.Entry(body)
        email_entry.pack(fill="x", ipady=3)

        lbl("Password")
        pw_entry = ttk.Entry(body, show="*")
        pw_entry.pack(fill="x", ipady=3)

        lbl("Role")
        role_var = tk.StringVar(value=UserRole.STAFF.value)
        role_row = tk.Frame(body, bg=bg)
        role_row.pack(anchor="w", pady=(4, 0))
        for r in UserRole:
            ttk.Radiobutton(role_row, text=r.value.capitalize(),
                            value=r.value, variable=role_var).pack(side="left", padx=4)

        username_entry.focus()

        def save():
            u = username_entry.get().strip()
            e = email_entry.get().strip()
            p = pw_entry.get()
            if not all([u, e, p]):
                messagebox.showerror("Error", "All fields are required", parent=dlg)
                return
            try:
                self.services['user'].create_user(
                    username=u, email=e, password=p, role=UserRole(role_var.get()),
                    audit_user_id=self._audit_id()
                )
                messagebox.showinfo("Success", f"User '{u}' created successfully!", parent=dlg)
                dlg.destroy()
                self._load_users()
            except Exception as ex:
                logger.error(f"Create user error: {ex}")
                messagebox.showerror("Error", str(ex) or "Failed to create user", parent=dlg)

        btn_row = tk.Frame(body, bg=bg)
        btn_row.pack(fill="x", pady=(16, 0))
        ttk.Button(btn_row, text="Cancel",
                   style="Secondary.TButton" if _HAS_STYLES else "TButton",
                   command=dlg.destroy).pack(side="left")
        ttk.Button(btn_row, text="Create User",
                   style="Primary.TButton" if _HAS_STYLES else "TButton",
                   command=save).pack(side="right")
        dlg.bind("<Return>", lambda _: save())

    def _show_edit_dialog(self):
        uid = self._get_selected_id()
        if uid is None:
            return
        try:
            user = self.services['user'].get_user_by_id(uid)
        except Exception as e:
            logger.error(f"Get user error: {e}")
            messagebox.showerror("Error", "Could not load user details")
            return

        bg = CREAM if _HAS_STYLES else "#f0f0f0"
        dlg = tk.Toplevel(self)
        dlg.title("Edit User")
        dlg.geometry("400x320")
        dlg.resizable(False, False)
        dlg.configure(bg=bg)
        dlg.grab_set()

        self._dialog_header(dlg, f"Edit: {user['username']}")

        body = tk.Frame(dlg, bg=bg, padx=24, pady=16)
        body.pack(fill="both", expand=True)

        tk.Label(body, text="Email:", bg=bg,
                 font=FONT_SMALL if _HAS_STYLES else ("Helvetica", 10)).pack(anchor="w", pady=(0, 2))
        email_var = tk.StringVar(value=user['email'])
        ttk.Entry(body, textvariable=email_var).pack(fill="x", ipady=3)

        tk.Label(body, text="Role:", bg=bg,
                 font=FONT_SMALL if _HAS_STYLES else ("Helvetica", 10)).pack(anchor="w", pady=(12, 2))
        role_var = tk.StringVar(value=user['role'])
        role_row = tk.Frame(body, bg=bg)
        role_row.pack(anchor="w")
        for r in UserRole:
            ttk.Radiobutton(role_row, text=r.value.capitalize(),
                            value=r.value, variable=role_var).pack(side="left", padx=4)

        def save():
            e = email_var.get().strip()
            if not e:
                messagebox.showerror("Error", "Email is required", parent=dlg)
                return
            try:
                self.services['user'].update_user(
                    user_id=uid,
                    update_data={'email': e, 'role': UserRole(role_var.get())},
                    audit_user_id=self._audit_id()
                )
                messagebox.showinfo("Success", "User updated successfully!", parent=dlg)
                dlg.destroy()
                self._load_users()
            except Exception as ex:
                logger.error(f"Update user error: {ex}")
                messagebox.showerror("Error", str(ex) or "Failed to update user", parent=dlg)

        btn_row = tk.Frame(body, bg=bg)
        btn_row.pack(fill="x", pady=(20, 0))
        ttk.Button(btn_row, text="Cancel",
                   style="Secondary.TButton" if _HAS_STYLES else "TButton",
                   command=dlg.destroy).pack(side="left")
        ttk.Button(btn_row, text="Save Changes",
                   style="Primary.TButton" if _HAS_STYLES else "TButton",
                   command=save).pack(side="right")

    def _show_reset_password_dialog(self):
        uid = self._get_selected_id()
        if uid is None:
            return

        bg = CREAM if _HAS_STYLES else "#f0f0f0"
        dlg = tk.Toplevel(self)
        dlg.title("Reset Password")
        dlg.geometry("360x260")
        dlg.resizable(False, False)
        dlg.configure(bg=bg)
        dlg.grab_set()

        username = self.selected_user[1] if self.selected_user else ""
        self._dialog_header(dlg, f"Reset: {username}")

        body = tk.Frame(dlg, bg=bg, padx=24, pady=16)
        body.pack(fill="both", expand=True)

        tk.Label(body, text="New Password:", bg=bg,
                 font=FONT_SMALL if _HAS_STYLES else ("Helvetica", 10)).pack(anchor="w", pady=(0, 2))
        pw_entry = ttk.Entry(body, show="*")
        pw_entry.pack(fill="x", ipady=3)
        pw_entry.focus()

        tk.Label(body, text="Confirm Password:", bg=bg,
                 font=FONT_SMALL if _HAS_STYLES else ("Helvetica", 10)).pack(anchor="w", pady=(10, 2))
        cpw_entry = ttk.Entry(body, show="*")
        cpw_entry.pack(fill="x", ipady=3)

        def save():
            p, cp = pw_entry.get(), cpw_entry.get()
            if not p:
                messagebox.showerror("Error", "Password cannot be empty", parent=dlg)
                return
            if p != cp:
                messagebox.showerror("Error", "Passwords do not match", parent=dlg)
                return
            try:
                self.services['user'].admin_reset_password(
                    user_id=uid, new_password=p, audit_user_id=self._audit_id()
                )
                messagebox.showinfo("Success", "Password reset successfully!", parent=dlg)
                dlg.destroy()
            except Exception as ex:
                logger.error(f"Reset password error: {ex}")
                messagebox.showerror("Error", str(ex) or "Failed to reset password", parent=dlg)

        btn_row = tk.Frame(body, bg=bg)
        btn_row.pack(fill="x", pady=(16, 0))
        ttk.Button(btn_row, text="Cancel",
                   style="Secondary.TButton" if _HAS_STYLES else "TButton",
                   command=dlg.destroy).pack(side="left")
        ttk.Button(btn_row, text="Reset Password",
                   style="Danger.TButton" if _HAS_STYLES else "TButton",
                   command=save).pack(side="right")
        dlg.bind("<Return>", lambda _: save())

    def _toggle_status(self):
        uid = self._get_selected_id()
        if uid is None:
            return
        status = str(self.selected_user[5])   # "Active" or "Inactive"
        username = str(self.selected_user[1])
        action = "deactivate" if status == "Active" else "reactivate"
        if not messagebox.askyesno(
            "Confirm", f"Are you sure you want to {action} user '{username}'?"
        ):
            return
        try:
            if action == "deactivate":
                self.services['user'].deactivate_user(
                    user_id=uid, audit_user_id=self._audit_id()
                )
            else:
                self.services['user'].reactivate_user(
                    user_id=uid, audit_user_id=self._audit_id()
                )
            messagebox.showinfo("Success", f"User {action}d successfully!")
            self._load_users()
        except Exception as e:
            logger.error(f"Toggle status error: {e}")
            messagebox.showerror("Error", f"Failed to {action} user")
