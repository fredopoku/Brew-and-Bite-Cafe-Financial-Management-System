from typing import Dict, Optional
import tkinter as tk
from tkinter import ttk, messagebox
import logging
from datetime import datetime, timedelta

from src.gui.dialogs import ChangePasswordDialog, UserManualDialog
from src.gui.sales_screen import SalesScreen
from src.gui.inventory_screen import InventoryScreen
from src.gui.expense_screen import ExpenseScreen
from src.gui.reports_screen import ReportsScreen
from src.gui.user_management_screen import UserManagementScreen
from src.gui.styles import (apply_theme, ESPRESSO, DARK_BROWN, MEDIUM_BROWN,
                             LIGHT_BROWN, CREAM, CARD_BG, BORDER, SIDEBAR_TEXT,
                             SIDEBAR_MUTED, TEXT_DARK, TEXT_MID, TEXT_LIGHT,
                             SUCCESS, WARNING, DANGER, ROW_DANGER_BG, ROW_WARNING_BG,
                             FONT_H1, FONT_H2, FONT_H3, FONT_BODY, FONT_SMALL)
from src.database.models import UserRole
from src.bll.service_provider import ServiceProvider
from src.bll.user_service import UserService
from src.bll.sales_service import SalesService
from src.bll.expense_service import ExpenseService
from src.bll.inventory_service import InventoryService
from src.bll.reporting_service import ReportingService

logger = logging.getLogger(__name__)


class MainWindow:
    def __init__(self, user_data: Dict):
        self.user_data = user_data
        self.last_activity = datetime.now()
        self._active_nav = None

        self.root = tk.Tk()
        self.style = apply_theme(self.root)
        self.setup_window()

        self.service_provider = ServiceProvider.get_instance()
        self.auth_service = self.service_provider.get_service('auth')

        self.create_services()
        self.create_widgets()
        self.setup_activity_tracking()
        self.load_dashboard()

    # ------------------------------------------------------------------
    # Window setup
    # ------------------------------------------------------------------
    def setup_window(self):
        self.root.title("Brew and Bite Café — Management System")
        self.root.geometry("1200x780")
        self.root.minsize(900, 620)
        self.root.configure(bg=CREAM)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

    def create_services(self):
        try:
            session = self.auth_service.session
            self.services = {
                'auth':      self.auth_service,
                'user':      UserService(session),
                'sales':     SalesService(session),
                'expense':   ExpenseService(session),
                'inventory': InventoryService(session),
                'reporting': ReportingService(session),
            }
        except Exception as e:
            logger.error(f"Error creating services: {e}")
            messagebox.showerror("Error", "Failed to initialise services")
            self.root.destroy()

    # ------------------------------------------------------------------
    # Widget construction
    # ------------------------------------------------------------------
    def create_widgets(self):
        self.create_menu()
        self.create_sidebar()
        self.create_main_content()
        self.create_status_bar()

    def create_menu(self):
        menubar = tk.Menu(self.root, bg=DARK_BROWN, fg=SIDEBAR_TEXT,
                          activebackground=MEDIUM_BROWN, activeforeground=CARD_BG,
                          relief="flat", bd=0)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0, bg=CARD_BG, fg=TEXT_DARK,
                            activebackground=MEDIUM_BROWN, activeforeground=CARD_BG)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Change Password", command=self.show_change_password)
        file_menu.add_separator()
        file_menu.add_command(label="Logout",  command=self.logout)
        file_menu.add_command(label="Exit",    command=self.quit_app)

        help_menu = tk.Menu(menubar, tearoff=0, bg=CARD_BG, fg=TEXT_DARK,
                            activebackground=MEDIUM_BROWN, activeforeground=CARD_BG)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="User Manual", command=self.show_manual)
        help_menu.add_command(label="About",       command=self.show_about)

    def create_sidebar(self):
        self.sidebar = tk.Frame(self.root, bg=ESPRESSO, width=220)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        # --- Logo / branding area ---
        brand_frame = tk.Frame(self.sidebar, bg=DARK_BROWN, pady=20)
        brand_frame.pack(fill="x")

        tk.Label(brand_frame, text="☕", font=("Helvetica", 28),
                 bg=DARK_BROWN, fg=CARD_BG).pack()
        tk.Label(brand_frame, text="Brew & Bite",
                 font=("Helvetica", 16, "bold"),
                 bg=DARK_BROWN, fg=CARD_BG).pack()
        tk.Label(brand_frame, text="Café Management",
                 font=("Helvetica", 9),
                 bg=DARK_BROWN, fg=LIGHT_BROWN).pack()

        # --- User card ---
        user_frame = tk.Frame(self.sidebar, bg=ESPRESSO, pady=12)
        user_frame.pack(fill="x", padx=14)

        tk.Label(user_frame, text=self.user_data['username'].upper(),
                 font=("Helvetica", 11, "bold"),
                 bg=ESPRESSO, fg=CARD_BG).pack(anchor="w")
        role_colour = LIGHT_BROWN if self.user_data['role'] == UserRole.ADMIN.value else "#7DB0A0"
        tk.Label(user_frame, text=f"  {self.user_data['role']}",
                 font=("Helvetica", 9), bg=ESPRESSO, fg=role_colour).pack(anchor="w")

        # divider
        tk.Frame(self.sidebar, bg=DARK_BROWN, height=1).pack(fill="x", padx=10, pady=6)

        # --- Nav label ---  use SIDEBAR_MUTED (5.5:1 on ESPRESSO) not TEXT_LIGHT
        tk.Label(self.sidebar, text="NAVIGATION",
                 font=("Helvetica", 8, "bold"),
                 bg=ESPRESSO, fg=SIDEBAR_MUTED).pack(anchor="w", padx=18, pady=(6, 2))

        # --- Nav labels (tk.Label instead of tk.Button — macOS ignores Button bg/fg) ---
        self._nav_buttons = {}
        nav_items = [
            ("dashboard", "  Dashboard",   self.load_dashboard),
            ("sales",     "  Sales",       self.load_sales),
            ("inventory", "  Inventory",   self.load_inventory),
            ("expenses",  "  Expenses",    self.load_expenses),
            ("reports",   "  Reports",     self.load_reports),
        ]
        if self.user_data['role'] == UserRole.ADMIN.value:
            nav_items.append(("users", "  User Management", self.load_user_management))

        for key, label, cmd in nav_items:
            lbl = tk.Label(
                self.sidebar, text=label,
                font=FONT_BODY, anchor="w",
                bg=ESPRESSO, fg=SIDEBAR_TEXT,
                cursor="hand2", pady=10, padx=8
            )
            lbl.pack(fill="x", padx=8, pady=1)
            lbl.bind("<Button-1>", lambda e, k=key, c=cmd: self._nav_click(k, c))
            lbl.bind("<Enter>",    lambda e, l=lbl, k=key: self._nav_hover(l, k, True))
            lbl.bind("<Leave>",    lambda e, l=lbl, k=key: self._nav_hover(l, k, False))
            self._nav_buttons[key] = lbl

        # --- Bottom: logout ---
        tk.Frame(self.sidebar, bg=DARK_BROWN, height=1).pack(fill="x", padx=10, pady=10)
        logout_lbl = tk.Label(
            self.sidebar, text="  Logout",
            font=FONT_SMALL, anchor="w",
            bg=ESPRESSO, fg=SIDEBAR_TEXT,
            cursor="hand2", pady=8, padx=8
        )
        logout_lbl.pack(fill="x", padx=8, pady=1)
        logout_lbl.bind("<Button-1>", lambda e: self.logout())
        logout_lbl.bind("<Enter>", lambda e: logout_lbl.configure(bg=DANGER, fg=CARD_BG))
        logout_lbl.bind("<Leave>", lambda e: logout_lbl.configure(bg=ESPRESSO, fg=SIDEBAR_TEXT))

    def _nav_click(self, key: str, command):
        for k, lbl in self._nav_buttons.items():
            lbl.configure(bg=ESPRESSO, fg=SIDEBAR_TEXT, font=FONT_BODY)
        if key in self._nav_buttons:
            self._nav_buttons[key].configure(
                bg=MEDIUM_BROWN, fg=CARD_BG, font=("Helvetica", 11, "bold")
            )
        self._active_nav = key
        command()

    def _nav_hover(self, label: tk.Label, key: str, entering: bool):
        if key == self._active_nav:
            return
        label.configure(bg=DARK_BROWN if entering else ESPRESSO,
                        fg=CARD_BG if entering else SIDEBAR_TEXT)

    def create_main_content(self):
        self.main_content = tk.Frame(self.root, bg=CREAM)
        self.main_content.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        self.main_content.grid_rowconfigure(0, weight=1)
        self.main_content.grid_columnconfigure(0, weight=1)

    def create_status_bar(self):
        bar = tk.Frame(self.root, bg=DARK_BROWN, height=26)
        bar.grid(row=1, column=0, columnspan=2, sticky="ew")
        bar.grid_propagate(False)

        tk.Label(bar, text="  Brew & Bite Café Management System  v1.0",
                 font=("Helvetica", 9), bg=DARK_BROWN, fg=LIGHT_BROWN).pack(side="left")

        self.time_label = tk.Label(bar, font=("Helvetica", 9),
                                   bg=DARK_BROWN, fg=LIGHT_BROWN)
        self.time_label.pack(side="right", padx=10)
        self.update_time()

    # ------------------------------------------------------------------
    # Dashboard
    # ------------------------------------------------------------------
    def load_dashboard(self):
        self._clear_main_content()
        self._nav_click("dashboard", lambda: None)

        today     = datetime.now()
        today_str = today.strftime('%Y-%m-%d')
        week_start = (today - timedelta(days=6)).strftime('%Y-%m-%d')

        # Load each data source independently so one failure doesn't block others
        sales_summary    = self._safe_service_call(
            lambda: self.services['sales'].get_daily_sales_summary(today_str),
            {'summary': {'total_sales': 0.0, 'transaction_count': 0, 'average_sale': 0.0},
             'top_items': []}
        )
        expense_summary  = self._safe_service_call(
            lambda: self.services['expense'].get_expense_summary(today_str, today_str),
            {'summary': {'total_amount': 0.0, 'total_transactions': 0}}
        )
        inventory_status = self._safe_service_call(
            lambda: self.services['inventory'].get_inventory_status(),
            {'items': [], 'total_items': 0, 'total_value': 0.0, 'alerts': []}
        )

        outer = tk.Frame(self.main_content, bg=CREAM)
        outer.pack(fill="both", expand=True, padx=24, pady=18)

        # ---- Page header ----
        ph = tk.Frame(outer, bg=CREAM)
        ph.pack(fill="x", pady=(0, 14))
        tk.Label(ph, text="Dashboard",
                 font=FONT_H1, bg=CREAM, fg=ESPRESSO).pack(side="left")
        tk.Label(ph, text=today.strftime("  %A, %d %B %Y"),
                 font=FONT_SMALL, bg=CREAM, fg=TEXT_MID).pack(side="left", pady=(6, 0))

        ttk.Button(ph, text="+ New Sale",
                   style="Primary.TButton",
                   command=self.load_sales).pack(side="right", padx=(6, 0))
        ttk.Button(ph, text="+ Expense",
                   style="Secondary.TButton",
                   command=self.load_expenses).pack(side="right")

        # ---- KPI cards ----
        cards_row = tk.Frame(outer, bg=CREAM)
        cards_row.pack(fill="x", pady=(0, 14))
        for _i in range(4):
            cards_row.grid_columnconfigure(_i, weight=1)

        net = (sales_summary['summary']['total_sales']
               - expense_summary['summary']['total_amount'])
        low_stock = len([i for i in inventory_status['items']
                         if i['quantity'] <= i['reorder_level']])

        card_data = [
            ("Today's Revenue",
             f"${sales_summary['summary']['total_sales']:,.2f}",
             f"{sales_summary['summary']['transaction_count']} transactions",
             MEDIUM_BROWN, "💰"),
            ("Today's Expenses",
             f"${expense_summary['summary']['total_amount']:,.2f}",
             f"{expense_summary['summary']['total_transactions']} recorded",
             WARNING, "📋"),
            ("Net Income",
             f"${net:,.2f}",
             "Revenue − Expenses",
             SUCCESS if net >= 0 else DANGER,
             "📈" if net >= 0 else "📉"),
            ("Inventory Alerts",
             str(low_stock),
             f"of {inventory_status['total_items']} items at reorder level",
             DANGER if low_stock > 0 else SUCCESS,
             "⚠️" if low_stock > 0 else "✅"),
        ]
        for col, (title, value, sub, colour, icon) in enumerate(card_data):
            self._make_stat_card(cards_row, title, value, sub, colour, icon, col)

        # ---- Lower section: chart (left) + activity feed (right) ----
        lower = tk.Frame(outer, bg=CREAM)
        lower.pack(fill="both", expand=True)
        lower.grid_columnconfigure(0, weight=6)
        lower.grid_columnconfigure(1, weight=4)
        lower.grid_rowconfigure(0, weight=1)

        # -- Weekly sales chart --
        chart_card = tk.Frame(lower, bg=CARD_BG,
                              highlightbackground=BORDER, highlightthickness=1)
        chart_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        ch_hdr = tk.Frame(chart_card, bg=CREAM)
        ch_hdr.pack(fill="x", padx=14, pady=(10, 4))
        tk.Label(ch_hdr, text="Sales — Last 7 Days",
                 font=FONT_H3, bg=CREAM, fg=ESPRESSO).pack(side="left")

        from src.gui.charts import BarChart
        chart = BarChart(chart_card, bar_color=MEDIUM_BROWN)
        chart.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        try:
            report = self.services['reporting'].generate_periodic_report(
                start_date=week_start, end_date=today_str, group_by='day'
            )
            chart_data = []
            for d in report['sales_analysis']['over_time']:
                raw_date = str(d['date'])
                label    = raw_date[5:] if len(raw_date) >= 7 else raw_date
                chart_data.append((label, float(d['total_amount'])))
            chart.set_data(chart_data)
        except Exception as e:
            logger.warning(f"Chart data error: {e}")
            chart.set_data([])

        # -- Recent activity feed --
        act_card = tk.Frame(lower, bg=CARD_BG,
                            highlightbackground=BORDER, highlightthickness=1)
        act_card.grid(row=0, column=1, sticky="nsew")

        act_hdr = tk.Frame(act_card, bg=CREAM)
        act_hdr.pack(fill="x", padx=14, pady=(10, 6))
        tk.Label(act_hdr, text="Recent Activity",
                 font=FONT_H3, bg=CREAM, fg=ESPRESSO).pack(side="left")

        act_scroll = tk.Frame(act_card, bg=CARD_BG)
        act_scroll.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        try:
            activities = self.services['reporting'].get_recent_activities()
            if not activities:
                tk.Label(act_scroll, text="No activity recorded yet.",
                         bg=CARD_BG, fg=TEXT_MID,
                         font=FONT_SMALL).pack(pady=20)
            else:
                for act in activities[:14]:
                    row_bg = CARD_BG
                    row = tk.Frame(act_scroll, bg=row_bg,
                                   highlightbackground=BORDER, highlightthickness=0)
                    row.pack(fill="x", pady=1)

                    tk.Label(row, text=act['timestamp'].strftime("%H:%M"),
                             font=("Courier", 9), bg=row_bg, fg=TEXT_MID,
                             width=6, anchor="w").pack(side="left")

                    type_color = MEDIUM_BROWN if act['type'] == 'SALE' else WARNING
                    tk.Label(row, text=act['type'],
                             font=("Helvetica", 9, "bold"), bg=row_bg,
                             fg=type_color, width=9, anchor="w").pack(side="left")

                    amt_color = SUCCESS if act['type'] == 'SALE' else DANGER
                    tk.Label(row,
                             text=f"${act['amount']:,.2f}",
                             font=("Helvetica", 9), bg=row_bg,
                             fg=amt_color, anchor="e", width=10).pack(side="right")

                    tk.Label(row,
                             text=act['details'][:28],
                             font=("Helvetica", 9), bg=row_bg,
                             fg=TEXT_DARK, anchor="w").pack(side="left", fill="x")
        except Exception as e:
            logger.warning(f"Activity feed error: {e}")
            tk.Label(act_scroll, text="Could not load activity.",
                     bg=CARD_BG, fg=TEXT_MID, font=FONT_SMALL).pack(pady=20)

    def _safe_service_call(self, fn, default):
        """Call a service function; on failure rollback session and return default."""
        try:
            return fn()
        except Exception as e:
            logger.error(f"Service call failed: {e}")
            try:
                # Recover the shared session so subsequent calls can still work
                self.services['sales'].session.rollback()
            except Exception:
                pass
            return default

    def _show_error_placeholder(self, message: str):
        """Show a styled error message in the main content area."""
        f = tk.Frame(self.main_content, bg=CREAM)
        f.pack(fill="both", expand=True)
        tk.Label(f, text="⚠", font=("Helvetica", 40),
                 bg=CREAM, fg=DANGER).pack(pady=(60, 8))
        tk.Label(f, text=message, font=FONT_BODY,
                 bg=CREAM, fg=TEXT_MID, justify="center").pack()

    def _make_stat_card(self, parent, title, value, subtitle, colour, icon, col):
        card = tk.Frame(parent, bg=CARD_BG,
                        highlightbackground=BORDER, highlightthickness=1)
        card.grid(row=0, column=col, padx=6, pady=4, sticky="nsew")

        # Colour accent bar at top
        tk.Frame(card, bg=colour, height=4).pack(fill="x")

        inner = tk.Frame(card, bg=CARD_BG, padx=14, pady=12)
        inner.pack(fill="both", expand=True)

        top = tk.Frame(inner, bg=CARD_BG)
        top.pack(fill="x")
        # Use TEXT_MID (6.5:1 on white) instead of TEXT_LIGHT (2.7:1) for legibility
        tk.Label(top, text=title, font=FONT_SMALL,
                 bg=CARD_BG, fg=TEXT_MID).pack(side="left")
        tk.Label(top, text=icon, font=("Helvetica", 16),
                 bg=CARD_BG).pack(side="right")

        tk.Label(inner, text=value, font=("Helvetica", 22, "bold"),
                 bg=CARD_BG, fg=colour).pack(anchor="w", pady=(4, 0))
        tk.Label(inner, text=subtitle, font=FONT_SMALL,
                 bg=CARD_BG, fg=TEXT_MID).pack(anchor="w")

    # ------------------------------------------------------------------
    # Navigation helpers
    # ------------------------------------------------------------------
    def _clear_main_content(self):
        for w in self.main_content.winfo_children():
            w.destroy()

    def load_sales(self):
        self._clear_main_content()
        SalesScreen(self.main_content, self.services).pack(fill="both", expand=True)

    def load_inventory(self):
        self._clear_main_content()
        InventoryScreen(self.main_content, self.services).pack(fill="both", expand=True)

    def load_expenses(self):
        self._clear_main_content()
        ExpenseScreen(self.main_content, self.services).pack(fill="both", expand=True)

    def load_reports(self):
        self._clear_main_content()
        ReportsScreen(self.main_content, self.services).pack(fill="both", expand=True)

    def load_user_management(self):
        self._clear_main_content()
        UserManagementScreen(
            self.main_content, self.services, self.user_data
        ).pack(fill="both", expand=True)

    # ------------------------------------------------------------------
    # Activity tracking / auto-logout
    # ------------------------------------------------------------------
    def setup_activity_tracking(self):
        self.last_activity = datetime.now()
        self.root.bind_all("<Key>",        self.reset_activity_timer)
        self.root.bind_all("<Button>",     self.reset_activity_timer)
        self.root.bind_all("<MouseWheel>", self.reset_activity_timer)
        self.check_activity()

    def reset_activity_timer(self, event=None):
        self.last_activity = datetime.now()

    def check_activity(self):
        if (datetime.now() - self.last_activity).seconds > 1800:
            self.logout()
        else:
            self.root.after(60000, self.check_activity)

    def update_time(self):
        self.time_label.config(
            text=datetime.now().strftime("  %Y-%m-%d  %H:%M:%S  "))
        self.root.after(1000, self.update_time)

    # ------------------------------------------------------------------
    # Dialogs / actions
    # ------------------------------------------------------------------
    def show_change_password(self):
        ChangePasswordDialog(self.root, self.services['auth'], self.user_data['id'])

    def show_manual(self):
        UserManualDialog(self.root)

    def show_about(self):
        messagebox.showinfo(
            "About Brew & Bite",
            "Brew and Bite Café Management System\n"
            "Version 1.0.0\n\n"
            "Developed for Brew & Bite Café\n"
            "© 2024  All rights reserved"
        )

    def logout(self):
        try:
            self.auth_service.logout(self.user_data['id'])
        except Exception:
            pass
        self.root.destroy()
        from src.gui.login_window import LoginWindow
        LoginWindow().run()

    def quit_app(self):
        if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
            try:
                self.auth_service.logout(self.user_data['id'])
            except Exception:
                pass
            self.root.quit()

    def run(self):
        self.root.mainloop()
