import tkinter as tk
from tkinter import ttk, messagebox
import logging
from datetime import datetime
from typing import Dict, List
from src.database.models import UserRole

logger = logging.getLogger(__name__)


class SalesScreen(ttk.Frame):
    def __init__(self, parent, services):
        super().__init__(parent)
        self.parent = parent
        self.services = services

        # Initialize variables
        self.current_sale_items = []
        self.selected_item = None

        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        """Create and arrange widgets"""
        # Main heading
        heading_frame = ttk.Frame(self)
        heading_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(
            heading_frame,
            text="Sales Management",
            font=("Helvetica", 16, "bold")
        ).pack(side="left")

        ttk.Button(
            heading_frame,
            text="New Sale",
            command=self.show_new_sale_dialog
        ).pack(side="right")

        # Create notebook for different views
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=5)

        # Create tabs
        self.create_active_sales_tab()
        self.create_sales_history_tab()
        self.create_reports_tab()

        # Pack main frame
        self.pack(fill="both", expand=True)

    def create_active_sales_tab(self):
        """Create active sales view"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Active Sales")

        # Split frame for sale entry and current sales
        sale_frame = ttk.Frame(tab)
        sale_frame.pack(fill="both", expand=True)

        # Left side - Sale Entry
        left_frame = ttk.LabelFrame(sale_frame, text="New Sale Entry")
        left_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        # Inventory items list
        inventory_frame = ttk.Frame(left_frame)
        inventory_frame.pack(fill="both", expand=True, padx=5, pady=5)

        ttk.Label(inventory_frame, text="Available Items:").pack(anchor="w")

        # Create treeview for inventory items
        columns = ("Item", "Stock", "Price")
        self.inventory_tree = ttk.Treeview(
            inventory_frame,
            columns=columns,
            show="headings",
            selectmode="browse",
            height=10
        )

        # Configure columns
        for col in columns:
            self.inventory_tree.heading(col, text=col)
            self.inventory_tree.column(col, width=100)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(
            inventory_frame,
            orient="vertical",
            command=self.inventory_tree.yview
        )
        self.inventory_tree.configure(yscrollcommand=scrollbar.set)

        # Pack treeview and scrollbar
        self.inventory_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Quantity frame
        quantity_frame = ttk.Frame(left_frame)
        quantity_frame.pack(fill="x", padx=5, pady=5)

        ttk.Label(quantity_frame, text="Quantity:").pack(side="left")
        self.quantity_var = tk.StringVar(value="1")
        quantity_entry = ttk.Entry(
            quantity_frame,
            textvariable=self.quantity_var,
            width=10
        )
        quantity_entry.pack(side="left", padx=5)

        ttk.Button(
            quantity_frame,
            text="Add to Sale",
            command=self.add_item_to_sale
        ).pack(side="left", padx=5)

        # Right side - Current Sale
        right_frame = ttk.LabelFrame(sale_frame, text="Current Sale")
        right_frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)

        # Create treeview for current sale items
        columns = ("Item", "Quantity", "Unit Price", "Total")
        self.sale_tree = ttk.Treeview(
            right_frame,
            columns=columns,
            show="headings",
            selectmode="browse",
            height=10
        )

        # Configure columns
        for col in columns:
            self.sale_tree.heading(col, text=col)
            self.sale_tree.column(col, width=100)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(
            right_frame,
            orient="vertical",
            command=self.sale_tree.yview
        )
        self.sale_tree.configure(yscrollcommand=scrollbar.set)

        # Pack treeview and scrollbar
        self.sale_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Total and payment frame
        payment_frame = ttk.Frame(right_frame)
        payment_frame.pack(fill="x", padx=5, pady=5)

        ttk.Label(payment_frame, text="Payment Method:").pack(side="left")
        self.payment_var = tk.StringVar(value="Cash")
        payment_combo = ttk.Combobox(
            payment_frame,
            textvariable=self.payment_var,
            values=["Cash", "Card", "Mobile"],
            state="readonly",
            width=15
        )
        payment_combo.pack(side="left", padx=5)

        self.total_var = tk.StringVar(value="Total: $0.00")
        ttk.Label(
            payment_frame,
            textvariable=self.total_var,
            font=("Helvetica", 12, "bold")
        ).pack(side="right")

        # Buttons frame
        buttons_frame = ttk.Frame(right_frame)
        buttons_frame.pack(fill="x", padx=5, pady=5)

        ttk.Button(
            buttons_frame,
            text="Remove Selected",
            command=self.remove_selected_item
        ).pack(side="left", padx=5)

        ttk.Button(
            buttons_frame,
            text="Clear Sale",
            command=self.clear_sale
        ).pack(side="left", padx=5)

        ttk.Button(
            buttons_frame,
            text="Complete Sale",
            command=self.complete_sale,
            style="Accent.TButton"
        ).pack(side="right", padx=5)

    def create_sales_history_tab(self):
        """Create sales history view"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Sales History")

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

        ttk.Button(
            controls_frame,
            text="Search",
            command=self.load_sales_history
        ).pack(side="left", padx=5)

        ttk.Button(
            controls_frame,
            text="Export",
            command=self.export_sales_history
        ).pack(side="right", padx=5)

        # Create treeview for sales history
        columns = ("Date", "Sale ID", "Items", "Total", "Payment", "User")
        self.history_tree = ttk.Treeview(
            tab,
            columns=columns,
            show="headings",
            selectmode="browse"
        )

        # Configure columns
        for col in columns:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=100)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(
            tab,
            orient="vertical",
            command=self.history_tree.yview
        )
        self.history_tree.configure(yscrollcommand=scrollbar.set)

        # Pack treeview and scrollbar
        self.history_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def create_reports_tab(self):
        """Create sales reports view"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Reports")

        # Controls frame
        controls_frame = ttk.Frame(tab)
        controls_frame.pack(fill="x", padx=5, pady=5)

        ttk.Label(controls_frame, text="Report Type:").pack(side="left")
        self.report_type_var = tk.StringVar(value="Daily Sales")
        report_combo = ttk.Combobox(
            controls_frame,
            textvariable=self.report_type_var,
            values=["Daily Sales", "Monthly Sales", "Product Performance"],
            state="readonly",
            width=20
        )
        report_combo.pack(side="left", padx=5)

        ttk.Button(
            controls_frame,
            text="Generate",
            command=self.generate_report
        ).pack(side="left", padx=5)

        ttk.Button(
            controls_frame,
            text="Export",
            command=self.export_report
        ).pack(side="right", padx=5)

        # Report content frame
        self.report_frame = ttk.Frame(tab)
        self.report_frame.pack(fill="both", expand=True, padx=5, pady=5)

    def load_data(self):
        """Load initial data"""
        try:
            # Load inventory items
            inventory = self.services['inventory'].get_inventory_status()

            # Clear existing items
            for item in self.inventory_tree.get_children():
                self.inventory_tree.delete(item)

            # Add items to treeview
            for item in inventory['items']:
                self.inventory_tree.insert("", "end", values=(
                    item['name'],
                    item['quantity'],
                    f"${item['unit_cost']:.2f}"
                ))

            # Load sales history
            self.load_sales_history()

        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            messagebox.showerror("Error", "Failed to load data")

    def add_item_to_sale(self):
        """Add selected item to current sale"""
        try:
            # Get selected inventory item
            selection = self.inventory_tree.selection()
            if not selection:
                messagebox.showwarning("Warning", "Please select an item")
                return

            # Get item details
            item = self.inventory_tree.item(selection)['values']

            # Validate quantity
            try:
                quantity = int(self.quantity_var.get())
                if quantity <= 0:
                    raise ValueError("Quantity must be positive")
                if quantity > item[1]:  # Check stock
                    raise ValueError("Insufficient stock")
            except ValueError as e:
                messagebox.showerror("Error", str(e))
                return

            # Add to current sale
            unit_price = float(item[2].replace('$', ''))
            total = quantity * unit_price

            self.sale_tree.insert("", "end", values=(
                item[0],
                quantity,
                f"${unit_price:.2f}",
                f"${total:.2f}"
            ))

            # Update total
            self.update_sale_total()

        except Exception as e:
            logger.error(f"Error adding item to sale: {str(e)}")
            messagebox.showerror("Error", "Failed to add item")

    def update_sale_total(self):
        """Update the total amount for current sale"""
        total = 0.0

        for item in self.sale_tree.get_children():
            item_total = float(
                self.sale_tree.item(item)['values'][3].replace('$', '')
            )
            total += item_total

        self.total_var.set(f"Total: ${total:.2f}")

    def remove_selected_item(self):
        """Remove selected item from current sale"""
        selection = self.sale_tree.selection()
        if selection:
            self.sale_tree.delete(selection)
            self.update_sale_total()

    def clear_sale(self):
        """Clear all items from current sale"""
        if messagebox.askyesno("Confirm", "Clear all items from current sale?"):
            for item in self.sale_tree.get_children():
                self.sale_tree.delete(item)
            self.update_sale_total()

    def complete_sale(self):
        """Complete the current sale"""
        try:
            if not self.sale_tree.get_children():
                messagebox.showwarning("Warning", "No items in current sale")
                return

            # Prepare sale items
            items = []
            for item in self.sale_tree.get_children():
                values = self.sale_tree.item(item)['values']
                items.append({
                    'name': values[0],
                    'quantity': values[1],
                    'unit_price': float(values[2].replace('$', '')),
                    'total': float(values[3].replace('$', ''))
                })

            # Create sale record
            sale = self.services['sales'].create_sale(
                items=items,
                payment_method=self.payment_var.get(),
                user_id=1  # TODO: Get actual user ID
            )

            messagebox.showinfo("Success", "Sale completed successfully!")

            # Clear current sale
            self.clear_sale()

            # Refresh data
            self.load_data()

        except Exception as e:
            logger.error(f"Error completing sale: {str(e)}")
            messagebox.showerror("Error", "Failed to complete sale")

    def load_sales_history(self):
        """Load sales history data"""
        try:
            # Get date range
            start_date = self.start_date_var.get()
            end_date = self.end_date_var.get()

            # Get sales history
            sales = self.services['sales'].get_sales_report(
                start_date=start_date,
                end_date=end_date
            )

            # Clear existing items
            for item in self.history_tree.get_children():
                self.history_tree.delete(item)

            # Add sales to treeview
            for sale in sales['sales_over_time']:
                self.history_tree.insert("", "end", values=(
                    sale['date'],
                    sale['id'],
                    len(sale['items']),
                    f"${sale['total_amount']:.2f}",
                    sale['payment_method'],
                    sale['user']['username']
                ))

        except Exception as e:
            logger.error(f"Error loading sales history: {str(e)}")
            messagebox.showerror("Error", "Failed to load sales history")

        def export_sales_history(self):
            """Export sales history to CSV"""
            try:
                start_date = self.start_date_var.get()
                end_date = self.end_date_var.get()

                # Generate report
                report_data = self.services['reporting'].export_report(
                    report_type='sales',
                    start_date=start_date,
                    end_date=end_date,
                    format='csv'
                )

                # Save file
                import tkinter.filedialog as filedialog
                filename = filedialog.asksaveasfilename(
                    defaultextension=".csv",
                    filetypes=[("CSV files", "*.csv")],
                    initialfile=f"sales_history_{start_date}_to_{end_date}.csv"
                )

                if filename:
                    with open(filename, 'wb') as f:
                        f.write(report_data)
                    messagebox.showinfo("Success", "Sales history exported successfully!")

            except Exception as e:
                logger.error(f"Error exporting sales history: {str(e)}")
                messagebox.showerror("Error", "Failed to export sales history")

        def generate_report(self):
            """Generate selected sales report"""
            try:
                # Clear report frame
                for widget in self.report_frame.winfo_children():
                    widget.destroy()

                report_type = self.report_type_var.get()

                if report_type == "Daily Sales":
                    self._generate_daily_sales_report()
                elif report_type == "Monthly Sales":
                    self._generate_monthly_sales_report()
                else:  # Product Performance
                    self._generate_product_performance_report()

            except Exception as e:
                logger.error(f"Error generating report: {str(e)}")
                messagebox.showerror("Error", "Failed to generate report")

        def _generate_daily_sales_report(self):
            """Generate daily sales report"""
            # Get today's date
            today = datetime.now().strftime('%Y-%m-%d')

            # Get sales data
            sales_data = self.services['sales'].get_daily_sales_summary(today)

            # Create report widgets
            ttk.Label(
                self.report_frame,
                text=f"Daily Sales Report - {today}",
                font=("Helvetica", 12, "bold")
            ).pack(pady=10)

            # Summary frame
            summary_frame = ttk.LabelFrame(self.report_frame, text="Summary")
            summary_frame.pack(fill="x", padx=5, pady=5)

            # Add summary info
            summary_info = [
                ("Total Sales:", f"${sales_data['summary']['total_sales']:.2f}"),
                ("Transactions:", str(sales_data['summary']['transaction_count'])),
                ("Average Sale:", f"${sales_data['summary']['average_sale']:.2f}")
            ]

            for i, (label, value) in enumerate(summary_info):
                ttk.Label(summary_frame, text=label).grid(row=i, column=0, padx=5, pady=2)
                ttk.Label(summary_frame, text=value).grid(row=i, column=1, padx=5, pady=2)

            # Top items frame
            items_frame = ttk.LabelFrame(self.report_frame, text="Top Selling Items")
            items_frame.pack(fill="x", padx=5, pady=5)

            # Create treeview for top items
            columns = ("Item", "Quantity", "Revenue")
            items_tree = ttk.Treeview(
                items_frame,
                columns=columns,
                show="headings",
                height=5
            )

            for col in columns:
                items_tree.heading(col, text=col)
                items_tree.column(col, width=100)

            items_tree.pack(fill="x", padx=5, pady=5)

            # Add top items
            for item in sales_data['top_items']:
                items_tree.insert("", "end", values=(
                    item['name'],
                    item['quantity'],
                    f"${item['revenue']:.2f}"
                ))

        def _generate_monthly_sales_report(self):
            """Generate monthly sales report"""
            # Get current month's date range
            today = datetime.now()
            start_date = today.replace(day=1).strftime('%Y-%m-%d')
            end_date = today.strftime('%Y-%m-%d')

            # Get sales data
            sales_data = self.services['sales'].get_sales_report(
                start_date=start_date,
                end_date=end_date,
                group_by='day'
            )

            # Create report widgets
            ttk.Label(
                self.report_frame,
                text=f"Monthly Sales Report - {today.strftime('%B %Y')}",
                font=("Helvetica", 12, "bold")
            ).pack(pady=10)

            # Summary frame
            summary_frame = ttk.LabelFrame(self.report_frame, text="Summary")
            summary_frame.pack(fill="x", padx=5, pady=5)

            # Add summary info
            summary_info = [
                ("Total Revenue:", f"${sales_data['summary']['total_revenue']:.2f}"),
                ("Total Transactions:", str(sales_data['summary']['total_transactions'])),
                ("Average Transaction:", f"${sales_data['summary']['average_transaction']:.2f}")
            ]

            for i, (label, value) in enumerate(summary_info):
                ttk.Label(summary_frame, text=label).grid(row=i, column=0, padx=5, pady=2)
                ttk.Label(summary_frame, text=value).grid(row=i, column=1, padx=5, pady=2)

            # Daily sales frame
            daily_frame = ttk.LabelFrame(self.report_frame, text="Daily Sales")
            daily_frame.pack(fill="both", expand=True, padx=5, pady=5)

            # Create treeview for daily sales
            columns = ("Date", "Sales", "Transactions", "Average")
            daily_tree = ttk.Treeview(
                daily_frame,
                columns=columns,
                show="headings"
            )

            for col in columns:
                daily_tree.heading(col, text=col)
                daily_tree.column(col, width=100)

            # Add scrollbar
            scrollbar = ttk.Scrollbar(
                daily_frame,
                orient="vertical",
                command=daily_tree.yview
            )
            daily_tree.configure(yscrollcommand=scrollbar.set)

            daily_tree.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

            # Add daily sales data
            for day in sales_data['sales_over_time']:
                daily_tree.insert("", "end", values=(
                    day['date'],
                    f"${day['total_amount']:.2f}",
                    day['transaction_count'],
                    f"${day['average_sale']:.2f}"
                ))

        def _generate_product_performance_report(self):
            """Generate product performance report"""
            # Get current month's date range
            today = datetime.now()
            start_date = today.replace(day=1).strftime('%Y-%m-%d')
            end_date = today.strftime('%Y-%m-%d')

            # Get top selling items
            items_data = self.services['sales'].get_top_selling_items(
                start_date=start_date,
                end_date=end_date,
                limit=10
            )

            # Create report widgets
            ttk.Label(
                self.report_frame,
                text=f"Product Performance Report - {today.strftime('%B %Y')}",
                font=("Helvetica", 12, "bold")
            ).pack(pady=10)

            # Create treeview for products
            columns = ("Product", "Units Sold", "Revenue", "Average Price")
            product_tree = ttk.Treeview(
                self.report_frame,
                columns=columns,
                show="headings"
            )

            for col in columns:
                product_tree.heading(col, text=col)
                product_tree.column(col, width=100)

            # Add scrollbar
            scrollbar = ttk.Scrollbar(
                self.report_frame,
                orient="vertical",
                command=product_tree.yview
            )
            product_tree.configure(yscrollcommand=scrollbar.set)

            product_tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)
            scrollbar.pack(side="right", fill="y")

            # Add product data
            for item in items_data:
                avg_price = item['revenue'] / item['quantity'] if item['quantity'] > 0 else 0
                product_tree.insert("", "end", values=(
                    item['name'],
                    item['quantity'],
                    f"${item['revenue']:.2f}",
                    f"${avg_price:.2f}"
                ))

        def export_report(self):
            """Export current report"""
            try:
                report_type = self.report_type_var.get().lower().replace(" ", "_")

                # Generate report
                report_data = self.services['reporting'].export_report(
                    report_type=report_type,
                    start_date=datetime.now().strftime('%Y-%m-%d'),  # Today
                    end_date=datetime.now().strftime('%Y-%m-%d'),
                    format='pdf'
                )

                # Save file
                import tkinter.filedialog as filedialog
                filename = filedialog.asksaveasfilename(
                    defaultextension=".pdf",
                    filetypes=[("PDF files", "*.pdf")],
                    initialfile=f"{report_type}_report_{datetime.now().strftime('%Y%m%d')}.pdf"
                )

                if filename:
                    with open(filename, 'wb') as f:
                        f.write(report_data)
                    messagebox.showinfo("Success", "Report exported successfully!")

            except Exception as e:
                logger.error(f"Error exporting report: {str(e)}")
                messagebox.showerror("Error", "Failed to export report")