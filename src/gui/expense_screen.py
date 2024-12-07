import tkinter as tk
from tkinter import ttk, messagebox
import logging
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class ExpenseScreen(ttk.Frame):
    def __init__(self, parent, services):
        super().__init__(parent)
        self.parent = parent
        self.services = services
        self.selected_expense = None

        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        """Create and arrange widgets"""
        # Main heading
        heading_frame = ttk.Frame(self)
        heading_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(
            heading_frame,
            text="Expense Management",
            font=("Helvetica", 16, "bold")
        ).pack(side="left")

        ttk.Button(
            heading_frame,
            text="Record Expense",
            command=self.show_add_expense_dialog
        ).pack(side="right")

        # Create notebook for different views
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=5)

        # Create tabs
        self.create_expenses_tab()
        self.create_categories_tab()
        self.create_analysis_tab()

        # Pack main frame
        self.pack(fill="both", expand=True)

    def create_expenses_tab(self):
        """Create main expenses view"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Expenses")

        # Controls frame
        controls_frame = ttk.Frame(tab)
        controls_frame.pack(fill="x", padx=5, pady=5)

        # Date range
        ttk.Label(controls_frame, text="Date Range:").pack(side="left")
        self.start_date_var = tk.StringVar(
            value=datetime.now().strftime("%Y-%m-%d")
        )
        ttk.Entry(
            controls_frame,
            textvariable=self.start_date_var,
            width=10
        ).pack(side="left", padx=5)

        ttk.Label(controls_frame, text="to").pack(side="left")
        self.end_date_var = tk.StringVar(
            value=datetime.now().strftime("%Y-%m-%d")
        )
        ttk.Entry(
            controls_frame,
            textvariable=self.end_date_var,
            width=10
        ).pack(side="left", padx=5)

        # Category filter
        ttk.Label(controls_frame, text="Category:").pack(side="left", padx=(20, 5))
        self.category_var = tk.StringVar(value="All")
        self.category_combo = ttk.Combobox(
            controls_frame,
            textvariable=self.category_var,
            state="readonly",
            width=20
        )
        self.category_combo.pack(side="left", padx=5)

        # Search button
        ttk.Button(
            controls_frame,
            text="Search",
            command=self.load_expenses
        ).pack(side="left", padx=5)

        # Export button
        ttk.Button(
            controls_frame,
            text="Export",
            command=self.export_expenses
        ).pack(side="right", padx=5)

        # Create expenses treeview
        columns = ("Date", "Category", "Amount", "Description", "Added By")
        self.expenses_tree = ttk.Treeview(
            tab,
            columns=columns,
            show="headings",
            selectmode="browse"
        )

        # Configure columns
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

        # Bind context menu
        self.expenses_tree.bind("<Button-3>", self.show_context_menu)
        self.expenses_tree.bind("<Double-1>", self.show_expense_details)

        # Create context menu
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Edit Expense", command=self.show_edit_dialog)
        self.context_menu.add_command(label="Delete Expense", command=self.delete_expense)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="View Details", command=self.show_expense_details)

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
        dialog = tk.Toplevel(self)
        dialog.title("Record Expense")
        dialog.geometry("400x500")
        dialog.grab_set()

        # Create expense form
        ttk.Label(dialog, text="Category:").pack(pady=5)
        category_var = tk.StringVar()
        category_combo = ttk.Combobox(
            dialog,
            textvariable=category_var,
            values=[cat['name'] for cat in self.services['expense'].get_categories()],
            state="readonly",
            width=30
        )
        category_combo.pack(pady=5)

        ttk.Label(dialog, text="Amount ($):").pack(pady=5)
        amount_var = tk.StringVar()
        ttk.Entry(
            dialog,
            textvariable=amount_var,
            width=30
        ).pack(pady=5)

        ttk.Label(dialog, text="Date:").pack(pady=5)
        date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        ttk.Entry(
            dialog,
            textvariable=date_var,
            width=30
        ).pack(pady=5)

        ttk.Label(dialog, text="Description:").pack(pady=5)
        description_var = tk.StringVar()
        ttk.Entry(
            dialog,
            textvariable=description_var,
            width=30
        ).pack(pady=5)

        def save_expense():
            try:
                # Validate inputs
                category = category_var.get()
                if not category:
                    raise ValueError("Please select a category")

                try:
                    amount = float(amount_var.get())
                    if amount <= 0:
                        raise ValueError()
                except ValueError:
                    raise ValueError("Amount must be a positive number")

                description = description_var.get().strip()
                if not description:
                    raise ValueError("Please enter a description")

                # Create expense
                self.services['expense'].record_expense(
                    user_id=1,  # TODO: Get actual user ID
                    category_id=next(
                        cat['id'] for cat in self.services['expense'].get_categories()
                        if cat['name'] == category
                    ),
                    amount=amount,
                    description=description,
                    expense_date=date_var.get()
                )

                messagebox.showinfo("Success", "Expense recorded successfully!")
                dialog.destroy()

                # Refresh expenses list
                self.load_expenses()

            except ValueError as e:
                messagebox.showerror("Error", str(e))
            except Exception as e:
                logger.error(f"Error recording expense: {str(e)}")
                messagebox.showerror("Error", "Failed to record expense")

        # Add save button
        ttk.Button(
            dialog,
            text="Save",
            command=save_expense
        ).pack(pady=20)

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

                # Update expense
                update_data = {
                    'category_id': next(
                        cat['id'] for cat in self.services['expense'].get_categories()
                        if cat['name'] == category_var.get()
                    ),
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
            expenses = self.services['expense'].get_expense_summary(
                start_date=start_date,
                end_date=end_date,
                category_id=next(
                    (cat['id'] for cat in self.services['expense'].get_categories()
                     if cat['name'] == category),
                    None
                ) if category != "All" else None
            )

            # Add expenses to treeview
            for expense in expenses['expenses']:
                self.expenses_tree.insert("", "end", values=(
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
                category_data=category_data,
                audit_user_id=1  # TODO: Get actual user ID
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
                self.services['expense'].delete_category(
                    category_name=category_name,
                    audit_user_id=1  # TODO: Get actual user ID
                )

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

            # Generate report
            report_data = self.services['reporting'].export_report(
                report_type='expenses',
                start_date=start_date,
                end_date=end_date,
                category=category if category != "All" else None,
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
            analysis = self.services['expense'].get_category_breakdown(
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
            # Generate report
            report_data = self.services['reporting'].export_report(
                report_type='expense_analysis',
                start_date=self.analysis_start_var.get(),
                end_date=self.analysis_end_var.get(),
                format='pdf'
            )

            # Save file
            import tkinter.filedialog as filedialog
            filename = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")],
                initialfile=f"expense_analysis_{datetime.now().strftime('%Y%m%d')}.pdf"
            )

            if filename:
                with open(filename, 'wb') as f:
                    f.write(report_data)
                messagebox.showinfo("Success", "Analysis exported successfully!")

        except Exception as e:
            logger.error(f"Error exporting analysis: {str(e)}")
            messagebox.showerror("Error", "Failed to export analysis")