"""Login window — split-panel café-themed design."""
import tkinter as tk
from tkinter import messagebox
import logging
from src.database.database import get_session
from src.bll import create_auth_service
from src.gui.main_window import MainWindow

try:
    from src.gui.styles import (
        ESPRESSO, DARK_BROWN, MEDIUM_BROWN, LIGHT_BROWN,
        CREAM, CARD_BG, BORDER, TEXT_DARK, TEXT_MID,
        FONT_H2, FONT_BODY, FONT_SMALL,
    )
except ImportError:
    ESPRESSO = "#2C1A0E"; DARK_BROWN = "#4A2C17"; MEDIUM_BROWN = "#8B5E3C"
    LIGHT_BROWN = "#C49A6C"; CREAM = "#F5EFE7"; CARD_BG = "#FFFFFF"
    BORDER = "#C8A882"; TEXT_DARK = "#2D1B0E"; TEXT_MID = "#5C3B24"
    FONT_H2 = ("Helvetica", 15, "bold")
    FONT_BODY = ("Helvetica", 11); FONT_SMALL = ("Helvetica", 10)

logger = logging.getLogger(__name__)


class LoginWindow:
    _W, _H, _LEFT_W = 860, 560, 340

    def __init__(self):
        self.root = tk.Tk()
        self._pw_visible = False
        self._setup_window()
        self._build_left()
        self._build_right()
        self.session = get_session()
        self.auth_service = create_auth_service(self.session)

    # ------------------------------------------------------------------ setup
    def _setup_window(self):
        self.root.title("Brew & Bite Café")
        self.root.resizable(False, False)
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(
            f"{self._W}x{self._H}+{(sw - self._W) // 2}+{(sh - self._H) // 2}"
        )
        self.root.configure(bg=ESPRESSO)
        self.root.bind("<Return>", lambda _: self._do_login())

    # ------------------------------------------------------------------ left panel
    def _build_left(self):
        panel = tk.Frame(self.root, bg=ESPRESSO, width=self._LEFT_W)
        panel.pack(side="left", fill="y")
        panel.pack_propagate(False)

        tk.Frame(panel, bg=ESPRESSO, height=52).pack()

        # Coffee icon in a circle-like ring
        icon_frame = tk.Frame(panel, bg=DARK_BROWN, width=90, height=90)
        icon_frame.pack()
        icon_frame.pack_propagate(False)
        tk.Label(icon_frame, text="☕", font=("Helvetica", 44),
                 bg=DARK_BROWN, fg=CARD_BG).place(relx=0.5, rely=0.5, anchor="center")

        tk.Frame(panel, bg=ESPRESSO, height=18).pack()

        tk.Label(panel, text="Brew & Bite",
                 font=("Helvetica", 26, "bold"),
                 bg=ESPRESSO, fg=CARD_BG).pack()
        tk.Label(panel, text="C  A  F  É",
                 font=("Helvetica", 10, "bold"),
                 bg=ESPRESSO, fg=LIGHT_BROWN).pack(pady=(2, 0))

        tk.Frame(panel, bg=DARK_BROWN, height=1).pack(fill="x", padx=36, pady=22)

        tk.Label(panel,
                 text='"Your café,\nperfectly managed."',
                 font=("Helvetica", 13, "italic"),
                 bg=ESPRESSO, fg=LIGHT_BROWN,
                 justify="center").pack()

        tk.Frame(panel, bg=ESPRESSO, height=26).pack()

        for feat in (
            "✓   Sales & POS tracking",
            "✓   Expense management",
            "✓   Inventory control",
            "✓   Financial analytics",
        ):
            tk.Label(panel, text=feat, font=("Helvetica", 9),
                     bg=ESPRESSO, fg="#A07860", anchor="w").pack(
                         fill="x", padx=38, pady=3)

        tk.Label(panel, text="v 1.0.0",
                 font=("Helvetica", 8),
                 bg=ESPRESSO, fg=DARK_BROWN).pack(side="bottom", pady=14)

    # ------------------------------------------------------------------ right panel
    def _build_right(self):
        right = tk.Frame(self.root, bg=CARD_BG)
        right.pack(side="right", fill="both", expand=True)

        wrap = tk.Frame(right, bg=CARD_BG)
        wrap.place(relx=0.5, rely=0.5, anchor="center", width=320)

        # Heading
        tk.Label(wrap, text="Welcome back  👋",
                 font=("Helvetica", 22, "bold"),
                 bg=CARD_BG, fg=ESPRESSO).pack(anchor="w")
        tk.Label(wrap,
                 text="Sign in to your management dashboard",
                 font=("Helvetica", 10),
                 bg=CARD_BG, fg=TEXT_MID).pack(anchor="w", pady=(3, 0))
        tk.Frame(wrap, bg=BORDER, height=1).pack(fill="x", pady=(16, 0))

        # Username
        self._lbl(wrap, "Username")
        self.username_entry = self._entry(wrap)

        # Password with eye toggle
        self._lbl(wrap, "Password")
        pw_outer = tk.Frame(wrap, bg=BORDER, pady=1, padx=1)
        pw_outer.pack(fill="x")
        pw_inner = tk.Frame(pw_outer, bg=CARD_BG)
        pw_inner.pack(fill="x")
        self.password_entry = tk.Entry(
            pw_inner, show="•", font=FONT_BODY,
            bg=CARD_BG, fg=TEXT_DARK, relief="flat", bd=0,
            insertbackground=MEDIUM_BROWN, highlightthickness=0,
        )
        self.password_entry.pack(side="left", fill="x", expand=True,
                                  ipady=9, padx=(10, 0))
        eye = tk.Label(pw_inner, text="👁", font=("Helvetica", 13),
                       bg=CARD_BG, fg=TEXT_MID, cursor="hand2", padx=10)
        eye.pack(side="right")
        eye.bind("<Button-1>", self._toggle_pw)

        # Remember + forgot password row
        row = tk.Frame(wrap, bg=CARD_BG)
        row.pack(fill="x", pady=(10, 0))
        self.remember_var = tk.BooleanVar(value=False)
        tk.Checkbutton(row, text="Remember me",
                       variable=self.remember_var,
                       font=("Helvetica", 9), bg=CARD_BG, fg=TEXT_MID,
                       activebackground=CARD_BG,
                       highlightthickness=0, cursor="hand2").pack(side="left")
        fgt = tk.Label(row, text="Forgot password?",
                       font=("Helvetica", 9, "underline"),
                       bg=CARD_BG, fg=MEDIUM_BROWN, cursor="hand2")
        fgt.pack(side="right")
        fgt.bind("<Button-1>", lambda _: self.show_reset_password())

        # Sign-in button
        tk.Frame(wrap, bg=CARD_BG, height=18).pack()
        btn = tk.Button(wrap, text="Sign In",
                        font=("Helvetica", 12, "bold"),
                        bg=MEDIUM_BROWN, fg=CARD_BG,
                        activebackground=DARK_BROWN, activeforeground=CARD_BG,
                        relief="flat", bd=0, cursor="hand2",
                        command=self._do_login)
        btn.pack(fill="x", ipady=11)
        btn.bind("<Enter>", lambda _: btn.configure(bg=DARK_BROWN))
        btn.bind("<Leave>", lambda _: btn.configure(bg=MEDIUM_BROWN))

        self.username_entry.focus()

    # ------------------------------------------------------------------ helpers
    @staticmethod
    def _lbl(parent, text):
        tk.Label(parent, text=text,
                 font=("Helvetica", 10, "bold"),
                 bg=CARD_BG, fg=TEXT_MID).pack(anchor="w", pady=(14, 3))

    @staticmethod
    def _entry(parent, show=""):
        outer = tk.Frame(parent, bg=BORDER, pady=1, padx=1)
        outer.pack(fill="x")
        inner = tk.Frame(outer, bg=CARD_BG)
        inner.pack(fill="x")
        e = tk.Entry(inner, show=show, font=FONT_BODY,
                     bg=CARD_BG, fg=TEXT_DARK, relief="flat", bd=0,
                     insertbackground=MEDIUM_BROWN, highlightthickness=0)
        e.pack(fill="x", ipady=9, padx=10)
        return e

    def _toggle_pw(self, _=None):
        self._pw_visible = not self._pw_visible
        self.password_entry.configure(show="" if self._pw_visible else "•")

    # ------------------------------------------------------------------ logic
    def _do_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        if not username or not password:
            messagebox.showerror("Error",
                                 "Please enter both username and password")
            return
        try:
            ok, user_data, err = self.auth_service.login(username, password)
            if ok and user_data:
                logger.info(f"User logged in: {username}")
                self.root.withdraw()
                MainWindow(user_data).run()
            else:
                messagebox.showerror("Login Failed",
                                     err or "Invalid credentials")
                self.password_entry.delete(0, "end")
                self.password_entry.focus()
        except Exception as exc:
            logger.error(f"Login error: {exc}")
            messagebox.showerror("Error", "An error occurred during login")

    def login(self):
        self._do_login()

    def show_reset_password(self):
        win = tk.Toplevel(self.root)
        win.title("Reset Password")
        win.geometry("380x230")
        win.resizable(False, False)
        win.configure(bg=CARD_BG)
        win.transient(self.root)
        win.grab_set()
        win.geometry(
            f"+{self.root.winfo_x() + 240}+{self.root.winfo_y() + 165}"
        )

        tk.Label(win, text="Reset Password",
                 font=("Helvetica", 16, "bold"),
                 bg=CARD_BG, fg=ESPRESSO).pack(pady=(24, 4))
        tk.Label(win, text="Enter your email to receive reset instructions.",
                 font=("Helvetica", 9), bg=CARD_BG, fg=TEXT_MID).pack()

        tk.Label(win, text="Email Address",
                 font=("Helvetica", 10, "bold"),
                 bg=CARD_BG, fg=TEXT_MID).pack(anchor="w", padx=32, pady=(16, 3))
        outer = tk.Frame(win, bg=BORDER, pady=1, padx=1)
        outer.pack(fill="x", padx=32)
        inner = tk.Frame(outer, bg=CARD_BG)
        inner.pack(fill="x")
        email_entry = tk.Entry(inner, font=FONT_BODY,
                               bg=CARD_BG, fg=TEXT_DARK,
                               relief="flat", bd=0, highlightthickness=0)
        email_entry.pack(fill="x", ipady=9, padx=10)

        def _send():
            email = email_entry.get().strip()
            if not email:
                messagebox.showerror("Error", "Please enter your email.",
                                     parent=win)
                return
            try:
                if self.auth_service.initiate_password_reset(email):
                    messagebox.showinfo(
                        "Sent", "Reset instructions sent to your email.",
                        parent=win)
                    win.destroy()
                else:
                    messagebox.showerror("Not Found",
                                         "Email address not found.",
                                         parent=win)
            except Exception as exc:
                logger.error(f"Reset error: {exc}")
                messagebox.showerror("Error", "Request failed.", parent=win)

        send_btn = tk.Button(
            win, text="Send Reset Link",
            font=("Helvetica", 11, "bold"),
            bg=MEDIUM_BROWN, fg=CARD_BG,
            activebackground=DARK_BROWN, activeforeground=CARD_BG,
            relief="flat", bd=0, cursor="hand2", command=_send)
        send_btn.pack(fill="x", padx=32, ipady=10, pady=(16, 0))
        email_entry.focus()
        win.bind("<Return>", lambda _: _send())

    def run(self):
        self.root.mainloop()
