import tkinter as tk
from tkinter import ttk, messagebox
import logging
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional

try:
    from src.gui.styles import (CREAM, CARD_BG, ESPRESSO, MEDIUM_BROWN, DARK_BROWN,
                                 LIGHT_BROWN, BORDER, TEXT_DARK, TEXT_LIGHT, TEXT_MID,
                                 SUCCESS, WARNING, DANGER, FONT_H2, FONT_H3,
                                 FONT_BODY, FONT_SMALL)
    _HAS_STYLES = True
except ImportError:
    _HAS_STYLES = False

logger = logging.getLogger(__name__)


class ExpenseScreen(ttk.Frame):
    def __init__(self, parent, services):
        super().__init__(parent)
        self.parent = parent
        self.services = services
        self.selected_expense = None  # stores row values; [0] = expense ID

        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        bg = CREAM if _HAS_STYLES else "#f0f0f0"

        # Page header
        hdr = tk.Frame(self, bg=bg, pady=0)
        hdr.pack(fill="x")

        # Accent top bar
        tk.Frame(hdr, bg=MEDIUM_BROWN if _HAS_STYLES else "#8B5E3C", height=3).pack(fill="x")

        inner_hdr = tk.Frame(hdr, bg=bg, pady=14, padx=24)
        inner_hdr.pack(fill="x")

        title_col = tk.Frame(inner_hdr, bg=bg)
        title_col.pack(side="left")
        tk.Label(title_col, text="💳  Expense Management",
                 font=("Helvetica", 18, "bold"),
                 bg=bg, fg=ESPRESSO if _HAS_STYLES else "black").pack(anchor="w")
        tk.Label(title_col, text="Track and manage all café expenses",
                 font=("Helvetica", 9),
                 bg=bg, fg=TEXT_MID if _HAS_STYLES else "#555").pack(anchor="w", pady=(2, 0))

        add_btn = tk.Button(inner_hdr, text="  + Record Expense  ",
                            font=("Helvetica", 10, "bold"),
                            bg=MEDIUM_BROWN if _HAS_STYLES else "#8B5E3C",
                            fg="white",
                            activebackground=DARK_BROWN if _HAS_STYLES else "#4A2C17",
                            activeforeground="white",
                            relief="flat", bd=0, cursor="hand2",
                            command=self.show_add_expense_dialog)
        add_btn.pack(side="right", ipady=8)
        tk.Frame(inner_hdr, bg=bg, width=1).pack(side="right", padx=4)

        tk.Frame(hdr, bg=BORDER if _HAS_STYLES else "#ccc", height=1).pack(fill="x")

        # Notebook for tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=12, pady=8)

        self.create_expenses_tab()
        self.create_categories_tab()
        self.create_analysis_tab()

        self.pack(fill="both", expand=True)

    def create_expenses_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="  Expenses  ")

        # Filter bar
        bg = CREAM if _HAS_STYLES else "#f0f0f0"
        filter_bar = tk.Frame(tab, bg=CARD_BG if _HAS_STYLES else "white",
                              pady=10, padx=12,
                              highlightbackground=BORDER if _HAS_STYLES else "#ccc",
                              highlightthickness=1)
        filter_bar.pack(fill="x", padx=8, pady=(8, 4))

        tk.Label(filter_bar, text="From",
                 font=("Helvetica", 9, "bold"),
                 bg=CARD_BG if _HAS_STYLES else "white",
                 fg=TEXT_MID if _HAS_STYLES else "#555").pack(side="left")
        self.start_date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        ttk.Entry(filter_bar, textvariable=self.start_date_var, width=11).pack(
            side="left", padx=(4, 0))

        tk.Label(filter_bar, text="  to",
                 font=("Helvetica", 9, "bold"),
                 bg=CARD_BG if _HAS_STYLES else "white",
                 fg=TEXT_MID if _HAS_STYLES else "#555").pack(side="left")
        self.end_date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        ttk.Entry(filter_bar, textvariable=self.end_date_var, width=11).pack(
            side="left", padx=(4, 16))

        tk.Label(filter_bar, text="Category",
                 font=("Helvetica", 9, "bold"),
                 bg=CARD_BG if _HAS_STYLES else "white",
                 fg=TEXT_MID if _HAS_STYLES else "#555").pack(side="left")
        self.category_var = tk.StringVar(value="All")
        self.category_combo = ttk.Combobox(
            filter_bar, textvariable=self.category_var,
            state="readonly", width=18)
        self.category_combo.pack(side="left", padx=(4, 16))

        ttk.Button(filter_bar, text="🔍  Search",
                   command=self.load_expenses).pack(side="left", padx=(0, 4))
        ttk.Button(filter_bar, text="Export CSV",
                   style="Secondary.TButton" if _HAS_STYLES else "TButton",
                   command=self.export_expenses).pack(side="right")

        # Create expenses treeview (ID is column 0, hidden with width=0)
        columns = ("ID", "Date", "Category", "Amount", "Description", "Added By")
        self.expenses_tree = ttk.Treeview(
            tab,
            columns=columns,
            show="headings",
            selectmode="browse"
        )

        # ID column hidden
        self.expenses_tree.heading("ID", text="ID")
        self.expenses_tree.column("ID", width=0, minwidth=0, stretch=False)
        self.expenses_tree.heading("Date", text="Date")
        self.expenses_tree.column("Date", width=100)
        self.expenses_tree.heading("Category", text="Category")
        self.expenses_tree.column("Category", width=150)
        self.expenses_tree.heading("Amount", text="Amount")
        self.expenses_tree.column("Amount", width=100)
        self.expenses_tree.heading("Description", text="Description")
        self.expenses_tree.column("Description", width=300)
        self.expenses_tree.heading("Added By", text="Added By")
        self.expenses_tree.column("Added By", width=100)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(
            tab,
            orient="vertical",
            command=self.expenses_tree.yview
        )
        self.expenses_tree.configure(yscrollcommand=scrollbar.set)

        # Pack treeview and scrollbar
        self.expenses_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Alternating row colours
        self.expenses_tree.tag_configure('odd',  background="#F9F5F0")
        self.expenses_tree.tag_configure('even', background=CARD_BG if _HAS_STYLES else "white")

        self.expenses_tree.bind("<Button-3>", self.show_context_menu)
        self.expenses_tree.bind("<Double-1>", self.show_expense_details)

        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Edit Expense",   command=self.show_edit_dialog)
        self.context_menu.add_command(label="Delete Expense", command=self.delete_expense)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="View Details",   command=self.show_expense_details)

    def create_categories_tab(self):
        """Create expense categories management view"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Categories")

        # Split frame for category list and editor
        split_frame = ttk.Frame(tab)
        split_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Left side - Categories list
        left_frame = ttk.LabelFrame(split_frame, text="Expense Categories")
        left_frame.pack(side="left", fill="both", expand=True, padx=5)

        # Create categories treeview
        columns = ("Category", "Type", "Description")
        self.categories_tree = ttk.Treeview(
            left_frame,
            columns=columns,
            show="headings",
            selectmode="browse"
        )

        # Configure columns
        for col in columns:
            self.categories_tree.heading(col, text=col)
        self.categories_tree.column("Category", width=150)
        self.categories_tree.column("Type", width=100)
        self.categories_tree.column("Description", width=200)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(
            left_frame,
            orient="vertical",
            command=self.categories_tree.yview
        )
        self.categories_tree.configure(yscrollcommand=scrollbar.set)

        # Pack treeview and scrollbar
        self.categories_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Right side - Category editor
        right_frame = ttk.LabelFrame(split_frame, text="Category Details")
        right_frame.pack(side="right", fill="both", padx=5)

        # Category editor fields
        ttk.Label(right_frame, text="Category Name:").pack(pady=5)
        self.category_name_var = tk.StringVar()
        ttk.Entry(
            right_frame,
            textvariable=self.category_name_var,
            width=30
        ).pack(pady=5)

        ttk.Label(right_frame, text="Type:").pack(pady=5)
        self.category_type_var = tk.StringVar(value="expense")
        type_frame = ttk.Frame(right_frame)
        type_frame.pack(pady=5)
        ttk.Radiobutton(
            type_frame,
            text="Expense",
            variable=self.category_type_var,
            value="expense"
        ).pack(side="left", padx=5)
        ttk.Radiobutton(
            type_frame,
            text="Income",
            variable=self.category_type_var,
            value="income"
        ).pack(side="left", padx=5)

        ttk.Label(right_frame, text="Description:").pack(pady=5)
        self.category_desc_var = tk.StringVar()
        ttk.Entry(
            right_frame,
            textvariable=self.category_desc_var,
            width=30
        ).pack(pady=5)

        # Buttons
        buttons_frame = ttk.Frame(right_frame)
        buttons_frame.pack(pady=20)

        ttk.Button(
            buttons_frame,
            text="New",
            command=self.new_category
        ).pack(side="left", padx=5)

        ttk.Button(
            buttons_frame,
            text="Save",
            command=self.save_category
        ).pack(side="left", padx=5)

        ttk.Button(
            buttons_frame,
            text="Delete",
            command=self.delete_category
        ).pack(side="left", padx=5)

    def create_analysis_tab(self):
        """Create expense analysis view"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Analysis")

        # Controls frame
        controls_frame = ttk.Frame(tab)
        controls_frame.pack(fill="x", padx=5, pady=5)

        # Date range
        ttk.Label(controls_frame, text="Date Range:").pack(side="left")
        self.analysis_start_var = tk.StringVar(
            value=(datetime.now().replace(day=1)).strftime("%Y-%m-%d")
        )
        ttk.Entry(
            controls_frame,
            textvariable=self.analysis_start_var,
            width=10
        ).pack(side="left", padx=5)

        ttk.Label(controls_frame, text="to").pack(side="left")
        self.analysis_end_var = tk.StringVar(
            value=datetime.now().strftime("%Y-%m-%d")
        )
        ttk.Entry(
            controls_frame,
            textvariable=self.analysis_end_var,
            width=10
        ).pack(side="left", padx=5)

        ttk.Button(
            controls_frame,
            text="Generate",
            command=self.generate_analysis
        ).pack(side="left", padx=5)

        ttk.Button(
            controls_frame,
            text="Export",
            command=self.export_analysis
        ).pack(side="right", padx=5)

        # Analysis content
        self.analysis_frame = ttk.Frame(tab)
        self.analysis_frame.pack(fill="both", expand=True, padx=5, pady=5)

    def load_data(self):
        """Load initial data"""
        try:
            # Load categories for combo box
            categories = self.services['expense'].get_categories()
            self.category_combo['values'] = ["All"] + [cat['name'] for cat in categories]

            # Load expenses
            self.load_expenses()

            # Load categories
            self.load_categories()

            # Generate initial analysis
            self.generate_analysis()

        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            messagebox.showerror("Error", "Failed to load expense data")

    def show_add_expense_dialog(self):
        """Show dialog to add new expense"""
        bg = CREAM if _HAS_STYLES else "#f0f0f0"
        dialog = tk.Toplevel(self)
        dialog.title("Record Expense")
        dialog.geometry("440x440")
        dialog.resizable(False, False)
        dialog.configure(bg=bg)
        dialog.grab_set()

        # Header
        hdr = tk.Frame(dialog, bg=MEDIUM_BROWN if _HAS_STYLES else "#6B4423", pady=14)
        hdr.pack(fill="x")
        tk.Label(hdr, text="Record New Expense",
                 font=FONT_H3 if _HAS_STYLES else ("Helvetica", 13, "bold"),
                 bg=MEDIUM_BROWN if _HAS_STYLES else "#6B4423",
                 fg=CARD_BG if _HAS_STYLES else "white").pack()

        # Form area
        form = tk.Frame(dialog, bg=bg, padx=28, pady=14)
        form.pack(fill="both", expand=True)

        def _lbl(text):
            tk.Label(form, text=text,
                     font=FONT_SMALL if _HAS_STYLES else ("Helvetica", 10),
                     bg=bg,
                     fg=TEXT_MID if _HAS_STYLES else "#555").pack(anchor="w", pady=(8, 1))

        _lbl("Category *")
        category_var = tk.StringVar()
        category_combo = ttk.Combobox(
            form, textvariable=category_var,
            values=[cat['name'] for cat in self.services['expense'].get_categories()],
            state="readonly", width=36, font=FONT_BODY if _HAS_STYLES else None
        )
        category_combo.pack(fill="x")

        _lbl("Amount ($) *")
        amount_entry = ttk.Entry(form, width=38)
        amount_entry.pack(fill="x")

        _lbl("Date (YYYY-MM-DD)")
        date_entry = ttk.Entry(form, width=38)
        date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        date_entry.pack(fill="x")

        _lbl("Description *")
        desc_entry = ttk.Entry(form, width=38)
        desc_entry.pack(fill="x")

        def save_expense():
            try:
                # Read directly from widgets — textvariable can lag on macOS in grab_set dialogs
                category = category_combo.get()
                if not category:
                    raise ValueError("Please select a category")

                try:
                    amount = float(amount_entry.get())
                    if amount <= 0:
                        raise ValueError()
                except ValueError:
                    raise ValueError("Amount must be a positive number")

                description = desc_entry.get().strip()
                if not description:
                    raise ValueError("Please enter a description")

                cats = self.services['expense'].get_categories()
                cat_match = next((c for c in cats if c['name'] == category), None)
                if not cat_match:
                    raise ValueError("Selected category not found — please try again")

                # Create expense
                self.services['expense'].record_expense(
                    user_id=1,
                    category_id=cat_match['id'],
                    amount=amount,
                    description=description,
                    expense_date=date_entry.get()
                )

                messagebox.showinfo("Success", "Expense recorded successfully!")
                dialog.destroy()
                self.load_expenses()

            except ValueError as e:
                messagebox.showerror("Validation Error", str(e))
            except Exception as e:
                logger.error(f"Error recording expense: {e}")
                messagebox.showerror("Error", "Failed to record expense")

        # Button row
        btn_frame = tk.Frame(dialog, bg=bg, pady=12)
        btn_frame.pack(fill="x", padx=28)
        ttk.Button(btn_frame, text="Cancel", style="Secondary.TButton" if _HAS_STYLES else "TButton",
                   command=dialog.destroy).pack(side="right", padx=(6, 0))
        ttk.Button(btn_frame, text="Save Expense",
                   style="Primary.TButton" if _HAS_STYLES else "TButton",
                   command=save_expense).pack(side="right")

    def show_context_menu(self, event):
        """Show context menu for selected expense"""
        item = self.expenses_tree.identify_row(event.y)
        if item:
            self.expenses_tree.selection_set(item)
            self.selected_expense = self.expenses_tree.item(item)['values']
            self.context_menu.post(event.x_root, event.y_root)

    def show_expense_details(self, event=None):
        """Show details for selected expense"""
        if not self.selected_expense:
            return

        dialog = tk.Toplevel(self)
        dialog.title("Expense Details")
        dialog.geometry("400x300")
        dialog.grab_set()

        # Get full expense details
        expense = self.services['expense'].get_expense_details(self.selected_expense[0])
        if expense:
            # Create details view
            details_frame = ttk.Frame(dialog, padding="20")
            details_frame.pack(fill="both", expand=True)

            # Display expense details
            details = [
                ("Category:", expense['category']['name']),
                ("Amount:", f"${expense['amount']:.2f}"),
                ("Date:", expense['date']),
                ("Description:", expense['description']),
                ("Added By:", expense['user']['username']),
                ("Created At:", expense['created_at'])
            ]

            for i, (label, value) in enumerate(details):
                ttk.Label(details_frame, text=label, font=("Helvetica", 10, "bold")).grid(
                    row=i, column=0, sticky="e", padx=5, pady=5
                )
                ttk.Label(details_frame, text=value).grid(
                    row=i, column=1, sticky="w", padx=5, pady=5
                )

            # Add close button
            ttk.Button(
                dialog,
                text="Close",
                command=dialog.destroy
            ).pack(pady=10)

    def show_edit_dialog(self):
        """Show dialog to edit selected expense"""
        if not self.selected_expense:
            return

        dialog = tk.Toplevel(self)
        dialog.title("Edit Expense")
        dialog.geometry("400x400")
        dialog.grab_set()

        # Load expense details
        expense = self.services['expense'].get_expense_details(self.selected_expense[0])

        # Create edit form
        ttk.Label(dialog, text="Category:").pack(pady=5)
        category_var = tk.StringVar(value=expense['category']['name'])
        category_combo = ttk.Combobox(
            dialog,
            textvariable=category_var,
            values=[cat['name'] for cat in self.services['expense'].get_categories()],
            state="readonly",
            width=30
        )
        category_combo.pack(pady=5)

        ttk.Label(dialog, text="Amount ($):").pack(pady=5)
        amount_var = tk.StringVar(value=str(expense['amount']))
        ttk.Entry(
            dialog,
            textvariable=amount_var,
            width=30
        ).pack(pady=5)

        ttk.Label(dialog, text="Date:").pack(pady=5)
        date_var = tk.StringVar(value=expense['date'])
        ttk.Entry(
            dialog,
            textvariable=date_var,
            width=30
        ).pack(pady=5)

        ttk.Label(dialog, text="Description:").pack(pady=5)
        description_var = tk.StringVar(value=expense['description'])
        ttk.Entry(
            dialog,
            textvariable=description_var,
            width=30
        ).pack(pady=5)

        def save_changes():
            try:
                # Validate inputs
                try:
                    amount = float(amount_var.get())
                    if amount <= 0:
                        raise ValueError()
                except ValueError:
                    raise ValueError("Amount must be a positive number")

                description = description_var.get().strip()
                if not description:
                    raise ValueError("Please enter a description")

                # Update expense — use combo.get() to avoid macOS textvariable lag
                cat_name = category_combo.get()
                cats = self.services['expense'].get_categories()
                cat_match = next((c for c in cats if c['name'] == cat_name), None)
                if not cat_match:
                    raise ValueError("Please select a valid category")
                update_data = {
                    'category_id': cat_match['id'],
                    'amount': amount,
                    'date': date_var.get(),
                    'description': description
                }

                self.services['expense'].update_expense(
                    expense_id=expense['id'],
                    update_data=update_data,
                    audit_user_id=1  # TODO: Get actual user ID
                )

                messagebox.showinfo("Success", "Expense updated successfully!")
                dialog.destroy()

                # Refresh expenses list
                self.load_expenses()

            except ValueError as e:
                messagebox.showerror("Error", str(e))
            except Exception as e:
                logger.error(f"Error updating expense: {str(e)}")
                messagebox.showerror("Error", "Failed to update expense")

        # Add save button
        ttk.Button(
            dialog,
            text="Save Changes",
            command=save_changes
        ).pack(pady=20)

    def delete_expense(self):
        """Delete selected expense"""
        if not self.selected_expense:
            return

        if messagebox.askyesno(
                "Confirm Delete",
                "Are you sure you want to delete this expense?"
        ):
            try:
                self.services['expense'].delete_expense(
                    expense_id=self.selected_expense[0],
                    audit_user_id=1  # TODO: Get actual user ID
                )

                messagebox.showinfo("Success", "Expense deleted successfully!")

                # Refresh expenses list
                self.load_expenses()

            except Exception as e:
                logger.error(f"Error deleting expense: {str(e)}")
                messagebox.showerror("Error", "Failed to delete expense")

    def load_categories(self):
        """Load categories into the categories treeview"""
        try:
            for item in self.categories_tree.get_children():
                self.categories_tree.delete(item)
            categories = self.services['expense'].get_categories()
            for cat in categories:
                self.categories_tree.insert("", "end", values=(
                    cat['name'], 'expense', cat.get('description', '')
                ))
        except Exception as e:
            logger.error(f"Error loading categories: {str(e)}")

    def load_expenses(self):
        """Load expenses based on current filters"""
        try:
            start_date = self.start_date_var.get()
            end_date = self.end_date_var.get()
            category = self.category_var.get()

            # Clear existing items
            for item in self.expenses_tree.get_children():
                self.expenses_tree.delete(item)

            # Get expenses
            category_id = next(
                (cat['id'] for cat in self.services['expense'].get_categories()
                 if cat['name'] == category),
                None
            ) if category != "All" else None

            expenses = self.services['expense'].get_expenses(
                start_date=start_date,
                end_date=end_date,
                category_id=category_id
            )

            for i, expense in enumerate(expenses):
                tag = 'odd' if i % 2 == 0 else 'even'
                self.expenses_tree.insert("", "end", tags=(tag,), values=(
                    expense['id'],
                    expense['date'],
                    expense['category'],
                    f"${expense['amount']:.2f}",
                    expense['description'],
                    expense['user']
                ))

        except Exception as e:
            logger.error(f"Error loading expenses: {str(e)}")
            messagebox.showerror("Error", "Failed to load expenses")

    def new_category(self):
        """Clear category editor for new category"""
        self.category_name_var.set("")
        self.category_type_var.set("expense")
        self.category_desc_var.set("")

    def save_category(self):
        """Save current category"""
        try:
            name = self.category_name_var.get().strip()
            if not name:
                raise ValueError("Category name is required")

            category_data = {
                'name': name,
                'type': self.category_type_var.get(),
                'description': self.category_desc_var.get().strip()
            }

            # Create or update category
            self.services['expense'].save_category(
                name=name,
                description=category_data.get('description', '')
            )

            messagebox.showinfo("Success", "Category saved successfully!")

            # Refresh categories
            self.load_categories()

        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            logger.error(f"Error saving category: {str(e)}")
            messagebox.showerror("Error", "Failed to save category")

    def delete_category(self):
        """Delete selected category"""
        selection = self.categories_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a category")
            return

        category_name = self.categories_tree.item(selection[0])['values'][0]

        if messagebox.askyesno(
                "Confirm Delete",
                f"Are you sure you want to delete category '{category_name}'?\n"
                "This will affect all expenses in this category."
        ):
            try:
                cats = self.services['expense'].get_categories()
                category_id = next((c['id'] for c in cats if c['name'] == category_name), None)
                if not category_id:
                    raise ValueError("Category not found")
                self.services['expense'].delete_category(category_id=category_id)

                messagebox.showinfo("Success", "Category deleted successfully!")

                # Refresh categories
                self.load_categories()

            except Exception as e:
                logger.error(f"Error deleting category: {str(e)}")
                messagebox.showerror("Error", "Failed to delete category")

    def export_expenses(self):
        """Export filtered expenses list"""
        try:
            start_date = self.start_date_var.get()
            end_date = self.end_date_var.get()
            category = self.category_var.get()

            report_data = self.services['reporting'].export_report(
                report_type='periodic',
                start_date=start_date,
                end_date=end_date,
                format='csv'
            )

            # Save file
            import tkinter.filedialog as filedialog
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv")],
                initialfile=f"expenses_{start_date}_to_{end_date}.csv"
            )

            if filename:
                with open(filename, 'wb') as f:
                    f.write(report_data)
                messagebox.showinfo("Success", "Expenses exported successfully!")

        except Exception as e:
            logger.error(f"Error exporting expenses: {str(e)}")
            messagebox.showerror("Error", "Failed to export expenses")

    def generate_analysis(self):
        """Generate expense analysis"""
        try:
            # Clear analysis frame
            for widget in self.analysis_frame.winfo_children():
                widget.destroy()

            # Get analysis data
            analysis = self.services['expense'].get_expense_summary(
                start_date=self.analysis_start_var.get(),
                end_date=self.analysis_end_var.get()
            )

            # Create analysis visualization
            # TODO: Add charts and graphs using matplotlib or similar

            # Show summary statistics
            summary_frame = ttk.LabelFrame(self.analysis_frame, text="Summary")
            summary_frame.pack(fill="x", padx=5, pady=5)

            summary = [
                ("Total Expenses:", f"${analysis['summary']['total_amount']:.2f}"),
                ("Number of Transactions:", str(analysis['summary']['total_transactions'])),
                ("Average Transaction:", f"${analysis['summary']['average_transaction']:.2f}")
            ]

            for i, (label, value) in enumerate(summary):
                ttk.Label(summary_frame, text=label).grid(row=i, column=0, padx=5, pady=2)
                ttk.Label(summary_frame, text=value).grid(row=i, column=1, padx=5, pady=2)

            # Show category breakdown
            breakdown_frame = ttk.LabelFrame(self.analysis_frame, text="Category Breakdown")
            breakdown_frame.pack(fill="both", expand=True, padx=5, pady=5)

            # Create treeview for breakdown
            columns = ("Category", "Amount", "Transactions", "Average")
            breakdown_tree = ttk.Treeview(
                breakdown_frame,
                columns=columns,
                show="headings"
            )

            for col in columns:
                breakdown_tree.heading(col, text=col)
                breakdown_tree.column(col, width=100)

            # Add scrollbar
            scrollbar = ttk.Scrollbar(
                breakdown_frame,
                orient="vertical",
                command=breakdown_tree.yview
            )
            breakdown_tree.configure(yscrollcommand=scrollbar.set)

            breakdown_tree.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

            # Add category data
            for category in analysis['by_category']:
                breakdown_tree.insert("", "end", values=(
                    category['category'],
                    f"${category['total_amount']:.2f}",
                    category['transaction_count'],
                    f"${category['total_amount'] / category['transaction_count']:.2f}"
                ))

        except Exception as e:
            logger.error(f"Error generating analysis: {str(e)}")
            messagebox.showerror("Error", "Failed to generate analysis")

    def export_analysis(self):
        """Export current analysis"""
        try:
            report_data = self.services['reporting'].export_report(
                report_type='periodic',
                start_date=self.analysis_start_var.get(),
                end_date=self.analysis_end_var.get(),
                format='csv'
            )

            # Save file
            import tkinter.filedialog as filedialog
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv")],
                initialfile=f"expense_analysis_{datetime.now().strftime('%Y%m%d')}.csv"
            )

            if filename:
                with open(filename, 'wb') as f:
                    f.write(report_data)
                messagebox.showinfo("Success", "Analysis exported successfully!")

        except Exception as e:
            logger.error(f"Error exporting analysis: {str(e)}")
            messagebox.showerror("Error", "Failed to export analysis")