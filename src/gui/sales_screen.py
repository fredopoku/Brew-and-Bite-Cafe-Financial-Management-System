import tkinter as tk
from tkinter import ttk, messagebox
import logging
from datetime import datetime
from typing import Dict, List
from src.database.models import UserRole

try:
    from src.gui.styles import (CREAM, CARD_BG, ESPRESSO, MEDIUM_BROWN, DARK_BROWN,
                                 LIGHT_BROWN, BORDER, TEXT_DARK, TEXT_LIGHT, TEXT_MID,
                                 SUCCESS, WARNING, DANGER, FONT_H2, FONT_H3,
                                 FONT_BODY, FONT_SMALL)
    _HAS_STYLES = True
except ImportError:
    _HAS_STYLES = False

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
        bg = CREAM if _HAS_STYLES else "#f0f0f0"

        # Page header
        hdr = tk.Frame(self, bg=bg)
        hdr.pack(fill="x")
        tk.Frame(hdr, bg=MEDIUM_BROWN if _HAS_STYLES else "#8B5E3C", height=3).pack(fill="x")

        inner_hdr = tk.Frame(hdr, bg=bg, pady=14, padx=24)
        inner_hdr.pack(fill="x")

        title_col = tk.Frame(inner_hdr, bg=bg)
        title_col.pack(side="left")
        tk.Label(title_col, text="Sales Management",
                 font=("Helvetica", 18, "bold"),
                 bg=bg, fg=ESPRESSO if _HAS_STYLES else "black").pack(anchor="w")
        tk.Label(title_col, text="Manage transactions and view sales history",
                 font=("Helvetica", 9),
                 bg=bg, fg=TEXT_MID if _HAS_STYLES else "#555").pack(anchor="w", pady=(2, 0))

        new_sale_btn = tk.Button(inner_hdr, text="  + New Sale  ",
                                 font=("Helvetica", 10, "bold"),
                                 bg=MEDIUM_BROWN if _HAS_STYLES else "#8B5E3C",
                                 fg="white",
                                 activebackground=DARK_BROWN if _HAS_STYLES else "#4A2C17",
                                 activeforeground="white",
                                 relief="flat", bd=0, cursor="hand2",
                                 command=self.show_new_sale_dialog)
        new_sale_btn.pack(side="right", ipady=8)

        tk.Frame(hdr, bg=BORDER if _HAS_STYLES else "#ccc", height=1).pack(fill="x")

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=12, pady=8)

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

    def show_new_sale_dialog(self):
        """Open a focused POS dialog for a new sale."""
        bg = CREAM if _HAS_STYLES else "#f0f0f0"

        try:
            inventory = self.services['inventory'].get_inventory_status()
            items = [i for i in inventory['items'] if i['quantity'] > 0]
        except Exception as e:
            logger.error(f"Inventory load error: {e}")
            messagebox.showerror("Error", "Could not load inventory")
            return

        dlg = tk.Toplevel(self)
        dlg.title("New Sale")
        dlg.geometry("700x540")
        dlg.minsize(600, 460)
        dlg.configure(bg=bg)
        dlg.grab_set()

        # Header
        hdr = tk.Frame(dlg, bg=MEDIUM_BROWN if _HAS_STYLES else "#8B5E3C", pady=10)
        hdr.pack(fill="x")
        tk.Label(hdr, text="Point of Sale",
                 font=("Helvetica", 14, "bold"),
                 bg=MEDIUM_BROWN if _HAS_STYLES else "#8B5E3C", fg="white").pack(side="left", padx=16)

        body = tk.Frame(dlg, bg=bg)
        body.pack(fill="both", expand=True, padx=12, pady=10)
        body.grid_columnconfigure(0, weight=1)
        body.grid_columnconfigure(1, weight=1)
        body.grid_rowconfigure(0, weight=1)

        # Left: item selection
        left = tk.Frame(body, bg=bg)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

        tk.Label(left, text="Available Items", font=("Helvetica", 10, "bold"),
                 bg=bg, fg=ESPRESSO if _HAS_STYLES else "black").pack(anchor="w", pady=(0, 4))

        # Search bar
        search_frame = tk.Frame(left, bg=bg)
        search_frame.pack(fill="x", pady=(0, 4))
        search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=search_var)
        search_entry.pack(fill="x")

        inv_cols = ("Name", "Stock", "Price")
        inv_tree = ttk.Treeview(left, columns=inv_cols, show="headings",
                                selectmode="browse", height=14)
        for col, w in [("Name", 160), ("Stock", 60), ("Price", 70)]:
            inv_tree.heading(col, text=col)
            inv_tree.column(col, width=w)

        inv_sb = ttk.Scrollbar(left, orient="vertical", command=inv_tree.yview)
        inv_tree.configure(yscrollcommand=inv_sb.set)
        inv_tree.pack(side="left", fill="both", expand=True)
        inv_sb.pack(side="right", fill="y")

        def populate_inv(filter_text=""):
            inv_tree.delete(*inv_tree.get_children())
            for it in items:
                if filter_text.lower() in it['name'].lower():
                    inv_tree.insert("", "end", values=(
                        it['name'], it['quantity'],
                        f"${it['unit_cost']:.2f}"
                    ))

        populate_inv()
        search_var.trace_add('write', lambda *_: populate_inv(search_entry.get()))

        # Qty row
        qty_row = tk.Frame(left, bg=bg)
        qty_row.pack(fill="x", pady=(6, 0))
        tk.Label(qty_row, text="Qty:", bg=bg,
                 font=FONT_SMALL if _HAS_STYLES else ("Helvetica", 10)).pack(side="left")
        qty_var = tk.StringVar(value="1")
        qty_entry = ttk.Entry(qty_row, textvariable=qty_var, width=6)
        qty_entry.pack(side="left", padx=4)

        # Right: current sale
        right = tk.Frame(body, bg=bg)
        right.grid(row=0, column=1, sticky="nsew", padx=(6, 0))

        tk.Label(right, text="Current Sale", font=("Helvetica", 10, "bold"),
                 bg=bg, fg=ESPRESSO if _HAS_STYLES else "black").pack(anchor="w", pady=(0, 4))

        sale_cols = ("Item", "Qty", "Unit", "Total")
        sale_tree = ttk.Treeview(right, columns=sale_cols, show="headings",
                                 selectmode="browse", height=14)
        for col, w in [("Item", 140), ("Qty", 40), ("Unit", 65), ("Total", 70)]:
            sale_tree.heading(col, text=col)
            sale_tree.column(col, width=w)

        sale_sb = ttk.Scrollbar(right, orient="vertical", command=sale_tree.yview)
        sale_tree.configure(yscrollcommand=sale_sb.set)
        sale_tree.pack(side="left", fill="both", expand=True)
        sale_sb.pack(side="right", fill="y")

        sale_items = []

        def refresh_sale_tree():
            sale_tree.delete(*sale_tree.get_children())
            for si in sale_items:
                sale_tree.insert("", "end", values=(
                    si['name'], si['qty'],
                    f"${si['unit']:.2f}", f"${si['total']:.2f}"
                ))

        def add_item():
            sel = inv_tree.selection()
            if not sel:
                messagebox.showwarning("Select Item", "Please select an item first.", parent=dlg)
                return
            vals = inv_tree.item(sel[0])['values']
            try:
                qty = int(qty_entry.get())
                if qty <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Quantity must be a positive integer.", parent=dlg)
                return
            stock = int(vals[1])
            if qty > stock:
                messagebox.showerror("Error", f"Only {stock} in stock.", parent=dlg)
                return
            unit = float(str(vals[2]).replace("$", ""))
            name = str(vals[0])
            # Look up inventory_item_id by name
            inv_item = next((it for it in items if it['name'] == name), None)
            if not inv_item:
                messagebox.showerror("Error", f"Could not find item '{name}'.", parent=dlg)
                return
            item_id = inv_item['id']
            # Merge if same item already in sale
            for si in sale_items:
                if si['name'] == name:
                    si['qty']   += qty
                    si['total']  = si['qty'] * si['unit']
                    refresh_sale_tree()
                    update_total()
                    return
            sale_items.append({'name': name, 'qty': qty, 'unit': unit,
                               'total': qty * unit, 'item_id': item_id})
            refresh_sale_tree()
            update_total()

        def remove_item():
            sel = sale_tree.selection()
            if not sel:
                return
            idx = sale_tree.index(sel[0])
            if 0 <= idx < len(sale_items):
                sale_items.pop(idx)
            refresh_sale_tree()
            update_total()

        def update_total():
            t = sum(si['total'] for si in sale_items)
            total_lbl.config(text=f"Total: ${t:,.2f}")

        ttk.Button(qty_row, text="Add →",
                   style="Primary.TButton" if _HAS_STYLES else "TButton",
                   command=add_item).pack(side="left", padx=4)
        ttk.Button(qty_row, text="Remove",
                   style="Danger.TButton" if _HAS_STYLES else "TButton",
                   command=remove_item).pack(side="left")

        # Footer
        footer = tk.Frame(dlg, bg=bg, pady=8)
        footer.pack(fill="x", padx=12)

        tk.Label(footer, text="Payment:",
                 bg=bg, font=FONT_SMALL if _HAS_STYLES else ("Helvetica", 10)).pack(side="left")
        pay_var = tk.StringVar(value="Cash")
        pay_combo = ttk.Combobox(footer, textvariable=pay_var,
                                 values=["Cash", "Card", "Mobile"],
                                 state="readonly", width=10)
        pay_combo.pack(side="left", padx=(4, 16))

        total_lbl = tk.Label(footer, text="Total: $0.00",
                             font=("Helvetica", 14, "bold"),
                             bg=bg, fg=ESPRESSO if _HAS_STYLES else "black")
        total_lbl.pack(side="left")

        ttk.Button(footer, text="Cancel",
                   style="Secondary.TButton" if _HAS_STYLES else "TButton",
                   command=dlg.destroy).pack(side="right", padx=(6, 0))

        def complete():
            if not sale_items:
                messagebox.showwarning("Empty Sale", "Please add items to the sale.", parent=dlg)
                return
            payment = pay_combo.get()
            try:
                api_items = [
                    {'inventory_item_id': si['item_id'],
                     'quantity': si['qty'],
                     'unit_price': si['unit']}
                    for si in sale_items
                ]
                self.services['sales'].create_sale(
                    items=api_items,
                    payment_method=payment,
                    user_id=1
                )
                total = sum(si['total'] for si in sale_items)
                messagebox.showinfo(
                    "Sale Complete",
                    f"Sale completed successfully!\n\n"
                    f"Items: {len(sale_items)}\n"
                    f"Payment: {payment}\n"
                    f"Total: ${total:,.2f}",
                    parent=dlg
                )
                dlg.destroy()
                self.load_data()
            except Exception as ex:
                logger.error(f"Complete sale error: {ex}")
                messagebox.showerror("Error", str(ex) or "Failed to complete sale", parent=dlg)

        ttk.Button(footer, text="Complete Sale",
                   style="Success.TButton" if _HAS_STYLES else "TButton",
                   command=complete).pack(side="right")

        inv_tree.bind("<Double-1>", lambda e: add_item())
        dlg.bind("<Return>", lambda e: add_item())

    def load_data(self):
        """Load initial data — each section fails independently."""
        # Load inventory items
        try:
            inventory = self.services['inventory'].get_inventory_status()
            self._item_id_map = {}
            for item in self.inventory_tree.get_children():
                self.inventory_tree.delete(item)
            for item in inventory['items']:
                self._item_id_map[item['name']] = item['id']
                self.inventory_tree.insert("", "end", values=(
                    item['name'],
                    item['quantity'],
                    f"${item['unit_cost']:.2f}"
                ))
        except Exception as e:
            logger.error(f"Inventory load error: {e}")
            try:
                self.services['inventory'].session.rollback()
            except Exception:
                pass

        # Load sales history
        self.load_sales_history()

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

            id_map = getattr(self, '_item_id_map', {})

            # Prepare sale items
            items = []
            for item in self.sale_tree.get_children():
                values = self.sale_tree.item(item)['values']
                name = str(values[0])
                item_id = id_map.get(name)
                if not item_id:
                    messagebox.showerror("Error", f"Cannot find inventory ID for '{name}'. Reload and try again.")
                    return
                items.append({
                    'inventory_item_id': item_id,
                    'quantity': int(values[1]),
                    'unit_price': float(str(values[2]).replace('$', '')),
                })

            self.services['sales'].create_sale(
                items=items,
                payment_method=self.payment_var.get(),
                user_id=1
            )

            messagebox.showinfo("Success", "Sale completed successfully!")
            self.clear_sale()
            self.load_data()

        except Exception as e:
            logger.error(f"Error completing sale: {str(e)}")
            messagebox.showerror("Error", str(e) or "Failed to complete sale")

    def load_sales_history(self):
        """Load sales history data"""
        try:
            # Get date range
            start_date = self.start_date_var.get()
            end_date = self.end_date_var.get()

            # Get sales history
            sales = self.services['sales'].get_sales(
                start_date=start_date,
                end_date=end_date
            )

            # Clear existing items
            for item in self.history_tree.get_children():
                self.history_tree.delete(item)

            # Add sales to treeview
            for sale in sales:
                self.history_tree.insert("", "end", values=(
                    sale['date'][:10],
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

            report_data = self.services['reporting'].export_report(
                report_type='periodic',
                start_date=start_date,
                end_date=end_date,
                format='csv'
            )

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
        _TYPE_MAP = {
            "Daily Sales": "daily",
            "Monthly Sales": "periodic",
            "Product Performance": "periodic",
        }
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            selected = self.report_type_var.get()
            report_type = _TYPE_MAP.get(selected, "periodic")

            report_data = self.services['reporting'].export_report(
                report_type=report_type,
                start_date=today,
                end_date=today,
                format='csv'
            )

            import tkinter.filedialog as filedialog
            safe_name = selected.lower().replace(" ", "_")
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