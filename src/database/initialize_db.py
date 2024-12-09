import sqlite3
import os
from pathlib import Path


def create_database():
    # Get the project root directory
    root_dir = Path(__file__).parent.parent.parent
    data_dir = root_dir / 'data'

    # Create data directory if it doesn't exist
    data_dir.mkdir(exist_ok=True)

    # Database file path
    db_path = data_dir / 'brew_and_bite.db'

    # Read the SQL schema file
    schema_path = root_dir / 'src' / 'database' / 'schema.sql'
    with open(schema_path, 'r') as f:
        schema_sql = f.read()

    # Connect to database and create tables
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Enable foreign keys
        cursor.execute("PRAGMA foreign_keys = ON;")

        # Execute the schema SQL
        cursor.executescript(schema_sql)

        conn.commit()
        print("Database initialized successfully!")

    except sqlite3.Error as e:
        print(f"Error initializing database: {e}")

    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    create_database()