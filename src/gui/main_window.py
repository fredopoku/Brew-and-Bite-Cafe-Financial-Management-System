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
        self.root.resizable(True, True)
        self.root.minsize(900, 620)
        self.root.configure(bg=CREAM)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        # Start maximised — fills screen but keeps macOS menu bar / Dock
        self.root.update_idletasks()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"{sw}x{sh}+0+0")

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
        self.sidebar = tk.Frame(self.root, bg=ESPRESSO, width=230)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        # --- Brand area ---
        brand = tk.Frame(self.sidebar, bg=DARK_BROWN)
        brand.pack(fill="x")
        inner_brand = tk.Frame(brand, bg=DARK_BROWN, pady=18, padx=18)
        inner_brand.pack(fill="x")
        top_row = tk.Frame(inner_brand, bg=DARK_BROWN)
        top_row.pack(fill="x")
        icon_box = tk.Frame(top_row, bg=ESPRESSO, width=44, height=44)
        icon_box.pack(side="left")
        icon_box.pack_propagate(False)
        tk.Label(icon_box, text="☕", font=("Helvetica", 22),
                 bg=ESPRESSO, fg=CARD_BG).place(relx=0.5, rely=0.5, anchor="center")
        name_col = tk.Frame(top_row, bg=DARK_BROWN)
        name_col.pack(side="left", padx=(10, 0))
        tk.Label(name_col, text="Brew & Bite",
                 font=("Helvetica", 14, "bold"),
                 bg=DARK_BROWN, fg=CARD_BG).pack(anchor="w")
        tk.Label(name_col, text="Café Management",
                 font=("Helvetica", 8),
                 bg=DARK_BROWN, fg=LIGHT_BROWN).pack(anchor="w")

        # --- Nav section label ---
        tk.Frame(self.sidebar, bg=DARK_BROWN, height=1).pack(fill="x")
        tk.Label(self.sidebar, text="  MAIN MENU",
                 font=("Helvetica", 8, "bold"),
                 bg=ESPRESSO, fg=SIDEBAR_MUTED).pack(anchor="w", padx=14, pady=(14, 4))

        # --- Nav items with left-border indicator ---
        self._nav_buttons = {}
        self._nav_rows    = {}
        nav_items = [
            ("dashboard", "🏠", "Dashboard",      self.load_dashboard),
            ("sales",     "🛍", "Sales",           self.load_sales),
            ("inventory", "📦", "Inventory",       self.load_inventory),
            ("expenses",  "💳", "Expenses",        self.load_expenses),
            ("reports",   "📊", "Reports",         self.load_reports),
        ]
        if self.user_data['role'] == UserRole.ADMIN.value:
            nav_items.append(("users", "👥", "User Management", self.load_user_management))

        for key, icon, label, cmd in nav_items:
            row = tk.Frame(self.sidebar, bg=ESPRESSO, cursor="hand2")
            row.pack(fill="x", pady=1)

            indicator = tk.Frame(row, bg=ESPRESSO, width=4)
            indicator.pack(side="left", fill="y")

            content = tk.Frame(row, bg=ESPRESSO, pady=10)
            content.pack(side="left", fill="x", expand=True, padx=(8, 12))

            tk.Label(content, text=f"{icon}  {label}",
                     font=FONT_BODY, anchor="w",
                     bg=ESPRESSO, fg=SIDEBAR_TEXT).pack(fill="x")

            self._nav_buttons[key] = (row, indicator, content)

            for widget in (row, content) + tuple(content.winfo_children()):
                widget.bind("<Button-1>", lambda e, k=key, c=cmd: self._nav_click(k, c))
                widget.bind("<Enter>",    lambda e, k=key: self._nav_hover(k, True))
                widget.bind("<Leave>",    lambda e, k=key: self._nav_hover(k, False))

        # --- Bottom: divider + user card + logout ---
        tk.Frame(self.sidebar, bg=DARK_BROWN, height=1).pack(
            fill="x", padx=14, pady=(14, 0), side="bottom")

        bottom = tk.Frame(self.sidebar, bg=ESPRESSO, pady=14, padx=14)
        bottom.pack(side="bottom", fill="x")

        role_colour = LIGHT_BROWN if self.user_data['role'] == UserRole.ADMIN.value else "#7DB0A0"
        initials = self.user_data['username'][:2].upper()
        avatar = tk.Frame(bottom, bg=MEDIUM_BROWN, width=36, height=36)
        avatar.pack(side="left")
        avatar.pack_propagate(False)
        tk.Label(avatar, text=initials, font=("Helvetica", 12, "bold"),
                 bg=MEDIUM_BROWN, fg=CARD_BG).place(relx=0.5, rely=0.5, anchor="center")

        info = tk.Frame(bottom, bg=ESPRESSO)
        info.pack(side="left", padx=(10, 0))
        tk.Label(info, text=self.user_data['username'],
                 font=("Helvetica", 10, "bold"),
                 bg=ESPRESSO, fg=CARD_BG).pack(anchor="w")
        tk.Label(info, text=self.user_data['role'],
                 font=("Helvetica", 8),
                 bg=ESPRESSO, fg=role_colour).pack(anchor="w")

        logout_btn = tk.Label(bottom, text="⏻", font=("Helvetica", 16),
                              bg=ESPRESSO, fg=SIDEBAR_MUTED, cursor="hand2")
        logout_btn.pack(side="right")
        logout_btn.bind("<Button-1>", lambda _: self.logout())
        logout_btn.bind("<Enter>", lambda _: logout_btn.configure(fg=DANGER))
        logout_btn.bind("<Leave>", lambda _: logout_btn.configure(fg=SIDEBAR_MUTED))

    def _nav_click(self, key: str, command):
        for k, (row, ind, cont) in self._nav_buttons.items():
            is_active = (k == key)
            bg = DARK_BROWN if is_active else ESPRESSO
            ind.configure(bg=MEDIUM_BROWN if is_active else ESPRESSO)
            row.configure(bg=bg)
            cont.configure(bg=bg)
            for child in cont.winfo_children():
                child.configure(bg=bg,
                                fg=CARD_BG if is_active else SIDEBAR_TEXT,
                                font=("Helvetica", 11, "bold") if is_active else FONT_BODY)
        self._active_nav = key
        command()

    def _nav_hover(self, key: str, entering: bool):
        if key == self._active_nav:
            return
        row, ind, cont = self._nav_buttons[key]
        bg = DARK_BROWN if entering else ESPRESSO
        row.configure(bg=bg); cont.configure(bg=bg)
        for child in cont.winfo_children():
            child.configure(bg=bg)

    def create_main_content(self):
        self.main_content = tk.Frame(self.root, bg=CREAM)
        self.main_content.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        self.main_content.grid_rowconfigure(0, weight=1)
        self.main_content.grid_columnconfigure(0, weight=1)

    def create_status_bar(self):
        bar = tk.Frame(self.root, bg=ESPRESSO, height=28)
        bar.grid(row=1, column=0, columnspan=2, sticky="ew")
        bar.grid_propagate(False)

        tk.Label(bar, text="  ☕  Brew & Bite Café  ·  Management System  v1.0",
                 font=("Helvetica", 9), bg=ESPRESSO, fg=SIDEBAR_MUTED).pack(side="left")

        self.time_label = tk.Label(bar, font=("Helvetica", 9),
                                   bg=ESPRESSO, fg=SIDEBAR_MUTED)
        self.time_label.pack(side="right", padx=12)
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
        outer.pack(fill="both", expand=True, padx=28, pady=20)

        # ---- Page header ----
        ph = tk.Frame(outer, bg=CREAM)
        ph.pack(fill="x", pady=(0, 16))

        left_hdr = tk.Frame(ph, bg=CREAM)
        left_hdr.pack(side="left")
        tk.Label(left_hdr, text="Dashboard",
                 font=("Helvetica", 22, "bold"), bg=CREAM, fg=ESPRESSO).pack(anchor="w")
        tk.Label(left_hdr, text=today.strftime("%A, %d %B %Y"),
                 font=FONT_SMALL, bg=CREAM, fg=TEXT_MID).pack(anchor="w", pady=(2, 0))

        btn_frame = tk.Frame(ph, bg=CREAM)
        btn_frame.pack(side="right")
        new_sale = tk.Button(btn_frame, text="  + New Sale  ",
                             font=("Helvetica", 10, "bold"),
                             bg=MEDIUM_BROWN, fg=CARD_BG,
                             activebackground=DARK_BROWN, activeforeground=CARD_BG,
                             relief="flat", bd=0, cursor="hand2",
                             command=self.load_sales)
        new_sale.pack(side="right", ipady=7, ipadx=2)
        new_expense = tk.Button(btn_frame, text="  + Expense  ",
                                font=("Helvetica", 10),
                                bg=CARD_BG, fg=MEDIUM_BROWN,
                                activebackground=BORDER, activeforeground=ESPRESSO,
                                relief="flat", bd=0, cursor="hand2",
                                highlightbackground=BORDER, highlightthickness=1,
                                command=self.load_expenses)
        new_expense.pack(side="right", ipady=7, ipadx=2, padx=(0, 8))

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

        ch_hdr = tk.Frame(chart_card, bg=CARD_BG)
        ch_hdr.pack(fill="x", padx=16, pady=(14, 4))
        tk.Label(ch_hdr, text="📈  Sales — Last 7 Days",
                 font=("Helvetica", 11, "bold"), bg=CARD_BG, fg=ESPRESSO).pack(side="left")
        tk.Label(ch_hdr, text=f"{week_start}  →  {today_str}",
                 font=("Helvetica", 8), bg=CARD_BG, fg=TEXT_MID).pack(side="right")
        tk.Frame(chart_card, bg=BORDER, height=1).pack(fill="x", padx=16)

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

        act_hdr = tk.Frame(act_card, bg=CARD_BG)
        act_hdr.pack(fill="x", padx=16, pady=(14, 4))
        tk.Label(act_hdr, text="🕐  Recent Activity",
                 font=("Helvetica", 11, "bold"), bg=CARD_BG, fg=ESPRESSO).pack(side="left")
        tk.Frame(act_card, bg=BORDER, height=1).pack(fill="x", padx=16)

        act_scroll = tk.Frame(act_card, bg=CARD_BG)
        act_scroll.pack(fill="both", expand=True, padx=12, pady=(6, 10))

        try:
            activities = self.services['reporting'].get_recent_activities()
            if not activities:
                tk.Label(act_scroll, text="No activity recorded yet.",
                         bg=CARD_BG, fg=TEXT_MID,
                         font=FONT_SMALL).pack(pady=30)
            else:
                for i, act in enumerate(activities[:14]):
                    row_bg = "#F9F5F0" if i % 2 == 0 else CARD_BG
                    row = tk.Frame(act_scroll, bg=row_bg, pady=5, padx=6)
                    row.pack(fill="x")

                    tk.Label(row, text=act['timestamp'].strftime("%H:%M"),
                             font=("Courier", 8), bg=row_bg, fg=TEXT_MID,
                             width=5, anchor="w").pack(side="left")

                    badge_bg = MEDIUM_BROWN if act['type'] == 'SALE' else "#C87030"
                    badge = tk.Label(row, text=f" {act['type'][:4]} ",
                                     font=("Helvetica", 8, "bold"),
                                     bg=badge_bg, fg=CARD_BG)
                    badge.pack(side="left", padx=(4, 6))

                    tk.Label(row, text=act['details'][:22],
                             font=("Helvetica", 9), bg=row_bg,
                             fg=TEXT_DARK, anchor="w").pack(side="left", fill="x", expand=True)

                    amt_color = SUCCESS if act['type'] == 'SALE' else DANGER
                    tk.Label(row, text=f"${act['amount']:,.2f}",
                             font=("Helvetica", 9, "bold"), bg=row_bg,
                             fg=amt_color, anchor="e").pack(side="right")
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
        card.grid(row=0, column=col, padx=5, pady=4, sticky="nsew")

        body = tk.Frame(card, bg=CARD_BG)
        body.pack(fill="both", expand=True)

        # Left colour accent bar
        tk.Frame(body, bg=colour, width=5).pack(side="left", fill="y")

        content = tk.Frame(body, bg=CARD_BG, padx=14, pady=14)
        content.pack(side="left", fill="both", expand=True)

        top_row = tk.Frame(content, bg=CARD_BG)
        top_row.pack(fill="x")
        tk.Label(top_row, text=title, font=("Helvetica", 9),
                 bg=CARD_BG, fg=TEXT_MID).pack(side="left")
        tk.Label(top_row, text=icon, font=("Helvetica", 18),
                 bg=CARD_BG).pack(side="right")

        tk.Label(content, text=value,
                 font=("Helvetica", 24, "bold"),
                 bg=CARD_BG, fg=colour).pack(anchor="w", pady=(6, 2))
        tk.Label(content, text=subtitle,
                 font=("Helvetica", 9),
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
