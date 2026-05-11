from typing import Dict, Optional
import tkinter as tk
from tkinter import ttk, messagebox
import logging
from datetime import datetime, timedelta
from decimal import Decimal

try:
    from src.gui.styles import (CREAM, CARD_BG, ESPRESSO, MEDIUM_BROWN, DARK_BROWN,
                                 LIGHT_BROWN, BORDER, TEXT_DARK, TEXT_LIGHT, TEXT_MID,
                                 SUCCESS, WARNING, DANGER, FONT_H2, FONT_H3,
                                 FONT_BODY, FONT_SMALL)
    _HAS_STYLES = True
except ImportError:
    _HAS_STYLES = False


class DatePicker(ttk.Entry):
    """Simple date entry widget (YYYY-MM-DD format)."""
    def __init__(self, parent, textvariable=None, **kwargs):
        super().__init__(parent, textvariable=textvariable, width=12, **kwargs)

logger = logging.getLogger(__name__)


class ReportsScreen(ttk.Frame):
    def __init__(self, parent, services: Dict):
        super().__init__(parent)
        self.parent = parent
        self.services = services

        # Initialize variables
        self.report_type_var = tk.StringVar(value="Daily Sales")
        self.start_date_var = tk.StringVar(
            value=(datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        )
        self.end_date_var = tk.StringVar(
            value=datetime.now().strftime("%Y-%m-%d")
        )

        self.create_widgets()
        self.load_initial_data()

    def create_widgets(self):
        bg = CREAM if _HAS_STYLES else "#f0f0f0"

        # Page header
        hdr = tk.Frame(self, bg=bg)
        hdr.pack(fill="x")
        tk.Frame(hdr, bg=MEDIUM_BROWN if _HAS_STYLES else "#8B5E3C", height=3).pack(fill="x")

        inner_hdr = tk.Frame(hdr, bg=bg, pady=14, padx=24)
        inner_hdr.pack(fill="x")

        title_col = tk.Frame(inner_hdr, bg=bg)
        title_col.pack(side="left")
        tk.Label(title_col, text="Reports & Analytics",
                 font=("Helvetica", 18, "bold"),
                 bg=bg, fg=ESPRESSO if _HAS_STYLES else "black").pack(anchor="w")
        tk.Label(title_col, text="Generate and export financial reports",
                 font=("Helvetica", 9),
                 bg=bg, fg=TEXT_MID if _HAS_STYLES else "#555").pack(anchor="w", pady=(2, 0))

        export_btn = tk.Button(inner_hdr, text="  Export CSV  ",
                               font=("Helvetica", 10),
                               bg=CARD_BG if _HAS_STYLES else "white",
                               fg=MEDIUM_BROWN if _HAS_STYLES else "#8B5E3C",
                               activebackground=BORDER if _HAS_STYLES else "#ccc",
                               relief="flat", bd=0, cursor="hand2",
                               highlightbackground=BORDER if _HAS_STYLES else "#ccc",
                               highlightthickness=1,
                               command=self.export_report)
        export_btn.pack(side="right", ipady=8)

        tk.Frame(hdr, bg=BORDER if _HAS_STYLES else "#ccc", height=1).pack(fill="x")

        # Controls bar
        ctrl = tk.Frame(self, bg=CARD_BG if _HAS_STYLES else "white",
                        pady=10, padx=16,
                        highlightbackground=BORDER if _HAS_STYLES else "#ccc",
                        highlightthickness=1)
        ctrl.pack(fill="x", padx=12, pady=(8, 4))

        tk.Label(ctrl, text="Report Type",
                 font=("Helvetica", 9, "bold"),
                 bg=CARD_BG if _HAS_STYLES else "white",
                 fg=TEXT_MID if _HAS_STYLES else "#555").pack(side="left")
        report_types = ["Daily Sales", "Monthly Sales", "Product Performance"]
        report_combo = ttk.Combobox(ctrl, textvariable=self.report_type_var,
                                    values=report_types, state="readonly", width=22)
        report_combo.pack(side="left", padx=(6, 20))

        tk.Label(ctrl, text="From",
                 font=("Helvetica", 9, "bold"),
                 bg=CARD_BG if _HAS_STYLES else "white",
                 fg=TEXT_MID if _HAS_STYLES else "#555").pack(side="left")
        DatePicker(ctrl, self.start_date_var).pack(side="left", padx=(4, 0))
        tk.Label(ctrl, text="  to",
                 font=("Helvetica", 9, "bold"),
                 bg=CARD_BG if _HAS_STYLES else "white",
                 fg=TEXT_MID if _HAS_STYLES else "#555").pack(side="left")
        DatePicker(ctrl, self.end_date_var).pack(side="left", padx=(4, 20))

        gen_btn = tk.Button(ctrl, text="  Generate Report  ",
                            font=("Helvetica", 10, "bold"),
                            bg=MEDIUM_BROWN if _HAS_STYLES else "#8B5E3C",
                            fg="white",
                            activebackground=DARK_BROWN if _HAS_STYLES else "#4A2C17",
                            activeforeground="white",
                            relief="flat", bd=0, cursor="hand2",
                            command=self.generate_report)
        gen_btn.pack(side="left", ipady=6)

        # Report display area
        outer = tk.Frame(self, bg=bg)
        outer.pack(fill="both", expand=True, padx=12, pady=4)
        self.report_frame = ttk.Frame(outer)
        self.report_frame.pack(fill="both", expand=True)

        self.pack(fill="both", expand=True)
        report_combo.bind("<<ComboboxSelected>>", lambda e: self.generate_report())

    def load_initial_data(self):
        """Load initial report"""
        self.generate_report()

    def generate_report(self):
        """Generate selected report"""
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
        try:
            # Get today's date
            today = datetime.now().strftime('%Y-%m-%d')

            # Get sales data
            report_data = self.services['reporting'].generate_daily_report(today)

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
                ("Total Sales:", f"${report_data['overview']['total_sales']:,.2f}"),
                ("Transactions:", str(report_data['overview']['transaction_count'])),
                ("Average Sale:",
                 f"${report_data['overview']['total_sales'] / report_data['overview']['transaction_count']:,.2f}"
                 if report_data['overview']['transaction_count'] > 0 else "$0.00")
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
            for item in report_data['sales']['top_items']:
                items_tree.insert("", "end", values=(
                    item['name'],
                    item['quantity'],
                    f"${item['revenue']:,.2f}"
                ))

        except Exception as e:
            logger.error(f"Error generating daily sales report: {str(e)}")
            raise

    def _generate_monthly_sales_report(self):
        """Generate monthly sales report"""
        try:
            start_date = self.start_date_var.get()
            end_date = self.end_date_var.get()

            # Get sales data
            report_data = self.services['reporting'].generate_periodic_report(
                start_date=start_date,
                end_date=end_date,
                group_by='day'
            )

            # Create report widgets
            ttk.Label(
                self.report_frame,
                text=f"Monthly Sales Report",
                font=("Helvetica", 12, "bold")
            ).pack(pady=10)

            # Summary frame
            summary_frame = ttk.LabelFrame(self.report_frame, text="Summary")
            summary_frame.pack(fill="x", padx=5, pady=5)

            # Add summary info
            summary_info = [
                ("Total Revenue:", f"${report_data['overview']['total_sales']:,.2f}"),
                ("Total Transactions:", str(report_data['overview']['total_transactions'])),
                ("Average Transaction:",
                 f"${report_data['overview']['total_sales'] / report_data['overview']['total_transactions']:,.2f}"
                 if report_data['overview']['total_transactions'] > 0 else "$0.00")
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
            for day in report_data['sales_analysis']['over_time']:
                avg_sale = (day['total_amount'] / day['transaction_count']
                            if day['transaction_count'] > 0 else 0)
                daily_tree.insert("", "end", values=(
                    day['date'],
                    f"${day['total_amount']:,.2f}",
                    day['transaction_count'],
                    f"${avg_sale:,.2f}"
                ))

        except Exception as e:
            logger.error(f"Error generating monthly sales report: {str(e)}")
            raise

    def _generate_product_performance_report(self):
        """Generate product performance report"""
        try:
            start_date = self.start_date_var.get()
            end_date = self.end_date_var.get()

            # Get products data
            products = self.services['sales'].get_top_selling_items(
                start_date=start_date,
                end_date=end_date,
                limit=20
            )

            # Create report widgets
            ttk.Label(
                self.report_frame,
                text="Product Performance Report",
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
                product_tree.column(col, width=150)

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
            for product in products:
                avg_price = (product['revenue'] / product['quantity']
                             if product['quantity'] > 0 else 0)
                product_tree.insert("", "end", values=(
                    product['name'],
                    product['quantity'],
                    f"${product['revenue']:,.2f}",
                    f"${avg_price:,.2f}"
                ))

        except Exception as e:
            logger.error(f"Error generating product performance report: {str(e)}")
            raise

    def export_report(self):
        """Export current report"""
        _TYPE_MAP = {
            "Daily Sales": "daily",
            "Monthly Sales": "periodic",
            "Product Performance": "periodic",
        }
        try:
            selected = self.report_type_var.get()
            report_type = _TYPE_MAP.get(selected, "periodic")
            safe_name = selected.lower().replace(" ", "_")

            report_data = self.services['reporting'].export_report(
                report_type=report_type,
                start_date=self.start_date_var.get(),
                end_date=self.end_date_var.get(),
                format='csv'
            )

            from tkinter import filedialog
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv")],
                initialfile=f"{safe_name}_report_{datetime.now().strftime('%Y%m%d')}.csv"
            )

            if filename:
                with open(filename, 'wb') as f:
                    f.write(report_data)
                messagebox.showinfo("Success", "Report exported successfully!")

        except Exception as e:
            logger.error(f"Error exporting report: {str(e)}")
            messagebox.showerror("Error", "Failed to export report")