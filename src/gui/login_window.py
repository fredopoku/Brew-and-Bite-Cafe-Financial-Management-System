import tkinter as tk
from tkinter import ttk, messagebox
import logging
from src.database.database import get_session
from src.bll import create_auth_service
from src.gui.main_window import MainWindow

logger = logging.getLogger(__name__)


class LoginWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        self.create_variables()
        self.create_widgets()
        self.session = get_session()
        self.auth_service = create_auth_service(self.session)

    def setup_window(self):
        """Configure the main window"""
        self.root.title("Brew and Bite Café - Login")
        self.root.geometry("400x500")

        # Center window
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - 400) // 2
        y = (screen_height - 500) // 2
        self.root.geometry(f"400x500+{x}+{y}")

        # Configure grid weights
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        # Create main frame
        self.main_frame = ttk.Frame(self.root, padding="20")
        self.main_frame.grid(row=0, column=0, sticky="nsew")

        # Configure frame grid
        for i in range(6):
            self.main_frame.grid_columnconfigure(i, weight=1)

    def create_variables(self):
        """Create tkinter variables"""
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.remember_var = tk.BooleanVar(value=False)

    def create_widgets(self):
        """Create and place widgets"""
        # Logo/Title
        title_frame = ttk.Frame(self.main_frame)
        title_frame.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        title_label = ttk.Label(
            title_frame,
            text="Brew and Bite Café",
            font=("Helvetica", 20, "bold")
        )
        title_label.pack()

        subtitle_label = ttk.Label(
            title_frame,
            text="Management System",
            font=("Helvetica", 12)
        )
        subtitle_label.pack()

        # Username Field
        username_frame = ttk.Frame(self.main_frame)
        username_frame.grid(row=1, column=0, columnspan=2, pady=(0, 10), sticky="ew")

        ttk.Label(username_frame, text="Username:").pack(anchor="w")
        self.username_entry = ttk.Entry(
            username_frame,
            textvariable=self.username_var
        )
        self.username_entry.pack(fill="x", pady=(5, 0))

        # Password Field
        password_frame = ttk.Frame(self.main_frame)
        password_frame.grid(row=2, column=0, columnspan=2, pady=(0, 20), sticky="ew")

        ttk.Label(password_frame, text="Password:").pack(anchor="w")
        self.password_entry = ttk.Entry(
            password_frame,
            textvariable=self.password_var,
            show="*"
        )
        self.password_entry.pack(fill="x", pady=(5, 0))

        # Remember Me Checkbox
        remember_frame = ttk.Frame(self.main_frame)
        remember_frame.grid(row=3, column=0, columnspan=2, pady=(0, 20))

        ttk.Checkbutton(
            remember_frame,
            text="Remember Me",
            variable=self.remember_var
        ).pack()

        # Buttons
        button_frame = ttk.Frame(self.main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=(0, 20))

        ttk.Button(
            button_frame,
            text="Login",
            command=self.login,
            style="Accent.TButton"
        ).pack(side="left", padx=5)

        ttk.Button(
            button_frame,
            text="Reset Password",
            command=self.show_reset_password
        ).pack(side="left", padx=5)

        # Version Info
        version_label = ttk.Label(
            self.main_frame,
            text="Version 1.0.0",
            font=("Helvetica", 8)
        )
        version_label.grid(row=5, column=0, columnspan=2, pady=(20, 0))

        # Bind enter key to login
        self.root.bind("<Return>", lambda e: self.login())

        # Focus username field
        self.username_entry.focus()

    def login(self):
        """Handle login attempt"""
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()

        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return

        try:
            success, user_data, error = self.auth_service.login(username, password)

            if success and user_data:
                logger.info(f"User logged in successfully: {username}")
                self.root.withdraw()  # Hide login window
                MainWindow(user_data, self.auth_service)  # Open main window
            else:
                messagebox.showerror("Login Failed", error or "Invalid login attempt")
                self.password_var.set("")  # Clear password field

        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            messagebox.showerror("Error", "An error occurred during login")

    def show_reset_password(self):
        """Show password reset dialog"""
        reset_window = tk.Toplevel(self.root)
        reset_window.title("Reset Password")
        reset_window.geometry("300x150")
        reset_window.transient(self.root)  # Make window modal

        # Center window
        reset_window.geometry(
            f"+{self.root.winfo_x() + 50}+{self.root.winfo_y() + 50}"
        )

        ttk.Label(
            reset_window,
            text="Enter your email address:"
        ).pack(pady=(20, 5))

        email_var = tk.StringVar()
        email_entry = ttk.Entry(reset_window, textvariable=email_var)
        email_entry.pack(padx=20, fill="x")

        def request_reset():
            email = email_var.get().strip()
            if not email:
                messagebox.showerror("Error", "Please enter your email address")
                return

            try:
                if self.auth_service.initiate_password_reset(email):
                    messagebox.showinfo(
                        "Success",
                        "Password reset instructions have been sent to your email"
                    )
                    reset_window.destroy()
                else:
                    messagebox.showerror(
                        "Error",
                        "Email address not found"
                    )
            except Exception as e:
                logger.error(f"Password reset error: {str(e)}")
                messagebox.showerror(
                    "Error",
                    "An error occurred while processing your request"
                )

        ttk.Button(
            reset_window,
            text="Submit",
            command=request_reset
        ).pack(pady=20)

        email_entry.focus()
        reset_window.bind("<Return>", lambda e: request_reset())

    def run(self):
        """Start the application"""
        self.root.mainloop()