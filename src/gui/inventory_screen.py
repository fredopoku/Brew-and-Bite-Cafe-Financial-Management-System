import tkinter as tk
from tkinter import ttk, messagebox
import logging
from datetime import datetime
from decimal import Decimal
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class InventoryScreen(ttk.Frame):
    def __init__(self, parent, services):
        super().__init__(parent)
        self.parent = parent
        self.services = services
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
            text="Inventory Management",
            font=("Helvetica", 16, "bold")
        ).pack(side="left")

        ttk.Button(
            heading_frame,
            text="Add New Item",
            command=self.show_add_item_dialog
        ).pack(side="right", padx=5)

        ttk.Button(
            heading_frame,
            text="Stock Adjustment",
            command=self.show_adjustment_dialog
        ).pack(side="right", padx=5)

        # Create notebook for different views
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=5)

        # Create tabs
        self.create_inventory_tab()
        self.create_transactions_tab()
        self.create_alerts_tab()

        # Pack main frame
        self.pack(fill="both", expand=True)

    def create_inventory_tab(self):
        """Create main inventory view"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Current Stock")

        # Controls frame
        controls_frame = ttk.Frame(tab)
        controls_frame.pack(fill="x", padx=5, pady=5)

        # Search
        ttk.Label(controls_frame, text="Search:").pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.filter_inventory())
        search_entry = ttk.Entry(
            controls_frame,
            textvariable=self.search_var,
            width=30
        )
        search_entry.pack(side="left", padx=5)

        # Filter by status
        ttk.Label(controls_frame, text="Status:").pack(side="left", padx=(20, 5))
        self.status_var = tk.StringVar(value="All")
        status_combo = ttk.Combobox(
            controls_frame,
            textvariable=self.status_var,
            values=["All", "In Stock", "Low Stock", "Out of Stock"],
            state="readonly",
            width=15
        )
        status_combo.pack(side="left", padx=5)
        status_combo.bind('<<ComboboxSelected>>', lambda e: self.filter_inventory())

        # Export button
        ttk.Button(
            controls_frame,
            text="Export",
            command=self.export_inventory
        ).pack(side="right", padx=5)

        # Create main inventory treeview
        columns = ("ID", "Item", "Quantity", "Unit Cost", "Total Value", "Reorder Level", "Status")
        self.inventory_tree = ttk.Treeview(
            tab,
            columns=columns,
            show="headings",
            selectmode="browse"
        )

        # Configure columns
        self.inventory_tree.heading("ID", text="ID")
        self.inventory_tree.column("ID", width=50)
        self.inventory_tree.heading("Item", text="Item")
        self.inventory_tree.column("Item", width=200)
        self.inventory_tree.heading("Quantity", text="Quantity")
        self.inventory_tree.column("Quantity", width=100)
        self.inventory_tree.heading("Unit Cost", text="Unit Cost")
        self.inventory_tree.column("Unit Cost", width=100)
        self.inventory_tree.heading("Total Value", text="Total Value")
        self.inventory_tree.column("Total Value", width=100)
        self.inventory_tree.heading("Reorder Level", text="Reorder Level")
        self.inventory_tree.column("Reorder Level", width=100)
        self.inventory_tree.heading("Status", text="Status")
        self.inventory_tree.column("Status", width=100)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(
            tab,
            orient="vertical",
            command=self.inventory_tree.yview
        )
        self.inventory_tree.configure(yscrollcommand=scrollbar.set)

        # Pack treeview and scrollbar
        self.inventory_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Bind context menu
        self.inventory_tree.bind("<Button-3>", self.show_context_menu)
        self.inventory_tree.bind("<Double-1>", self.show_item_details)

        # Create context menu
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Edit Item", command=self.show_edit_dialog)
        self.context_menu.add_command(label="Adjust Stock", command=self.show_adjustment_dialog)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="View History", command=self.show_item_history)

    def create_transactions_tab(self):
        """Create transactions history view"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Transactions")

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

        # Transaction type filter
        ttk.Label(controls_frame, text="Type:").pack(side="left", padx=(20, 5))
        self.trans_type_var = tk.StringVar(value="All")
        type_combo = ttk.Combobox(
            controls_frame,
            textvariable=self.trans_type_var,
            values=["All", "Restock", "Sale", "Adjustment"],
            state="readonly",
            width=15
        )
        type_combo.pack(side="left", padx=5)

        # Search button
        ttk.Button(
            controls_frame,
            text="Search",
            command=self.load_transactions
        ).pack(side="left", padx=5)

        # Export button
        ttk.Button(
            controls_frame,
            text="Export",
            command=self.export_transactions
        ).pack(side="right", padx=5)

        # Create transactions treeview
        columns = ("Date", "Item", "Type", "Quantity", "User", "Notes")
        self.transactions_tree = ttk.Treeview(
            tab,
            columns=columns,
            show="headings",
            selectmode="browse"
        )

        # Configure columns
        for col in columns:
            self.transactions_tree.heading(col, text=col)
            if col == "Item":
                self.transactions_tree.column(col, width=200)
            elif col == "Notes":
                self.transactions_tree.column(col, width=300)
            else:
                self.transactions_tree.column(col, width=100)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(
            tab,
            orient="vertical",
            command=self.transactions_tree.yview
        )
        self.transactions_tree.configure(yscrollcommand=scrollbar.set)

        # Pack treeview and scrollbar
        self.transactions_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def create_alerts_tab(self):
        """Create inventory alerts view"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Alerts")

        # Create alerts treeview
        columns = ("Priority", "Item", "Current Stock", "Reorder Level", "Status")
        self.alerts_tree = ttk.Treeview(
            tab,
            columns=columns,
            show="headings",
            selectmode="browse"
        )

        # Configure columns
        self.alerts_tree.heading("Priority", text="!")
        self.alerts_tree.column("Priority", width=30)
        self.alerts_tree.heading("Item", text="Item")
        self.alerts_tree.column("Item", width=200)
        self.alerts_tree.heading("Current Stock", text="Current Stock")
        self.alerts_tree.column("Current Stock", width=100)
        self.alerts_tree.heading("Reorder Level", text="Reorder Level")
        self.alerts_tree.column("Reorder Level", width=100)
        self.alerts_tree.heading("Status", text="Status")
        self.alerts_tree.column("Status", width=100)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(
            tab,
            orient="vertical",
            command=self.alerts_tree.yview
        )
        self.alerts_tree.configure(yscrollcommand=scrollbar.set)

        # Pack treeview and scrollbar
        self.alerts_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Add button to generate reorder report
        ttk.Button(
            tab,
            text="Generate Reorder Report",
            command=self.generate_reorder_report
        ).pack(side="bottom", pady=10)

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
                total_value = item['quantity'] * item['unit_cost']
                status = (
                    "Out of Stock" if item['quantity'] == 0
                    else "Low Stock" if item['quantity'] <= item['reorder_level']
                    else "In Stock"
                )

                self.inventory_tree.insert("", "end", values=(
                    item['id'],
                    item['name'],
                    item['quantity'],
                    f"${item['unit_cost']:.2f}",
                    f"${total_value:.2f}",
                    item['reorder_level'],
                    status
                ))

            # Load transactions
            self.load_transactions()

            # Load alerts
            self.load_alerts()

        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            messagebox.showerror("Error", "Failed to load inventory data")

    def filter_inventory(self):
        """Filter inventory based on search and status"""
        try:
            search_term = self.search_var.get().lower()
            status_filter = self.status_var.get()

            # Show all items first
            for item in self.inventory_tree.get_children():
                self.inventory_tree.item(item, tags=())

            # Apply filters
            for item in self.inventory_tree.get_children():
                values = self.inventory_tree.item(item)['values']
                item_name = str(values[1]).lower()
                status = str(values[6])

                show_item = True

                # Apply search filter
                if search_term and search_term not in item_name:
                    show_item = False

                # Apply status filter
                if status_filter != "All" and status_filter != status:
                    show_item = False

                # Hide or show item
                if show_item:
                    self.inventory_tree.item(item, tags=())
                else:
                    self.inventory_tree.detach(item)

        except Exception as e:
            logger.error(f"Error filtering inventory: {str(e)}")

    def show_context_menu(self, event):
        """Show context menu for selected item"""
        item = self.inventory_tree.identify_row(event.y)
        if item:
            self.inventory_tree.selection_set(item)
            self.selected_item = self.inventory_tree.item(item)['values']
            self.context_menu.post(event.x_root, event.y_root)

    def show_item_details(self, event):
        """Show details for double-clicked item"""
        item = self.inventory_tree.selection()
        if item:
            self.selected_item = self.inventory_tree.item(item)['values']
            self.show_edit_dialog()

    def show_add_item_dialog(self):
        """Show dialog to add new inventory item"""
        dialog = tk.Toplevel(self)
        dialog.title("Add New Item")
        dialog.geometry("400x400")
        dialog.grab_set()

        # Form fields
        ttk.Label(dialog, text="Item Name:").pack(pady=5)
        name_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=name_var, width=40).pack(pady=5)

        ttk.Label(dialog, text="Description:").pack(pady=5)
        description_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=description_var, width=40).pack(pady=5)

        ttk.Label(dialog, text="Initial Quantity:").pack(pady=5)
        quantity_var = tk.StringVar(value="0")
        ttk.Entry(dialog, textvariable=quantity_var, width=40).pack(pady=5)

        ttk.Label(dialog, text="Unit Cost ($):").pack(pady=5)
        cost_var = tk.StringVar(value="0.00")
        ttk.Entry(dialog, textvariable=cost_var, width=40).pack(pady=5)

        ttk.Label(dialog, text="Reorder Level:").pack(pady=5)
        reorder_var = tk.StringVar(value="10")
        ttk.Entry(dialog, textvariable=reorder_var, width=40).pack(pady=5)

        def save_item():
            try:
                # Validate inputs
                name = name_var.get().strip()
                if not name:
                    raise ValueError("Item name is required")

                description = description_var.get().strip()

                try:
                    quantity = int(quantity_var.get())
                    if quantity < 0:
                        raise ValueError()
                except ValueError:
                    raise ValueError("Quantity must be a positive number")

                try:
                    unit_cost = float(cost_var.get())
                    if unit_cost < 0:
                        raise ValueError()
                except ValueError:
                    raise ValueError("Unit cost must be a positive number")

                try:
                    reorder_level = int(reorder_var.get())
                    if reorder_level < 0:
                        raise ValueError()
                except ValueError:
                    raise ValueError("Reorder level must be a positive number")

                # Create new item
                new_item = self.services['inventory'].add_inventory_item(
                    name=name,
                    description=description,
                    quantity=quantity,
                    unit_cost=unit_cost,
                    reorder_level=reorder_level,
                    audit_user_id=1  # TODO: Get actual user ID
                )

                messagebox.showinfo("Success", "Inventory item added successfully!")
                dialog.destroy()

                # Refresh inventory list
                self.load_data()

            except ValueError as e:
                messagebox.showerror("Error", str(e))
            except Exception as e:
                logger.error(f"Error adding inventory item: {str(e)}")
                messagebox.showerror("Error", "Failed to add inventory item")

                # Add save button
            ttk.Button(
                dialog,
                text="Save",
                command=save_item
            ).pack(pady=20)

            def show_edit_dialog(self):
                """Show dialog to edit selected inventory item"""
                if not self.selected_item:
                    return

                dialog = tk.Toplevel(self)
                dialog.title("Edit Item")
                dialog.geometry("400x400")
                dialog.grab_set()

                # Form fields
                ttk.Label(dialog, text="Item Name:").pack(pady=5)
                name_var = tk.StringVar(value=self.selected_item[1])
                ttk.Entry(dialog, textvariable=name_var, width=40).pack(pady=5)

                ttk.Label(dialog, text="Current Quantity:").pack(pady=5)
                ttk.Label(
                    dialog,
                    text=str(self.selected_item[2]),
                    font=("Helvetica", 12, "bold")
                ).pack(pady=5)

                ttk.Label(dialog, text="Unit Cost ($):").pack(pady=5)
                cost_var = tk.StringVar(
                    value=str(float(self.selected_item[3].replace('$', '')))
                )
                ttk.Entry(dialog, textvariable=cost_var, width=40).pack(pady=5)

                ttk.Label(dialog, text="Reorder Level:").pack(pady=5)
                reorder_var = tk.StringVar(value=str(self.selected_item[5]))
                ttk.Entry(dialog, textvariable=reorder_var, width=40).pack(pady=5)

                def save_changes():
                    try:
                        # Validate inputs
                        name = name_var.get().strip()
                        if not name:
                            raise ValueError("Item name is required")

                        try:
                            unit_cost = float(cost_var.get())
                            if unit_cost < 0:
                                raise ValueError()
                        except ValueError:
                            raise ValueError("Unit cost must be a positive number")

                        try:
                            reorder_level = int(reorder_var.get())
                            if reorder_level < 0:
                                raise ValueError()
                        except ValueError:
                            raise ValueError("Reorder level must be a positive number")

                        # Update item
                        update_data = {
                            'name': name,
                            'unit_cost': unit_cost,
                            'reorder_level': reorder_level
                        }

                        self.services['inventory'].update_item(
                            item_id=self.selected_item[0],
                            update_data=update_data,
                            audit_user_id=1  # TODO: Get actual user ID
                        )

                        messagebox.showinfo("Success", "Item updated successfully!")
                        dialog.destroy()

                        # Refresh inventory list
                        self.load_data()

                    except ValueError as e:
                        messagebox.showerror("Error", str(e))
                    except Exception as e:
                        logger.error(f"Error updating inventory item: {str(e)}")
                        messagebox.showerror("Error", "Failed to update inventory item")

                # Add save button
                ttk.Button(
                    dialog,
                    text="Save Changes",
                    command=save_changes
                ).pack(pady=20)

            def show_adjustment_dialog(self):
                """Show dialog to adjust inventory stock"""
                if not self.selected_item:
                    messagebox.showwarning("Warning", "Please select an item first")
                    return

                dialog = tk.Toplevel(self)
                dialog.title("Stock Adjustment")
                dialog.geometry("400x300")
                dialog.grab_set()

                # Item details
                ttk.Label(
                    dialog,
                    text=f"Item: {self.selected_item[1]}",
                    font=("Helvetica", 12, "bold")
                ).pack(pady=5)

                ttk.Label(
                    dialog,
                    text=f"Current Stock: {self.selected_item[2]}",
                    font=("Helvetica", 10)
                ).pack(pady=5)

                # Adjustment fields
                frame = ttk.Frame(dialog)
                frame.pack(pady=20)

                ttk.Label(frame, text="Adjustment Type:").grid(row=0, column=0, padx=5)
                type_var = tk.StringVar(value="add")
                ttk.Radiobutton(
                    frame,
                    text="Add Stock",
                    variable=type_var,
                    value="add"
                ).grid(row=0, column=1, padx=5)
                ttk.Radiobutton(
                    frame,
                    text="Remove Stock",
                    variable=type_var,
                    value="remove"
                ).grid(row=0, column=2, padx=5)

                ttk.Label(frame, text="Quantity:").grid(row=1, column=0, padx=5, pady=10)
                quantity_var = tk.StringVar(value="0")
                ttk.Entry(
                    frame,
                    textvariable=quantity_var,
                    width=10
                ).grid(row=1, column=1, columnspan=2, pady=10)

                ttk.Label(frame, text="Reason:").grid(row=2, column=0, padx=5)
                reason_var = tk.StringVar()
                ttk.Entry(
                    frame,
                    textvariable=reason_var,
                    width=40
                ).grid(row=2, column=1, columnspan=2, padx=5)

                def save_adjustment():
                    try:
                        # Validate inputs
                        try:
                            quantity = int(quantity_var.get())
                            if quantity <= 0:
                                raise ValueError()
                        except ValueError:
                            raise ValueError("Quantity must be a positive number")

                        reason = reason_var.get().strip()
                        if not reason:
                            raise ValueError("Please provide a reason for the adjustment")

                        # Calculate actual quantity change
                        quantity_change = quantity if type_var.get() == "add" else -quantity

                        # Update stock
                        self.services['inventory'].update_stock(
                            item_id=self.selected_item[0],
                            quantity_change=quantity_change,
                            transaction_type='adjustment',
                            user_id=1,  # TODO: Get actual user ID
                            notes=reason
                        )

                        messagebox.showinfo("Success", "Stock adjusted successfully!")
                        dialog.destroy()

                        # Refresh inventory list
                        self.load_data()

                    except ValueError as e:
                        messagebox.showerror("Error", str(e))
                    except Exception as e:
                        logger.error(f"Error adjusting stock: {str(e)}")
                        messagebox.showerror("Error", "Failed to adjust stock")

                # Add save button
                ttk.Button(
                    dialog,
                    text="Save Adjustment",
                    command=save_adjustment
                ).pack(pady=20)

            def show_item_history(self):
                """Show transaction history for selected item"""
                if not self.selected_item:
                    return

                # Switch to transactions tab and filter for selected item
                self.notebook.select(1)  # Switch to transactions tab
                self.load_transactions(item_id=self.selected_item[0])

            def load_transactions(self, item_id: Optional[int] = None):
                """Load transaction history"""
                try:
                    # Clear existing items
                    for item in self.transactions_tree.get_children():
                        self.transactions_tree.delete(item)

                    # Get transaction history
                    transactions = self.services['inventory'].get_transaction_history(
                        item_id=item_id,
                        start_date=self.start_date_var.get(),
                        end_date=self.end_date_var.get(),
                        transaction_type=self.trans_type_var.get() if self.trans_type_var.get() != "All" else None
                    )

                    # Add transactions to treeview
                    for trans in transactions:
                        self.transactions_tree.insert("", "end", values=(
                            trans['date'],
                            trans['item_name'],
                            trans['type'],
                            trans['quantity'],
                            trans['user'],
                            trans['notes']
                        ))

                except Exception as e:
                    logger.error(f"Error loading transactions: {str(e)}")
                    messagebox.showerror("Error", "Failed to load transaction history")

            def load_alerts(self):
                """Load inventory alerts"""
                try:
                    # Clear existing alerts
                    for item in self.alerts_tree.get_children():
                        self.alerts_tree.delete(item)

                    # Get inventory status
                    inventory = self.services['inventory'].get_inventory_status()

                    # Add low stock and out of stock items
                    for item in inventory['items']:
                        if item['quantity'] <= item['reorder_level']:
                            priority = "‼️" if item['quantity'] == 0 else "⚠️"
                            status = "Out of Stock" if item['quantity'] == 0 else "Low Stock"

                            self.alerts_tree.insert("", "end", values=(
                                priority,
                                item['name'],
                                item['quantity'],
                                item['reorder_level'],
                                status
                            ))

                except Exception as e:
                    logger.error(f"Error loading alerts: {str(e)}")
                    messagebox.showerror("Error", "Failed to load inventory alerts")

            def generate_reorder_report(self):
                """Generate and export reorder report"""
                try:
                    report_data = self.services['inventory'].generate_reorder_report()

                    # Save file
                    import tkinter.filedialog as filedialog
                    filename = filedialog.asksaveasfilename(
                        defaultextension=".pdf",
                        filetypes=[("PDF files", "*.pdf")],
                        initialfile=f"reorder_report_{datetime.now().strftime('%Y%m%d')}.pdf"
                    )

                    if filename:
                        with open(filename, 'wb') as f:
                            f.write(report_data)
                        messagebox.showinfo("Success", "Reorder report generated successfully!")

                except Exception as e:
                    logger.error(f"Error generating reorder report: {str(e)}")
                    messagebox.showerror("Error", "Failed to generate reorder report")

            def export_inventory(self):
                """Export current inventory list"""
                try:
                    # Get current filters
                    search_term = self.search_var.get()
                    status_filter = self.status_var.get()

                    # Generate report
                    report_data = self.services['inventory'].export_inventory(
                        search_term=search_term if search_term else None,
                        status_filter=status_filter if status_filter != "All" else None,
                        format='csv'
                    )

                    # Save file
                    import tkinter.filedialog as filedialog
                    filename = filedialog.asksaveasfilename(
                        defaultextension=".csv",
                        filetypes=[("CSV files", "*.csv")],
                        initialfile=f"inventory_{datetime.now().strftime('%Y%m%d')}.csv"
                    )

                    if filename:
                        with open(filename, 'wb') as f:
                            f.write(report_data)
                        messagebox.showinfo("Success", "Inventory exported successfully!")

                except Exception as e:
                    logger.error(f"Error exporting inventory: {str(e)}")
                    messagebox.showerror("Error", "Failed to export inventory")

            def export_transactions(self):
                """Export transaction history"""
                try:
                    # Generate report
                    report_data = self.services['inventory'].export_transactions(
                        start_date=self.start_date_var.get(),
                        end_date=self.end_date_var.get(),
                        transaction_type=self.trans_type_var.get() if self.trans_type_var.get() != "All" else None,
                        format='csv'
                    )

                    # Save file
                    import tkinter.filedialog as filedialog
                    filename = filedialog.asksaveasfilename(
                        defaultextension=".csv",
                        filetypes=[("CSV files", "*.csv")],
                        initialfile=f"transactions_{datetime.now().strftime('%Y%m%d')}.csv"
                    )

                    if filename:
                        with open(filename, 'wb') as f:
                            f.write(report_data)
                        messagebox.showinfo("Success", "Transactions exported successfully!")

                except Exception as e:
                    logger.error(f"Error exporting transactions: {str(e)}")
                    messagebox.showerror("Error", "Failed to export transactions")