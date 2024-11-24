Brew and Bite Café Financial Management System

A database-driven application for managing expenses, inventory, and sales—designed for small businesses.

This repository contains the implementation of a robust expense tracking and inventory management system created for *Brew and Bite Café*. The application leverages a multi-tier architecture to provide a secure, efficient, and user-friendly solution tailored for small business owners to optimize financial decision-making.

---

Features

Database Design
- SQLite Database: A fully normalized database schema adhering to 3rd Normal Form (3NF).
- Entities:
  - Users: Manage user accounts with attributes such as username, password, and email.
  - Expenses: Record and categorize expenses by date, amount, category, and description.
  - Inventory: Manage items with attributes such as item name, quantity, and cost.
  - Sales: Track transactions, including date, revenue amount, and items sold.
  - Additional entities and relationships defined for data integrity.

Application Architecture
- Data Access Layer (DAL):
  - Built with SQLAlchemy for seamless interaction with the SQLite database.
  - Parameterized queries to prevent SQL injection.
- Business Logic Layer (BLL):
  - Core functionalities include:
    - User management (registration, updates, deletion).
    - Expense recording, history tracking, and categorization.
    - Inventory item management (add, update, delete, view).
    - Sales tracking and revenue management.
    - Financial reporting for expenses, inventory, and sales performance.
  - Data validation and integrity checks implemented.
- Presentation Layer (PL):
  - User Interface Options:
    - Command-line interface (CLI) for simplicity.
    - Graphical user interface (GUI) using Tkinter for enhanced usability.

Security
- User authentication and authorization for controlled access to financial data.
- Sensitive data (e.g., passwords) encrypted for security.
- Compliance with data privacy standards through anonymization and encryption.

Optimization
- Optimized queries for faster report generation and transaction searches.
- Indexing applied to frequently queried fields to enhance performance.

Reporting
- Generate detailed financial insights, including:
  - Expense summaries.
  - Inventory status reports.
  - Sales performance analytics.

---

Tools and Libraries

- Python 3.11: Core programming language.
- SQLite: Lightweight and efficient database.
- SQLAlchemy: ORM for data access and manipulation.
- Tkinter: GUI development.
- pytest/unittest: Automated testing for reliability.
- datetime: Date and time handling.
- os: File path management.
- PyCharm: Integrated development environment.
- Draw.io: For database schema and system diagrams.
- Microsoft Word: Documentation and reporting.

---

How to Use

1. Clone the repository:
   ```bash
   git clone https://github.com/fredopoku/Brew-and-Bite-Cafe-Financial-Management-System.git
   cd brew-and-bite-management
   ```
2. Set up the database using the provided schema diagrams and SQL scripts.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Launch the application:
   - CLI: Run the main Python script for command-line access.
   - GUI: Execute the Tkinter-based interface.

---

This project exemplifies how small businesses can leverage technology to streamline operations, maintain data integrity, and make informed decisions for sustainable growth.
