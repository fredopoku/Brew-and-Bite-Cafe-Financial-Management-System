import tkinter as tk
from tkinter import messagebox
import logging
import sys
from pathlib import Path
from datetime import datetime

# Add src directory to Python path
src_path = str(Path(__file__).parent.parent)
if src_path not in sys.path:
    sys.path.append(src_path)

from src.gui.login_window import LoginWindow
from src.database.database import initialize_database
from src.utils.logger import setup_logger
from src.config import LOG_CONFIG, APP_NAME, DATABASE
from src.utils.security import generate_secret_key

class BrewAndBiteApp:
    def __init__(self):
        self.setup_application()

    def setup_application(self):
        """Initialize application components"""
        try:
            # Setup logging
            setup_logger()
            self.logger = logging.getLogger(__name__)
            self.logger.info("Starting Brew and Bite Café Application")

            # Ensure required directories exist
            self.create_required_directories()

            # Initialize database
            self.initialize_db()

            # Generate secret key if not exists
            generate_secret_key()

            # Start GUI
            self.start_gui()

        except Exception as e:
            self.handle_startup_error(e)

    def create_required_directories(self):
        """Create necessary directories if they don't exist"""
        try:
            # Create directories from config
            Path(DATABASE['dir']).mkdir(parents=True, exist_ok=True)
            Path(DATABASE['backup_dir']).mkdir(parents=True, exist_ok=True)
            Path(LOG_CONFIG['dir']).mkdir(parents=True, exist_ok=True)

            self.logger.info("Required directories created successfully")

        except Exception as e:
            self.logger.error(f"Failed to create directories: {str(e)}")
            raise

    def initialize_db(self):
        """Initialize the database"""
        try:
            initialize_database()
            self.logger.info("Database initialized successfully")

        except Exception as e:
            self.logger.error(f"Database initialization failed: {str(e)}")
            raise

    def start_gui(self):
        """Initialize and start the GUI"""
        try:
            root = tk.Tk()
            root.withdraw()  # Hide the root window

            # Set application title
            root.title(APP_NAME)

            # Center the login window
            login_window = LoginWindow(root)

            # Start the application main loop
            root.mainloop()

        except Exception as e:
            self.logger.error(f"GUI initialization failed: {str(e)}")
            raise

    def handle_startup_error(self, error: Exception):
        """Handle application startup errors"""
        error_message = f"Application failed to start: {str(error)}"
        self.logger.critical(error_message)

        try:
            messagebox.showerror(
                "Startup Error",
                "The application encountered an error during startup.\n"
                "Please check the log files for more information."
            )
        except:
            # If GUI is not available, print to console
            print(error_message)

        sys.exit(1)

def main():
    """Application entry point"""
    try:
        app = BrewAndBiteApp()
    except Exception as e:
        print(f"Critical error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()